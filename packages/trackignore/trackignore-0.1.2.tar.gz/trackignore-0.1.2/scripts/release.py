#!/usr/bin/env python3

"""
Release preparation helper.

Runs safety checks before tagging/publishing a new version.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:  # Python 3.11+
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = REPO_ROOT / "pyproject.toml"


def run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    result = subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        check=False,
        text=True,
        capture_output=capture_output,
    )
    if check and result.returncode != 0:
        raise SystemExit(f"Command failed ({' '.join(cmd)}) with exit code {result.returncode}.")
    return result


def ensure_clean_worktree() -> None:
    status = run(["git", "status", "--porcelain"], check=False, capture_output=True)
    stdout = status.stdout or ""
    if stdout.strip():
        raise SystemExit("Working tree is dirty. Commit or stash changes before releasing.")


def read_version() -> str:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    try:
        return data["project"]["version"]
    except KeyError as exc:  # pragma: no cover
        raise SystemExit("Unable to find [project].version in pyproject.toml") from exc


def run_tests() -> None:
    print("→ Running pytest")
    run([sys.executable, "-m", "pytest", "tests"])


def build_package() -> None:
    print("→ Building distribution (hatch build)")
    dist_dir = REPO_ROOT / "dist"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    run(["hatch", "build"])


def pipx_smoke_test(version: str) -> None:
    pipx = shutil.which("pipx")
    if not pipx:
        print("→ pipx not found; skipping pipx smoke test.")
        return

    env_name = f"trackignore-release-{version}"
    print(f"→ Installing with pipx ({env_name})")
    run(
        [
            pipx,
            "install",
            "--force",
            f"--suffix=-release-{version}",
            REPO_ROOT.as_posix(),
        ]
    )
    binary = f"trackignore-release-{version}"
    print(f"→ Verifying CLI via pipx run ({binary})")
    run([pipx, "run", binary, "--help"])
    print(f"→ Uninstalling pipx environment ({env_name})")
    run([pipx, "uninstall", binary])


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a trackignore release.")
    parser.add_argument("--version", required=True, help="Expected version (matches pyproject.toml).")
    parser.add_argument("--skip-pipx", action="store_true", help="Skip pipx install verification.")
    args = parser.parse_args()

    ensure_clean_worktree()

    current_version = read_version()
    if current_version != args.version:
        raise SystemExit(
            f"Version mismatch: pyproject.toml has '{current_version}' but --version={args.version}."
        )

    run_tests()
    build_package()
    if not args.skip_pipx:
        pipx_smoke_test(args.version)

    print("All release checks passed.")


if __name__ == "__main__":
    main()
