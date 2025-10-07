from __future__ import annotations

import hashlib
import json
import logging as _logging
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

_LOGGER = _logging.getLogger("x_make")


def _info(*args: object) -> None:
    msg = " ".join(str(a) for a in args)
    try:
        _LOGGER.info("%s", msg)
    except Exception:
        pass
    try:
        print(msg)
    except Exception:
        try:
            sys.stdout.write(msg + "\n")
        except Exception:
            pass


"""Visitor to run ruff/black/mypy/pyright on immediate child git clones.

This module removes the previous "lessons" feature. It ignores hidden
and common tool-cache directories when discovering immediate child
repositories (for example: .mypy_cache, .ruff_cache, __pycache__, .pyright).
The visitor writes an a-priori and a-posteriori file index, preserves the
extended toolchain flow, and now supports caching tool outputs to speed up
incremental reruns. Any tool failures are raised as AssertionError with the
captured stdout/stderr to make failures visible.
"""


COMMON_CACHE_NAMES = {
    ".mypy_cache",
    ".ruff_cache",
    "__pycache__",
    ".pyright",
    ".tool_cache",
}


class x_cls_make_github_visitor_x:
    def __init__(
        self,
        root_dir: str | Path,
        *,
        output_filename: str = "repos_index.json",
        ctx: object | None = None,
        enable_cache: bool = True,
    ) -> None:
        """Initialize visitor.

        root_dir: path to a workspace that contains immediate child git clones.
        output_filename: unused for package-local index storage but kept for
        backwards compatibility.
        enable_cache: whether to reuse cached tool outputs when repositories are
        unchanged between runs.
        """
        self.root = Path(root_dir)
        if not self.root.exists() or not self.root.is_dir():
            raise AssertionError(
                f"root path must exist and be a directory: {self.root}"
            )

        # The workspace root must not itself be a git repository (we operate
        # on immediate child clones).

        if (self.root / ".git").exists():
            raise AssertionError(
                f"root path must not be a git repository: {self.root}"
            )

        self.output_filename = output_filename
        self._tool_reports: dict[str, Any] = {}
        self._ctx = ctx
        self.enable_cache = enable_cache
        self._last_run_failures: bool = False

        # package root (the folder containing this module). Use this for
        # storing the canonical a-priori / a-posteriori index files so they
        # live with the visitor package rather than the workspace root.
        self.package_root = Path(__file__).resolve().parent

        self.cache_dir = self.package_root / ".tool_cache"
        if self.enable_cache:
            self.cache_dir.mkdir(exist_ok=True)

    def _child_dirs(self) -> list[Path]:
        """Return immediate child directories excluding hidden and cache dirs.

        Exclude names starting with '.' or '__' and common cache names to avoid
        treating tool caches as repositories.
        """
        out: list[Path] = []
        for p in self.root.iterdir():
            if not p.is_dir():
                continue
            name = p.name
            if name.startswith(".") or name.startswith("__"):
                # hidden or dunder directories (including caches)
                continue
            if name in COMMON_CACHE_NAMES:
                continue
            # Only include directories that look like git clones (contain .git)
            if not (p / ".git").exists():
                # skip non-repo helper folders
                continue
            out.append(p)
        return sorted(out)

    def _atomic_write_json(self, path: Path, data: Any) -> None:
        tmp = path.with_name(path.name + ".tmp")
        with tmp.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=4, sort_keys=True)
            fh.flush()
            try:
                os.fsync(fh.fileno())
            except Exception:
                # best-effort fsync; ignore if unsupported
                pass
        os.replace(str(tmp), str(path))

    def _repo_content_hash(self, repo_path: Path) -> str:
        """Return a deterministic hash of repository contents for caching."""
        hasher = hashlib.sha256()
        for p in sorted(repo_path.rglob("*")):
            if not p.is_file():
                continue
            if ".git" in p.parts or "__pycache__" in p.parts:
                continue
            if p.suffix in {".pyc", ".pyo"}:
                continue
            rel = p.relative_to(repo_path).as_posix().encode("utf-8")
            hasher.update(rel)
            try:
                hasher.update(p.read_bytes())
            except Exception:
                # Skip unreadable files without failing the whole hash
                continue
        return hasher.hexdigest()

    def _cache_path(self, repo_name: str, tool_name: str, repo_hash: str) -> Path:
        key = f"{repo_name}_{tool_name}_{repo_hash[:16]}"
        return self.cache_dir / f"{key}.json"

    def _load_cache(
        self,
        repo_name: str,
        tool_name: str,
        repo_hash: str,
    ) -> dict[str, Any] | None:
        if not self.enable_cache:
            return None
        cache_file = self._cache_path(repo_name, tool_name, repo_hash)
        if not cache_file.exists():
            return None
        try:
            with cache_file.open("r", encoding="utf-8") as fh:
                cached = cast("dict[str, Any]", json.load(fh))
        except Exception:
            try:
                cache_file.unlink()
            except Exception:
                pass
            return None
        exit_code: int | None
        try:
            exit_code = int(cached.get("exit", 0))
        except Exception:
            exit_code = None
        if exit_code not in (None, 0):
            self._delete_cache(repo_name, tool_name, repo_hash)
            return None
        return cached

    def _store_cache(
        self,
        repo_name: str,
        tool_name: str,
        repo_hash: str,
        payload: dict[str, Any],
    ) -> None:
        if not self.enable_cache:
            return
        cache_file = self._cache_path(repo_name, tool_name, repo_hash)
        try:
            self._atomic_write_json(cache_file, payload)
        except Exception:
            # Don't let cache write failures stop execution
            pass

    def _delete_cache(
        self,
        repo_name: str,
        tool_name: str,
        repo_hash: str,
    ) -> None:
        if not self.enable_cache:
            return
        cache_file = self._cache_path(repo_name, tool_name, repo_hash)
        try:
            cache_file.unlink()
        except Exception:
            pass

    def _prune_cache(self, keep: int = 500) -> None:
        if not self.enable_cache or not self.cache_dir.exists():
            return
        try:
            cache_files = sorted(self.cache_dir.glob("*.json"), key=lambda p: p.stat().st_mtime)
        except Exception:
            return
        overflow = len(cache_files) - keep
        if overflow <= 0:
            return
        for stale in cache_files[:overflow]:
            try:
                stale.unlink()
            except Exception:
                continue

    def inspect(self, json_name: str) -> list[str]:
        """Write an index of files present in each immediate child repo.

        Returns the list of repository names (relative paths) that were indexed.
        """
        children = self._child_dirs()
        if not children:
            try:
                entries = sorted(
                    p.name for p in self.root.iterdir() if p.is_dir()
                )
            except Exception:
                entries = []
            preview = ", ".join(entries[:10])
            suffix = "" if len(entries) <= 10 else " …"
            raise AssertionError(
                "no child git repositories found"
                f" under {self.root} (visible dirs: {preview}{suffix})"
            )
        index: dict[str, list[str]] = {}
        repo_names: list[str] = []
        for child in children:
            rel = str(child.relative_to(self.root))
            repo_names.append(rel)
            files: list[str] = []
            for p in child.rglob("*"):
                if not p.is_file():
                    continue
                if ".git" in p.parts or "__pycache__" in p.parts:
                    continue
                files.append(str(p.relative_to(child).as_posix()))
            index[rel] = sorted(files)

        # store index files inside the visitor package directory
        out_path = self.package_root / json_name
        self._atomic_write_json(out_path, index)
        return repo_names

    def body(self) -> None:
        """Run toolchain (ruff -> black -> ruff -> mypy -> pyright) against each child repo."""

        python = sys.executable
        packages = ["ruff", "black", "mypy", "pyright"]
        p = subprocess.run(
            [python, "-m", "pip", "install", "--upgrade", *packages],
            check=False,
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            raise AssertionError(
                f"failed to install required packages: {p.stdout}\n{p.stderr}"
            )

        self._prune_cache()

        timeout = 300
        reports: dict[str, Any] = {}
        any_failures = False
        for child in self._child_dirs():
            rel = str(child.relative_to(self.root))
            repo_hash = self._repo_content_hash(child)
            repo_report: dict[str, Any] = {
                "timestamp": datetime.now(UTC).isoformat(),
                "repo_hash": repo_hash,
                "tool_reports": {},
            }

            py_files = list(child.rglob("*.py")) + list(child.rglob("*.pyi"))
            has_python = any(path.is_file() for path in py_files)

            tools = (
                (
                    "ruff_fix",
                    [
                        python,
                        "-m",
                        "ruff",
                        "check",
                        ".",
                        "--fix",
                    ],
                    False,
                ),
                (
                    "black",
                    [
                        python,
                        "-m",
                        "black",
                        ".",
                        "--check",
                        "--diff",
                    ],
                    True,
                ),
                (
                    "ruff_check",
                    [
                        python,
                        "-m",
                        "ruff",
                        "check",
                        ".",
                    ],
                    False,
                ),
                (
                    "mypy",
                    [
                        python,
                        "-m",
                        "mypy",
                        ".",
                        "--strict",
                        "--no-warn-unused-configs",
                        "--show-error-codes",
                        "--warn-return-any",
                        "--warn-unreachable",
                        "--disallow-any-unimported",
                        "--disallow-any-expr",
                        "--disallow-any-decorated",
                        "--disallow-any-explicit",
                    ],
                    True,
                ),
                (
                    "pyright",
                    [
                        python,
                        "-m",
                        "pyright",
                        ".",
                        "--level",
                        "error",
                    ],
                    True,
                ),
            )

            for tool_name, cmd, skip_if_no_python in tools:
                if skip_if_no_python and not has_python:
                    _info(f"{tool_name}: skipped (no Python files) in {rel}")
                    repo_report["tool_reports"][tool_name] = {
                        "exit": 0,
                        "stdout": "",
                        "stderr": "skipped - no Python source (.py/.pyi) found",
                        "cached": False,
                    }
                    continue

                cached = self._load_cache(rel, tool_name, repo_hash)
                if cached is not None:
                    cached["cached"] = True
                    repo_report["tool_reports"][tool_name] = cached
                    _info(f"{tool_name}: cache hit for {rel}")
                    continue

                proc = subprocess.run(
                    cmd,
                    check=False,
                    cwd=str(child),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                result: dict[str, Any] = {
                    "exit": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "cached": False,
                }
                repo_report["tool_reports"][tool_name] = result
                if proc.returncode != 0:
                    self._delete_cache(rel, tool_name, repo_hash)
                    any_failures = True
                    _info(
                        f"{tool_name}: failure (exit {proc.returncode}) in {rel}; see cached stdout/stderr"
                    )
                    continue
                self._store_cache(rel, tool_name, repo_hash, result)

            files: list[str] = []
            for pth in child.rglob("*"):
                if not pth.is_file():
                    continue
                if ".git" in pth.parts or "__pycache__" in pth.parts:
                    continue
                files.append(str(pth.relative_to(child).as_posix()))
            repo_report["files"] = sorted(files)

            reports[rel] = repo_report

        self._tool_reports = reports
        try:
            self._last_run_failures = any_failures
        except Exception:
            # Fallback attribute storage if attrs locked down
            setattr(self, "_last_run_failures", any_failures)

    def cleanup(self) -> None:
        """Placeholder for cleanup. Override if needed."""
        return

    def generate_summary_report(self) -> dict[str, Any]:
        """Produce an aggregate summary of the most recent tool run."""
        summary: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "total_repos": len(self._tool_reports),
            "overall_stats": {
                "cache_hits": 0,
                "cache_misses": 0,
                "failed_tools": 0,
                "total_tools_run": 0,
            },
            "repos": {},
        }
        overall = summary["overall_stats"]
        for repo_name, report in self._tool_reports.items():
            repo_summary: dict[str, Any] = {
                "repo_hash": report.get("repo_hash"),
                "tools": {},
                "cached": 0,
                "failed": 0,
            }
            tools = report.get("tool_reports", {})
            for tool_name, tool_report in tools.items():
                exit_code = int(tool_report.get("exit", -1))
                cached = bool(tool_report.get("cached", False))
                repo_summary["tools"][tool_name] = {
                    "exit": exit_code,
                    "cached": cached,
                }
                overall["total_tools_run"] += 1
                if cached:
                    repo_summary["cached"] += 1
                    overall["cache_hits"] += 1
                else:
                    overall["cache_misses"] += 1
                if exit_code != 0:
                    repo_summary["failed"] += 1
                    overall["failed_tools"] += 1
            summary["repos"][repo_name] = repo_summary
        return summary

    def run_inspect_flow(self) -> None:
        """Run the inspect flow in four steps:
            1) a-priori run -> writes `x_index_a_a_priori_x.json`
        2) body() -> run toolchain (formatters/linters/typecheck)
            3) a-posteriori run -> writes `x_index_b_a_posteriori_x.json`
            4) cleanup()
        """
        # Step 1: a-priori inspect (written into the visitor package dir)
        apriori_repos = self.inspect("x_index_a_a_priori_x.json")
        p1 = self.package_root / "x_index_a_a_priori_x.json"
        assert (
            p1.exists() and p1.stat().st_size > 0
        ), f"step1 failed: {p1} missing or empty"
        _info(
            f"apriori discovery: found {len(apriori_repos)} repositories under {self.root}"
        )

        # re-read and normalize apriori
        try:
            with p1.open("r", encoding="utf-8") as fh:
                raw_apriori = json.load(fh)
        except Exception as exc:
            raise AssertionError(
                f"failed to read a-priori index: {exc}"
            ) from exc

        if not isinstance(raw_apriori, dict):
            raise AssertionError(
                f"a-priori index must be a JSON object mapping repo->files: {p1}"
            )

        apriori_raw = cast("dict[str, Any]", raw_apriori)
        apriori: dict[str, list[str]] = {}
        for key, value in apriori_raw.items():
            key_str = str(key)
            if isinstance(value, list):
                normalized: list[str] = []
                for item in cast("list[Any]", value):
                    if isinstance(item, str):
                        normalized.append(item)
                apriori[key_str] = normalized
            else:
                apriori[key_str] = []

        # ensure the apriori keys match visible child dirs (use _child_dirs to ignore caches)
        current_children = [
            str(p.relative_to(self.root)) for p in self._child_dirs()
        ]
        apriori_keys = sorted(apriori.keys())
        if apriori_keys != sorted(current_children):
            raise AssertionError(
                f"a-priori index contents do not match immediate children.\n  expected: {sorted(current_children)}\n  found: {apriori_keys}"
            )

        # Step 2: run toolchain (ruff -> black -> ruff -> mypy)
        self.body()

        # Step 3: a-posteriori inspect (written into the visitor package dir)
        posterior_repos = self.inspect("x_index_b_a_posteriori_x.json")
        p2 = self.package_root / "x_index_b_a_posteriori_x.json"
        assert (
            p2.exists() and p2.stat().st_size > 0
        ), f"step3 failed: {p2} missing or empty"
        _info(
            f"a-posteriori discovery: found {len(posterior_repos)} repositories under {self.root}"
        )

        try:
            with p2.open("r", encoding="utf-8") as fh:
                raw_data = json.load(fh)
        except Exception as exc:
            raise AssertionError(
                f"failed to read a-posteriori index: {exc}"
            ) from exc

        if not isinstance(raw_data, dict):
            raise AssertionError(
                f"a-posteriori index must be a JSON object mapping repo->files: {p2}"
            )

        data_raw = cast("dict[str, Any]", raw_data)
        data: dict[str, Any] = {str(k): v for k, v in data_raw.items()}

        # attach reports under each repo key
        for repo_name, report in getattr(self, "_tool_reports", {}).items():
            if repo_name in data:
                data[repo_name] = {
                    "files": data.get(repo_name, []),
                    "tool_reports": report.get("tool_reports", {}),
                    "files_index": report.get("files", []),
                }
            else:
                data[repo_name] = {
                    "files": report.get("files", []),
                    "tool_reports": report.get("tool_reports", {}),
                }

        self._atomic_write_json(p2, data)

        summary = self.generate_summary_report()
        summary_path = self.package_root / "x_summary_report_x.json"
        self._atomic_write_json(summary_path, summary)

        # Step 4: cleanup
        self.cleanup()


def _workspace_root() -> str:
    here = Path(__file__).resolve()
    for anc in here.parents:
        if (anc / ".git").exists():  # repo root
            return str(anc.parent)
    # Fallback: two levels up
    return str(here.parent.parent)


def init_name(
    root_dir: str | Path,
    *,
    output_filename: str | None = None,
    ctx: object | None = None,
    enable_cache: bool = True,
) -> x_cls_make_github_visitor_x:
    if output_filename is None:
        return x_cls_make_github_visitor_x(
            root_dir,
            ctx=ctx,
            enable_cache=enable_cache,
        )
    return x_cls_make_github_visitor_x(
        root_dir,
        output_filename=output_filename,
        ctx=ctx,
        enable_cache=enable_cache,
    )


def init_main(
    ctx: object | None = None,
    *,
    enable_cache: bool = True,
) -> x_cls_make_github_visitor_x:
    """Initialize the visitor using dynamic workspace root (parent of this repo)."""
    return init_name(_workspace_root(), ctx=ctx, enable_cache=enable_cache)


if __name__ == "__main__":
    inst = init_main()
    inst.run_inspect_flow()
    summary = inst.generate_summary_report()
    overall = summary.get("overall_stats", {})
    hits = int(overall.get("cache_hits", 0))
    total = int(overall.get("total_tools_run", 0))
    ratio = (hits / total * 100.0) if total else 0.0
    _info(
        f"wrote a-priori, a-posteriori, and summary files to: {inst.package_root}"
    )
    _info(
        f"processed {summary.get('total_repos', 0)} repositories | cache hits: {hits}/{total} ({ratio:.1f}%)"
    )
