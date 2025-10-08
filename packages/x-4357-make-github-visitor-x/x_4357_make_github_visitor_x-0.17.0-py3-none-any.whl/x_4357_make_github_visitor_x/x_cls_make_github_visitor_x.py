from __future__ import annotations

import hashlib
import json
import logging as _logging
import os
import platform
import subprocess
import sys
import time
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

TOOL_MODULE_MAP = {
    "ruff_fix": "ruff",
    "ruff_check": "ruff",
    "black": "black",
    "mypy": "mypy",
    "pyright": "pyright",
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
        self._failure_messages: list[str] = []
        self._failure_details: list[dict[str, Any]] = []
        self._tool_versions: dict[str, str] = {}
        self._runtime_snapshot: dict[str, Any] = {}

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

    @staticmethod
    def _ensure_text(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, (bytes, bytearray)):
            try:
                return value.decode("utf-8")  # type: ignore[return-value]
            except Exception:  # pragma: no cover - diagnostic fallback
                return value.decode("utf-8", "replace")  # type: ignore[return-value]
        if value is None:
            return ""
        return str(value)

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

    def _collect_tool_versions(self, python: str) -> dict[str, str]:
        versions: dict[str, str] = {}
        for module in sorted({*TOOL_MODULE_MAP.values()}):
            try:
                proc = subprocess.run(
                    [python, "-m", module, "--version"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
            except Exception as exc:  # pragma: no cover - diagnostics only
                versions[module] = f"<error invoking --version: {exc}>"
                continue
            output = (proc.stdout or proc.stderr).strip()
            if proc.returncode != 0:
                versions[module] = f"<exit {proc.returncode}> {output}"
            else:
                versions[module] = output or "<no output>"
        return versions

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
                if p.suffix.lower() not in {".py", ".pyi"}:
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

        self._tool_versions = self._collect_tool_versions(python)
        self._runtime_snapshot = {
            "python_executable": python,
            "python_version": sys.version.replace("\n", " "),
            "platform": platform.platform(),
            "run_started_at": datetime.now(UTC).isoformat(),
            "workspace_root": str(self.root),
        }
        env_snapshot = {
            key: os.environ.get(key)
            for key in ("PATH", "PYTHONPATH", "VIRTUAL_ENV")
            if os.environ.get(key)
        }
        if env_snapshot:
            self._runtime_snapshot["environment"] = env_snapshot

        self._prune_cache()

        timeout = 300
        reports: dict[str, Any] = {}
        failure_messages: list[str] = []
        failure_details: list[dict[str, Any]] = []
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
                        "--select",
                        "ALL",
                        "--ignore",
                        "D,COM812,ISC001,T20",
                        "--line-length",
                        "88",
                        "--target-version",
                        "py311",
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
                        "--line-length",
                        "88",
                        "--target-version",
                        "py311",
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
                        "--select",
                        "ALL",
                        "--ignore",
                        "D,COM812,ISC001,T20",
                        "--line-length",
                        "88",
                        "--target-version",
                        "py311",
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
                module_name = TOOL_MODULE_MAP.get(tool_name, tool_name)
                tool_version = self._tool_versions.get(module_name, "<unknown>")
                if skip_if_no_python and not has_python:
                    _info(f"{tool_name}: skipped (no Python files) in {rel}")
                    now_iso = datetime.now(UTC).isoformat()
                    repo_report["tool_reports"][tool_name] = {
                        "exit": 0,
                        "stdout": "",
                        "stderr": "skipped - no Python source (.py/.pyi) found",
                        "cached": False,
                        "skipped": True,
                        "skip_reason": "no_python_files",
                        "cmd": cmd,
                        "cmd_display": " ".join(str(part) for part in cmd),
                        "cwd": str(child),
                        "started_at": now_iso,
                        "ended_at": now_iso,
                        "duration_seconds": 0.0,
                        "repo_hash": repo_hash,
                        "tool_version": tool_version,
                        "tool_module": module_name,
                    }
                    continue

                cached = self._load_cache(rel, tool_name, repo_hash)
                if cached is not None:
                    cached = dict(cached)
                    cached["cached"] = True
                    cached.setdefault("cmd", cmd)
                    cached.setdefault("cmd_display", " ".join(str(part) for part in cmd))
                    cached.setdefault("cwd", str(child))
                    cached.setdefault("repo_hash", repo_hash)
                    cached.setdefault("tool_version", tool_version)
                    cached.setdefault("tool_module", module_name)
                    cached.setdefault("started_at", "")
                    cached.setdefault("ended_at", "")
                    cached.setdefault("duration_seconds", 0.0)
                    repo_report["tool_reports"][tool_name] = cached
                    _info(f"{tool_name}: cache hit for {rel}")
                    continue

                start_wall = datetime.now(UTC)
                start_perf = time.perf_counter()
                try:
                    proc = subprocess.run(
                        cmd,
                        check=False,
                        cwd=str(child),
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                    )
                    timed_out = False
                    proc_stdout = proc.stdout
                    proc_stderr = proc.stderr
                    exit_code: int | None = proc.returncode
                except subprocess.TimeoutExpired as exc:  # pragma: no cover - diagnostic path
                    timed_out = True
                    exit_code = None
                    proc_stdout = (exc.output or "") if isinstance(exc.output, str) else ""
                    proc_stderr = (exc.stderr or "") if isinstance(exc.stderr, str) else ""
                    proc = None
                end_wall = datetime.now(UTC)
                duration = max(time.perf_counter() - start_perf, 0.0)

                proc_stdout = self._ensure_text(proc_stdout)
                proc_stderr = self._ensure_text(proc_stderr)

                result: dict[str, Any] = {
                    "exit": exit_code,
                    "stdout": proc_stdout,
                    "stderr": proc_stderr,
                    "cached": False,
                    "cmd": cmd,
                    "cmd_display": " ".join(str(part) for part in cmd),
                    "cwd": str(child),
                    "started_at": start_wall.isoformat(),
                    "ended_at": end_wall.isoformat(),
                    "duration_seconds": duration,
                    "repo_hash": repo_hash,
                    "tool_version": tool_version,
                    "tool_module": module_name,
                }
                if timed_out:
                    result["timed_out"] = True
                    result["timeout_seconds"] = timeout
                repo_report["tool_reports"][tool_name] = result
                failure_condition = timed_out or exit_code is None or exit_code != 0
                if failure_condition:
                    self._delete_cache(rel, tool_name, repo_hash)
                    truncated_stdout = proc_stdout.strip().splitlines()
                    truncated_stderr = proc_stderr.strip().splitlines()
                    preview_stdout = "\n".join(truncated_stdout[:5])
                    if len(truncated_stdout) > 5:
                        preview_stdout += "\n…"
                    preview_stderr = "\n".join(truncated_stderr[:5])
                    if len(truncated_stderr) > 5:
                        preview_stderr += "\n…"
                    exit_display = "timeout" if timed_out else f"exit {exit_code}"
                    failure_messages.append(
                        f"{tool_name} failed for {rel} ({exit_display})"
                        f"\ncwd: {child}"
                        f"\ncommand: {result['cmd_display']}"
                        f"\nstarted_at: {result['started_at']}"
                        f"\nduration: {duration:.3f}s"
                        f"\ntool_version: {tool_version}"
                        f"\nstdout:\n{preview_stdout or '<empty>'}"
                        f"\nstderr:\n{preview_stderr or '<empty>'}"
                    )
                    failure_entry = {
                        "repo": rel,
                        "repo_path": str(child),
                        "tool": tool_name,
                        "tool_module": module_name,
                    }
                    failure_entry.update(result)
                    failure_details.append(failure_entry)
                    _info(
                        f"{tool_name}: failure ({exit_display}) in {rel}; details captured"
                    )
                    continue
                self._store_cache(rel, tool_name, repo_hash, result)

            files: list[str] = []
            for pth in child.rglob("*"):
                if not pth.is_file():
                    continue
                if ".git" in pth.parts or "__pycache__" in pth.parts:
                    continue
                if pth.suffix.lower() not in {".py", ".pyi"}:
                    continue
                files.append(str(pth.relative_to(child).as_posix()))
            repo_report["files"] = sorted(files)

            reports[rel] = repo_report

        self._tool_reports = reports
        self._last_run_failures = bool(failure_messages)
        self._failure_messages = failure_messages
        self._failure_details = failure_details
        self._runtime_snapshot["run_completed_at"] = datetime.now(UTC).isoformat()

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
                "had_failures": bool(self._last_run_failures),
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
                exit_raw = tool_report.get("exit")
                exit_code: int | None
                if exit_raw is None:
                    exit_code = None
                else:
                    try:
                        exit_code = int(exit_raw)
                    except Exception:
                        exit_code = -1
                cached = bool(tool_report.get("cached", False))
                timed_out_flag = bool(tool_report.get("timed_out", False))
                repo_summary["tools"][tool_name] = {
                    "exit": exit_code,
                    "cached": cached,
                    "timed_out": timed_out_flag,
                }
                overall["total_tools_run"] += 1
                if cached:
                    repo_summary["cached"] += 1
                    overall["cache_hits"] += 1
                else:
                    overall["cache_misses"] += 1
                if timed_out_flag or exit_code not in (0, None):
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

        failure_report_path = self.package_root / "x_tool_failures_x.json"
        failure_payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "root": str(self.root),
            "had_failures": bool(self._last_run_failures),
            "total_failures": len(self._failure_details),
            "failures": self._failure_details,
            "summary_report_path": str(summary_path),
            "apriori_index_path": str(p1),
            "posteriori_index_path": str(p2),
            "tool_versions": self._tool_versions,
            "runtime_snapshot": self._runtime_snapshot,
        }
        if self._failure_messages:
            failure_payload["failure_messages"] = self._failure_messages
        self._atomic_write_json(failure_report_path, failure_payload)

        # Step 4: cleanup
        self.cleanup()

        if self._last_run_failures:
            msgs = self._failure_messages[:]
            if not msgs:
                msgs = ["tool failures occurred but no messages were captured"]
            preview = "\n\n".join(msgs[:5])
            if len(msgs) > 5:
                preview += "\n\n…"
            raise AssertionError(
                f"toolchain failures detected across repositories ({len(msgs)} total).\n{preview}\n\nFull failure log: {failure_report_path}"
            )


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
