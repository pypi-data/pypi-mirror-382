"""CLI entrypoints for trackignore tooling."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, cast

from trackignore.config import generate_default_trackignore, load_trackignore
from trackignore.templates import export_to


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trackignore")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check_parser = subparsers.add_parser("config-check", help="Validate .trackignore configuration")
    check_parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root containing .trackignore (default: current directory)",
    )
    check_parser.add_argument(
        "--json",
        action="store_true",
        help="Output config details as JSON",
    )

    push_parser = subparsers.add_parser("push", help="Publish sanitized history to a public remote")
    push_parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository containing the trackignore configuration (default: current directory)",
    )
    push_parser.add_argument(
        "--remote",
        help="Name of the Git remote to push (e.g., origin).",
    )
    push_parser.add_argument(
        "--remote-url",
        help="Explicit URL for the public remote (overrides --remote).",
    )
    push_parser.add_argument(
        "--branches",
        nargs="+",
        help="Branches to push. Defaults to ['main'] when omitted.",
    )
    push_parser.add_argument(
        "--yes",
        action="store_true",
        help="Do not prompt for confirmation when changes are detected.",
    )
    push_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the operations that would be performed without cloning or pushing.",
    )
    push_parser.add_argument(
        "--force",
        action="store_true",
        help="Use --force instead of --force-with-lease when pushing.",
    )
    push_parser.add_argument(
        "--skip-state",
        action="store_true",
        help="Do not read or write .trackignore.state (always treat config as changed).",
    )

    sync_parser = subparsers.add_parser(
        "sync",
        help="Sync a protected directory to a private remote using git subtree.",
    )
    sync_parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository containing the trackignore configuration (default: current directory)",
    )
    sync_parser.add_argument(
        "--remote",
        help="Name of the Git remote to push (default: PRIVATE_REMOTE env or origin-private).",
    )
    sync_parser.add_argument(
        "--branch",
        help="Remote branch to update (default: PRIVATE_BRANCH env or main).",
    )
    sync_parser.add_argument(
        "--path",
        help="Directory pattern (must exist in .trackignore). Trailing '/' optional.",
    )
    sync_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the operations that would be performed without modifying the remote.",
    )
    sync_parser.add_argument(
        "--force",
        action="store_true",
        help="Pass --force to git subtree push (use cautiously).",
    )

    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Rewrite history to remove protected paths before publishing.",
    )
    cleanup_parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository containing the trackignore configuration (default: current directory)",
    )
    cleanup_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show the operations that would be performed without modifying history.",
    )
    cleanup_parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt before running git filter-repo.",
    )

    init_parser = subparsers.add_parser(
        "init",
        help="Set up trackignore configuration and hooks in the current repo.",
    )
    init_parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root to configure (default: current directory).",
    )
    init_parser.add_argument(
        "--public-remote",
        help="Name of the public remote to protect (default: origin).",
    )
    init_parser.add_argument(
        "--private-remote",
        help="Name of the private remote (default: origin-private).",
    )
    init_parser.add_argument(
        "--private-branch",
        help="Branch name for private sync operations (default: main).",
    )
    init_parser.add_argument(
        "--autorun",
        action="store_true",
        help="Enable automatic trackignore push without prompting.",
    )
    init_parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Skip interactive prompts (conflicts are skipped unless --force provided).",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files without prompting.",
    )

    return parser


def config_check(repo_root: str, *, json_output: bool = False) -> int:
    config = load_trackignore(Path(repo_root))

    if json_output:
        print(json.dumps(config.to_dict(), indent=2))
    else:
        print(f"Patterns ({len(config.patterns)}):")
        for pattern in config.patterns:
            print(f"  - {pattern}")

        if config.warnings:
            print("\nWarnings:")
            for warning in config.warnings:
                location = ""
                if warning.path:
                    location = f"{warning.path}"
                    if warning.line_no:
                        location += f":{warning.line_no}"
                    location += " "
                suggestion = f" -> {warning.suggestion}" if warning.suggestion else ""
                print(f"  - [{warning.code}] {location}{warning.message}{suggestion}")
        else:
            print("\nNo warnings detected.")

    # Non-zero exit if any error-level warnings present.
    for warning in config.warnings:
        if warning.severity.value == "error":
            return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "config-check":
        return config_check(args.repo_root, json_output=args.json)
    if args.command == "push":
        return push_command(
            repo_root=args.repo_root,
            remote=args.remote,
            remote_url=args.remote_url,
            branches=args.branches,
            assume_yes=args.yes,
            dry_run=args.dry_run,
            force=args.force,
            skip_state=args.skip_state,
        )
    if args.command == "sync":
        return sync_command(
            repo_root=args.repo_root,
            remote=args.remote,
            branch=args.branch,
            path=args.path,
            dry_run=args.dry_run,
            force=args.force,
        )
    if args.command == "cleanup":
        return cleanup_command(
            repo_root=args.repo_root,
            dry_run=args.dry_run,
            assume_yes=args.yes,
        )
    if args.command == "init":
        return init_command(
            repo_root=args.repo_root,
            public_remote=args.public_remote,
            private_remote=args.private_remote,
            private_branch=args.private_branch,
            autorun=args.autorun,
            non_interactive=args.non_interactive,
            force=args.force,
        )
    parser.print_help()
    return 2


# ---------------------------------------------------------------------------
# Push implementation


def push_command(
    *,
    repo_root: str,
    remote: str | None,
    remote_url: str | None,
    branches: Iterable[str] | None,
    assume_yes: bool,
    dry_run: bool,
    force: bool,
    skip_state: bool,
) -> int:
    repo_path = Path(repo_root).resolve()
    _ensure_git_repo(repo_path)
    _ensure_dependency_available("git")
    if not dry_run:
        _ensure_dependency_available("git-filter-repo")

    config = load_trackignore(repo_path)

    if _has_error_warnings(config):
        _print_error_warnings(config)
        return 1

    positive_patterns = [p for p in config.patterns if not p.startswith("!")]
    if not positive_patterns:
        print("No positive patterns defined in .trackignore; nothing to strip.")
        return 0

    remote_info = _resolve_remote(repo_path, remote=remote, remote_url=remote_url)
    branch_list = list(branches) if branches else ["main"]

    history_hits = detect_history_hits(repo_path, positive_patterns)
    if history_hits:
        _print_history_hits(history_hits)
        print(
            "Protected paths already exist in history. "
            "Run 'trackignore cleanup --repo-root .' before publishing."
        )
        return 2

    state_path = repo_path / ".trackignore.state"
    delta_summary = None
    previous_hash = None
    previous_state: dict[str, object] = {}
    if not skip_state and state_path.exists():
        try:
            previous_state = json.loads(state_path.read_text(encoding="utf-8"))
            previous_hash = previous_state.get("hash")
        except json.JSONDecodeError:
            previous_state = {}
            previous_hash = None

    print(f"trackignore push → remote: {remote_info.display}")
    print(f"  branches: {', '.join(branch_list)}")
    print(f"  patterns: {', '.join(positive_patterns)}")

    if previous_hash != config.hash:
        delta_summary = _summarize_pattern_changes(previous_state, config)
        if delta_summary:
            _print_pattern_delta(delta_summary)
            if not assume_yes and not _confirm(f"Continue pushing to {remote_info.display}?"):
                print("Aborted by user.")
                return 2

    if dry_run:
        _print_dry_run(remote_info, branch_list, positive_patterns)
        return 0

    temp_dir = tempfile.TemporaryDirectory(prefix="trackignore-push-")
    export_path = Path(temp_dir.name) / "export"
    try:
        print("Cloning repository to temporary workspace...")
        _clone_repository(repo_path, export_path)
        print("Running git filter-repo to strip protected paths...")
        _run_filter_repo(export_path, positive_patterns)
        print("Verifying filtered history...")
        _verify_stripped_paths(export_path, positive_patterns)
        print("Pushing sanitized branches...")
        _push_branches(
            export_path,
            remote_info=remote_info,
            branches=branch_list,
            force=force,
        )
    finally:
        temp_dir.cleanup()

    if not skip_state:
        state_payload = {
            "hash": config.hash,
            "updated_at": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "version": "0.1",
            "patterns": config.patterns,
        }
        state_path.write_text(json.dumps(state_payload, indent=2) + "\n", encoding="utf-8")

    print("trackignore push complete.")
    return 0


# Helper functions ----------------------------------------------------------


def _ensure_git_repo(path: Path) -> None:
    if not (path / ".git").exists():
        raise SystemExit(f"{path} is not a Git repository (missing .git directory).")


def _ensure_dependency_available(name: str) -> None:
    if shutil.which(name):
        return
    raise SystemExit(f"Required dependency '{name}' not found on PATH.")


def _has_error_warnings(config) -> bool:
    return any(w.severity.value == "error" for w in config.warnings)


def _print_error_warnings(config) -> None:
    print("Errors detected in .trackignore configuration:", file=sys.stderr)
    for warning in config.warnings:
        if warning.severity.value != "error":
            continue
        location = ""
        if warning.path:
            location = str(warning.path)
            if warning.line_no:
                location += f":{warning.line_no}"
            location += " "
        print(f"- [{warning.code}] {location}{warning.message}", file=sys.stderr)


class RemoteInfo:
    def __init__(self, name: str, url: str, display: str) -> None:
        self.name = name
        self.url = url
        self.display = display


def _resolve_remote(repo: Path, *, remote: str | None, remote_url: str | None) -> RemoteInfo:
    if remote_url:
        display = remote_url
        name = remote or "trackignore-remote"
        return RemoteInfo(name=name, url=remote_url, display=display)

    remote_name = remote or "origin"
    result = _run(
        ["git", "remote", "get-url", remote_name],
        cwd=repo,
        capture_output=True,
        check=True,
    )
    url = result.stdout.strip()
    if not url:
        raise SystemExit(f"Remote '{remote_name}' has no URL configured.")
    return RemoteInfo(name=remote_name, url=url, display=f"{remote_name} ({url})")


def _summarize_pattern_changes(
    previous_state: dict[str, object], config
) -> dict[str, list[str]] | None:
    previous_patterns = previous_state.get("patterns")
    if not isinstance(previous_patterns, list):
        previous_patterns = []

    old = set(previous_patterns)
    new = set(config.patterns)
    added = sorted(new - old)
    removed = sorted(old - new)
    if not added and not removed:
        return None
    return {"added": added, "removed": removed}


def _print_pattern_delta(delta: dict[str, list[str]]) -> None:
    print("Detected changes in .trackignore:")
    for label in ("added", "removed"):
        entries = delta.get(label, [])
        if not entries:
            continue
        for entry in entries:
            prefix = "+" if label == "added" else "-"
            print(f"  {prefix} {entry}")


def _confirm(message: str) -> bool:
    response = input(f"{message} [y/N]: ").strip().lower()
    return response in {"y", "yes"}


def _print_dry_run(remote_info: RemoteInfo, branches: list[str], patterns: list[str]) -> None:
    print("trackignore push (dry-run)")
    print(f"  remote: {remote_info.display}")
    print(f"  branches: {', '.join(branches)}")
    print("  patterns:")
    for pattern in patterns:
        print(f"    - {pattern}")
    print("No changes were made (dry-run mode).")


def _clone_repository(src_repo: Path, dest_repo: Path) -> None:
    _run(
        ["git", "clone", "--no-local", "--quiet", str(src_repo), str(dest_repo)],
        check=True,
    )


def _run_filter_repo(repo: Path, patterns: list[str]) -> None:
    cmd = ["git", "filter-repo", "--invert-paths", "--force"]
    for pattern in patterns:
        glob = _pattern_to_glob(pattern)
        cmd.extend(["--path-glob", glob])
    _run(cmd, cwd=repo, check=True)


def _pattern_to_glob(pattern: str) -> str:
    if pattern.endswith("/"):
        return pattern + "**"
    return pattern


def _verify_stripped_paths(repo: Path, patterns: list[str]) -> None:
    cmd = ["git", "log", "--name-only", "--pretty=format:", "--all"]
    result = _run(cmd, cwd=repo, capture_output=True, check=True)
    names = set(line.strip() for line in result.stdout.splitlines() if line.strip())
    for pattern in patterns:
        candidate = pattern.rstrip("/")
        if candidate and any(name.startswith(candidate) for name in names):
            raise SystemExit(
                f"Pattern '{pattern}' still present after filter-repo. Aborting push."
            )


def _push_branches(
    repo: Path,
    *,
    remote_info: RemoteInfo,
    branches: list[str],
    force: bool,
) -> None:
    temp_remote_name = "trackignore-temp"
    _run(["git", "remote", "add", temp_remote_name, remote_info.url], cwd=repo, check=True)
    _run(["git", "fetch", temp_remote_name, "--prune"], cwd=repo, check=True)

    for branch in branches:
        ref = f"refs/heads/{branch}"
        show_ref = _run(["git", "show-ref", "--quiet", "--heads", ref], cwd=repo)
        if show_ref.returncode != 0:
            print(f"Skip: branch '{branch}' not found in export.")
            continue

        push_cmd = ["git", "push", temp_remote_name, f"{branch}:{branch}"]
        push_cmd.append("--force" if force else "--force-with-lease")
        _run(push_cmd, cwd=repo, check=True)

    _run(["git", "remote", "remove", temp_remote_name], cwd=repo, check=False)


def _run(
    cmd: list[str],
    *,
    cwd: Path | None = None,
    capture_output: bool = False,
    check: bool = False,
):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        capture_output=capture_output,
    )
    if check and result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else ""
        raise SystemExit(f"Command failed ({' '.join(cmd)}): {stderr}")
    return result


# ---------------------------------------------------------------------------
# Sync implementation


def sync_command(
    *,
    repo_root: str,
    remote: str | None,
    branch: str | None,
    path: str | None,
    dry_run: bool,
    force: bool,
) -> int:
    repo_path = Path(repo_root).resolve()
    _ensure_git_repo(repo_path)
    _ensure_dependency_available("git")

    config = load_trackignore(repo_path)
    if _has_error_warnings(config):
        _print_error_warnings(config)
        return 1

    positive_patterns = [p for p in config.patterns if not p.startswith("!")]
    directories, unsupported_patterns, file_patterns = _classify_sync_targets(positive_patterns)

    if file_patterns:
        joined = ", ".join(file_patterns)
        print(f"Note: file patterns are ignored for sync: {joined}")
    if unsupported_patterns:
        joined = ", ".join(unsupported_patterns)
        print(
            "Note: patterns with wildcards are not supported for sync "
            f"and will be skipped: {joined}"
        )

    if not directories:
        print(
            "No syncable directory patterns found in .trackignore. "
            "Add a directory entry ending with '/' before running sync."
        )
        return 2

    explicit_path = path or os.environ.get("TRACKIGNORE_SYNC_PATH") or os.environ.get("PRIVATE_DIR")
    selected = None
    available = {entry.rstrip("/"): entry for entry in directories}

    if explicit_path:
        normalized = explicit_path.strip().strip("/")
        if normalized not in available:
            print(
                "Selected path not found in .trackignore. "
                f"Choose one of: {', '.join(sorted(available))}"
            )
            return 2
        selected = normalized
    elif len(available) == 1:
        selected = next(iter(available))
    else:
        options = ", ".join(sorted(available))
        print(
            "Multiple directory patterns detected in .trackignore. "
            f"Specify which one to sync using --path. Available: {options}"
        )
        return 2

    target_dir = repo_path / selected
    if not target_dir.exists() or not target_dir.is_dir():
        print(f"Directory '{selected}' does not exist in the repository; nothing to sync.")
        return 2

    remote_name = remote or os.environ.get("PRIVATE_REMOTE") or "origin-private"
    branch_name = branch or os.environ.get("PRIVATE_BRANCH") or "main"

    remote_url = ""
    try:
        result = _run(
            ["git", "remote", "get-url", remote_name],
            cwd=repo_path,
            capture_output=True,
            check=True,
        )
        remote_url = result.stdout.strip()
    except SystemExit:
        print(f"Remote '{remote_name}' not found. Configure it before syncing.")
        return 2

    print(f"trackignore sync → remote: {remote_name} ({remote_url})")
    print(f"  branch: {branch_name}")
    print(f"  path: {selected}/")

    if dry_run:
        print("Dry-run: git subtree push would be executed with the above parameters.")
        return 0

    cmd = ["git", "subtree", "push", f"--prefix={selected}", remote_name, branch_name]
    if force:
        cmd.append("--force")
    _run(cmd, cwd=repo_path, check=True)

    print("trackignore sync complete.")
    return 0


def _classify_sync_targets(patterns: list[str]) -> tuple[list[str], list[str], list[str]]:
    directories: list[str] = []
    wildcard_patterns: list[str] = []
    file_patterns: list[str] = []

    for pattern in patterns:
        if pattern.endswith("/"):
            trimmed = pattern.rstrip("/")
            if _contains_wildcards(trimmed):
                wildcard_patterns.append(pattern)
                continue
            directories.append(pattern)
        else:
            file_patterns.append(pattern)
    return directories, wildcard_patterns, file_patterns


def _contains_wildcards(value: str) -> bool:
    return any(ch in value for ch in {"*", "?", "["})


# ---------------------------------------------------------------------------
# Cleanup implementation


def cleanup_command(
    *,
    repo_root: str,
    dry_run: bool,
    assume_yes: bool,
) -> int:
    repo_path = Path(repo_root).resolve()
    _ensure_git_repo(repo_path)
    _ensure_dependency_available("git")
    if not dry_run:
        _ensure_dependency_available("git-filter-repo")

    config = load_trackignore(repo_path)
    if _has_error_warnings(config):
        _print_error_warnings(config)
        return 1

    positive_patterns = [p for p in config.patterns if not p.startswith("!")]
    if not positive_patterns:
        print("No positive patterns defined in .trackignore; nothing to clean.")
        return 0

    hits = detect_history_hits(repo_path, positive_patterns)
    if not hits:
        print("No tracked history detected for protected patterns. Nothing to clean.")
        return 0

    _print_history_hits(hits)
    print(
        "\nCleanup will rewrite history in-place using git filter-repo. "
        "Ensure you have a backup before continuing."
    )
    if dry_run:
        _print_cleanup_plan(positive_patterns)
        return 0

    if not assume_yes and not _confirm("Proceed with rewriting repository history?"):
        print("Cleanup aborted by user.")
        return 2

    _run_filter_repo(repo_path, positive_patterns)

    print("\nCleanup complete. Recommended next steps:")
    print("  1. Inspect git log and verify sensitive paths are removed.")
    print("  2. Force-push updated branches to the appropriate remotes (e.g., git push --force --all).")
    print("  3. Inform collaborators to re-clone or reset their repositories.")
    return 0


def init_command(
    *,
    repo_root: str,
    public_remote: str | None,
    private_remote: str | None,
    private_branch: str | None,
    autorun: bool,
    non_interactive: bool,
    force: bool,
) -> int:
    repo_path = Path(repo_root).resolve()
    _ensure_git_repo(repo_path)

    defaults = {
        "public_remote": (public_remote or "origin").strip() or "origin",
        "private_remote": (private_remote or "origin-private").strip() or "origin-private",
        "private_branch": (private_branch or "main").strip() or "main",
        "autorun": bool(autorun),
    }

    results: list[str] = []

    trackignore_file = repo_path / ".trackignore"
    if not trackignore_file.exists():
        trackignore_file.write_text(generate_default_trackignore(), encoding="utf-8")
        results.append("Created .trackignore with default template.")
    else:
        results.append(".trackignore already exists; left unchanged.")

    config_dir = repo_path / ".trackignore.d"
    config_dir.mkdir(exist_ok=True)
    config_path = config_dir / "config.sh"

    if config_path.exists() and not force:
        results.append(".trackignore.d/config.sh already exists; skipping (use --force to overwrite).")
    else:
        config_lines = [
            "# Generated by trackignore init",
            f'TRACKIGNORE_PUBLIC_REMOTES="{defaults["public_remote"]}"',
            f'TRACKIGNORE_PRIVATE_REMOTES="{defaults["private_remote"]}"',
            f'TRACKIGNORE_PRIVATE_BRANCH="{defaults["private_branch"]}"',
        ]
        if defaults["autorun"]:
            config_lines.append('TRACKIGNORE_AUTORUN="1"')
        config_lines.append("")
        config_path.write_text("\n".join(config_lines), encoding="utf-8")
        results.append("Wrote .trackignore.d/config.sh with project preferences.")

    _ensure_gitignore_state_entry(repo_path, results, force=force)

    hooks_dir = repo_path / ".git" / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    hook_path = hooks_dir / "pre-push"

    install_hook = True
    if hook_path.exists() and not force:
        if non_interactive:
            results.append("Existing pre-push hook found; skipping (use --force to replace).")
            install_hook = False
        else:
            if not _confirm("pre-push hook already exists. Replace with trackignore hook?"):
                results.append("Existing pre-push hook retained.")
                install_hook = False
    if install_hook:
        export_to(hook_path, "pre-push", mode=0o755)
        results.append("Installed trackignore pre-push hook.")

    _update_global_config(
        repo_path,
        {
            "public_remote": defaults["public_remote"],
            "private_remote": defaults["private_remote"],
            "private_branch": defaults["private_branch"],
            "autorun": defaults["autorun"],
        },
    )

    print("trackignore init complete.\n")
    for message in results:
        print(f"- {message}")

    return 0


# ---------------------------------------------------------------------------
# History detection utilities


@dataclass(slots=True)
class HistoryHit:
    pattern: str
    commit: str
    sample_path: str | None


def detect_history_hits(repo: Path, patterns: Iterable[str]) -> list[HistoryHit]:
    hits: list[HistoryHit] = []
    for pattern in patterns:
        pathspec = _pattern_to_pathspec(pattern)
        if not pathspec:
            continue
        result = _run(
            ["git", "log", "-n", "1", "--pretty=format:%H", "--name-only", "--", pathspec],
            cwd=repo,
            capture_output=True,
        )
        if result.returncode != 0:
            continue

        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        if not lines:
            continue

        commit = lines[0]
        sample_path = lines[1] if len(lines) > 1 else None
        hits.append(HistoryHit(pattern=pattern, commit=commit, sample_path=sample_path))

    # Deduplicate by pattern (git log may repeat). Keep earliest found.
    unique: dict[str, HistoryHit] = {}
    for hit in hits:
        if hit.pattern not in unique:
            unique[hit.pattern] = hit
    return list(unique.values())


def _pattern_to_pathspec(pattern: str) -> str | None:
    core = pattern.lstrip("/")
    if not core:
        return None
    if core.endswith("/"):
        core = core.rstrip("/")

    if _contains_wildcards(core):
        return f":(glob){core}"
    return core


def _print_history_hits(hits: list[HistoryHit]) -> None:
    print("Protected content detected in Git history:")
    for hit in hits[:5]:
        sample = f" (e.g., {hit.sample_path})" if hit.sample_path else ""
        print(f"  - {hit.pattern} -> commit {hit.commit}{sample}")
    if len(hits) > 5:
        remaining = len(hits) - 5
        print(f"  ... {remaining} additional pattern(s) omitted.")


def _print_cleanup_plan(patterns: list[str]) -> None:
    print("\nDry-run summary:")
    print("  git filter-repo --invert-paths --force \\")
    for pattern in patterns:
        glob = _pattern_to_glob(pattern)
        print(f"    --path-glob {glob} \\")
    print("  (run inside your repository)")


def _global_config_dir() -> Path:
    custom = os.environ.get("TRACKIGNORE_HOME")
    if custom:
        return Path(custom).expanduser()
    return Path.home() / ".trackignore"


def _update_global_config(repo_path: Path, payload: dict[str, object]) -> None:
    directory = _global_config_dir()
    directory.mkdir(parents=True, exist_ok=True)
    config_path = directory / "config.json"

    data: dict[str, object]
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}

    projects = cast(dict[str, object], data.setdefault("projects", {}))
    projects[str(repo_path)] = payload
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _ensure_gitignore_state_entry(repo_path: Path, results: list[str], *, force: bool) -> None:
    gitignore_path = repo_path / ".gitignore"
    entry = ".trackignore.state"

    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8")
        if entry in {line.strip() for line in content.splitlines()}:
            results.append(".gitignore already includes .trackignore.state.")
            return
        if not content.endswith("\n"):
            content += "\n"
        content += f"# trackignore state file\n{entry}\n"
        gitignore_path.write_text(content, encoding="utf-8")
        results.append("Updated .gitignore to ignore .trackignore.state.")
    else:
        gitignore_path.write_text(f"# trackignore state file\n{entry}\n", encoding="utf-8")
        results.append("Created .gitignore ignoring .trackignore.state.")


if __name__ == "__main__":
    sys.exit(main())
