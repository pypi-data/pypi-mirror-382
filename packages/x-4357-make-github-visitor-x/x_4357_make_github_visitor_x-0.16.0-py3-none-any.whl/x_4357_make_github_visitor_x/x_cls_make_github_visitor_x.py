from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import logging as _logging

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


"""Visitor to run ruff/black/mypy on immediate child git clones.

This module removes the previous "lessons" feature. It ignores hidden
and common tool-cache directories when discovering immediate child
repositories (for example: .mypy_cache, .ruff_cache, __pycache__). The
visitor writes an a-priori and a-posteriori file index and preserves the
ruff/black/mypy flow. Any tool failures are raised as AssertionError with
the captured stdout/stderr to make failures visible.
"""


COMMON_CACHE_NAMES = {".mypy_cache", ".ruff_cache", "__pycache__"}


class x_cls_make_github_visitor_x:
    def __init__(
        self,
        root_dir: str | Path,
        *,
        output_filename: str = "repos_index.json",
        ctx: object | None = None,
    ) -> None:
        """Initialize visitor.

        root_dir: path to a workspace that contains immediate child git clones.
        output_filename: unused for package-local index storage but kept for
        backwards compatibility.
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

        # package root (the folder containing this module). Use this for
        # storing the canonical a-priori / a-posteriori index files so they
        # live with the visitor package rather than the workspace root.
        self.package_root = Path(__file__).resolve().parent

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

    def inspect(self, json_name: str) -> None:
        """Write an index of files present in each immediate child repo.

        The produced JSON maps repo-name -> [file paths].
        """
        children = self._child_dirs()
        if not children:
            raise AssertionError("no child git repositories found")
        index: dict[str, list[str]] = {}
        for child in children:
            rel = str(child.relative_to(self.root))
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

    def body(self) -> None:
        """Run toolchain (ruff -> black -> ruff -> mypy) against each child repo.

        Any non-zero exit from a tool raises an AssertionError that contains
        the tool's stdout/stderr to aid debugging.
        """
        python = sys.executable
        # ensure required formatter/linter/typecheck packages are available; if install fails surface stderr
        p = subprocess.run(
            [
                python,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "ruff",
                "black",
                "mypy",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if p.returncode != 0:
            raise AssertionError(
                f"failed to install required packages: {p.stderr}"
            )

        timeout = 120
        reports: dict[str, Any] = {}
        for child in self._child_dirs():
            rel = str(child.relative_to(self.root))
            repo_report: dict[str, Any] = {
                "timestamp": datetime.now(UTC).isoformat(),
                "tool_reports": {},
            }

            # 1) ruff --fix
            cmd = [python, "-m", "ruff", "check", ".", "--fix"]
            p = subprocess.run(
                cmd,
                check=False,
                cwd=str(child),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            repo_report["tool_reports"]["ruff_fix"] = {
                "exit": p.returncode,
                "stdout": p.stdout,
                "stderr": p.stderr,
            }
            if p.returncode != 0:
                raise AssertionError(
                    f"ruff --fix failed for {rel}: exit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}"
                )

            # 2) black
            cmd = [python, "-m", "black", ".", "--line-length", "79"]
            p = subprocess.run(
                cmd,
                check=False,
                cwd=str(child),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            repo_report["tool_reports"]["black"] = {
                "exit": p.returncode,
                "stdout": p.stdout,
                "stderr": p.stderr,
            }
            if p.returncode != 0:
                raise AssertionError(
                    f"black failed for {rel}: exit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}"
                )

            # 3) ruff check
            cmd = [python, "-m", "ruff", "check", "."]
            p = subprocess.run(
                cmd,
                check=False,
                cwd=str(child),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            repo_report["tool_reports"]["ruff_check"] = {
                "exit": p.returncode,
                "stdout": p.stdout,
                "stderr": p.stderr,
            }
            if p.returncode != 0:
                raise AssertionError(
                    f"ruff check failed for {rel}: exit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}"
                )

            # 4) mypy strict
            # Skip mypy if there are no Python source files in the repo
            py_files = list(child.rglob("*.py")) + list(child.rglob("*.pyi"))
            if not any(p.is_file() for p in py_files):
                repo_report["tool_reports"]["mypy"] = {
                    "exit": 0,
                    "stdout": "",
                    "stderr": "skipped - no Python source (.py/.pyi) found",
                }
            else:
                cmd = [
                    python,
                    "-m",
                    "mypy",
                    "--strict",
                    "--no-warn-unused-configs",
                    "--show-error-codes",
                    ".",
                ]
                p = subprocess.run(
                    cmd,
                    check=False,
                    cwd=str(child),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                repo_report["tool_reports"]["mypy"] = {
                    "exit": p.returncode,
                    "stdout": p.stdout,
                    "stderr": p.stderr,
                }
                if p.returncode != 0:
                    raise AssertionError(
                        f"mypy failed for {rel}: exit={p.returncode}\nstdout={p.stdout}\nstderr={p.stderr}"
                    )

            # capture resulting file index for this repo
            files: list[str] = []
            for pth in child.rglob("*"):
                if not pth.is_file():
                    continue
                if ".git" in pth.parts or "__pycache__" in pth.parts:
                    continue
                files.append(str(pth.relative_to(child).as_posix()))
            repo_report["files"] = sorted(files)

            reports[rel] = repo_report

        # store for merge into a-posteriori index later
        self._tool_reports = reports

    def cleanup(self) -> None:
        """Placeholder for cleanup. Override if needed."""
        return None

    def run_inspect_flow(self) -> None:
        """Run the inspect flow in four steps:
            1) a-priori run -> writes `x_index_a_a_priori_x.json`
        2) body() -> run toolchain (formatters/linters/typecheck)
            3) a-posteriori run -> writes `x_index_b_a_posteriori_x.json`
            4) cleanup()
        """
        # Step 1: a-priori inspect (written into the visitor package dir)
        self.inspect("x_index_a_a_priori_x.json")
        p1 = self.package_root / "x_index_a_a_priori_x.json"
        assert (
            p1.exists() and p1.stat().st_size > 0
        ), f"step1 failed: {p1} missing or empty"

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

        apriori: dict[str, list[str]] = {}
        for k, v in raw_apriori.items():
            key = str(k)
            if isinstance(v, list):
                apriori[key] = [str(x) for x in v if isinstance(x, str)]
            else:
                apriori[key] = []

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
        self.inspect("x_index_b_a_posteriori_x.json")
        p2 = self.package_root / "x_index_b_a_posteriori_x.json"
        assert (
            p2.exists() and p2.stat().st_size > 0
        ), f"step3 failed: {p2} missing or empty"

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

        data: dict[str, Any] = {str(k): v for k, v in raw_data.items()}

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
) -> x_cls_make_github_visitor_x:
    if output_filename is None:
        return x_cls_make_github_visitor_x(root_dir, ctx=ctx)
    return x_cls_make_github_visitor_x(
        root_dir, output_filename=output_filename, ctx=ctx
    )


def init_main(ctx: object | None = None) -> x_cls_make_github_visitor_x:
    """Initialize the visitor using dynamic workspace root (parent of this repo)."""
    return init_name(_workspace_root(), ctx=ctx)


if __name__ == "__main__":
    inst = init_main()
    inst.run_inspect_flow()
    _info(
        f"wrote a-priori and a-posteriori index files to: {inst.package_root}"
    )
