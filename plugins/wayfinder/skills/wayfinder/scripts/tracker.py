#!/usr/bin/env python3
"""Minimal local Markdown tracker for Wayfinder."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


CONFIG_PATH = Path("docs/agents/issue-tracker.md")
TRACKER_ROOT_RE = re.compile(r"^Tracker root:\s*`([^`]+)`\s*$", re.MULTILINE)
ISSUE_FILE_RE = re.compile(r"^(\d+)(?:-([a-z0-9][a-z0-9-]*))?\.md$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
INTERACTIONS = {"HITL", "AFK"}
TYPES = {"grilling", "research", "prototype", "task"}
STATUSES = {"open", "claimed", "closed"}
MAP_HEADINGS = (
    "Destination",
    "Notes",
    "Decisions so far",
    "Not yet specified",
    "Out of scope",
)
MAP_TEMPLATE = """# <Map title>

## Destination

## Notes

## Decisions so far

## Not yet specified

## Out of scope
"""
ISSUE_TEMPLATE = """# <Issue title>

Interaction: <HITL|AFK>
Type: <grilling|research|prototype|task>
Status: open
Blocked by:

## Question
"""


class TrackerError(Exception):
    pass


@dataclass
class Issue:
    path: Path
    number: int
    number_text: str
    title: str
    interaction: str
    issue_type: str
    status: str
    blocked_by: list[int]
    question: str
    answer: str | None


@dataclass
class MapData:
    directory: Path
    path: Path
    title: str
    destination: str
    issues: list[Issue]
    updated_at: float


def find_repo_root() -> Path:
    override = os.environ.get("WAYFINDER_REPO_ROOT")
    if override:
        return Path(override).resolve()

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=3,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return Path(result.stdout.strip()).resolve()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists() or (candidate / CONFIG_PATH).is_file():
            return candidate
    raise TrackerError("Could not locate the repository root.")


def load_tracker_root(repo_root: Path, *, ensure: bool = True) -> Path:
    config_path = repo_root / CONFIG_PATH
    if not config_path.is_file():
        raise TrackerError(f"Tracker configuration is missing: {CONFIG_PATH.as_posix()}")

    try:
        content = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise TrackerError(f"Could not read {CONFIG_PATH.as_posix()}: {exc}") from exc

    matches = TRACKER_ROOT_RE.findall(content)
    if len(matches) != 1:
        raise TrackerError(
            f"Expected exactly one `Tracker root: `<path>`` setting in {CONFIG_PATH.as_posix()}."
        )

    configured = Path(matches[0].strip())
    if configured.is_absolute():
        raise TrackerError("Tracker root must be relative to the repository root.")

    resolved = (repo_root / configured).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise TrackerError("Tracker root must stay inside the repository.") from exc

    if ensure:
        try:
            resolved.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise TrackerError(f"Could not create Tracker root {configured.as_posix()}: {exc}") from exc
    return resolved


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TrackerError(f"Could not read {path}: {exc}") from exc


def first_h1(content: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", content, re.MULTILINE)
    return match.group(1).strip() if match else ""


def section(content: str, heading: str) -> str | None:
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    return match.group(1).strip() if match else None


def field(content: str, name: str) -> str | None:
    match = re.search(rf"^{re.escape(name)}:[ \t]*(.*?)[ \t]*$", content, re.MULTILINE)
    return match.group(1).strip() if match else None


def is_placeholder(value: str | None) -> bool:
    if value is None or not value.strip():
        return True
    stripped = value.strip()
    return stripped.startswith("<") and stripped.endswith(">")


def parse_blockers(raw: str | None) -> tuple[list[int], list[str]]:
    if raw is None or not raw.strip():
        return [], []
    tokens = [token.strip() for token in raw.split(",")]
    blockers: list[int] = []
    errors: list[str] = []
    for token in tokens:
        if not token.isdigit():
            errors.append(f"invalid blocker `{token}`")
            continue
        blockers.append(int(token))
    return blockers, errors


def parse_issue(path: Path) -> tuple[Issue | None, list[str]]:
    errors: list[str] = []
    match = ISSUE_FILE_RE.match(path.name)
    if not match:
        return None, ["filename must start with a numeric Issue ID"]

    try:
        content = read_text(path)
    except TrackerError as exc:
        return None, [str(exc)]

    number_text = match.group(1)
    title = first_h1(content)
    interaction = field(content, "Interaction") or ""
    issue_type = field(content, "Type") or ""
    status = field(content, "Status") or ""
    blocked_by, blocker_errors = parse_blockers(field(content, "Blocked by"))
    question = section(content, "Question")
    answer = section(content, "Answer")

    if is_placeholder(title):
        errors.append("missing Issue title")
    if interaction not in INTERACTIONS:
        errors.append(f"Interaction must be one of: {', '.join(sorted(INTERACTIONS))}")
    if issue_type not in TYPES:
        errors.append(f"Type must be one of: {', '.join(sorted(TYPES))}")
    if status not in STATUSES:
        errors.append(f"Status must be one of: {', '.join(sorted(STATUSES))}")
    if is_placeholder(question):
        errors.append("missing Question")
    if status == "closed" and is_placeholder(answer):
        errors.append("closed Issue is missing Answer")
    errors.extend(blocker_errors)
    if len(blocked_by) != len(set(blocked_by)):
        errors.append("Blocked by contains duplicate Issue IDs")

    issue = Issue(
        path=path,
        number=int(number_text),
        number_text=number_text,
        title=title,
        interaction=interaction,
        issue_type=issue_type,
        status=status,
        blocked_by=blocked_by,
        question=question or "",
        answer=answer,
    )
    return issue, errors


def parse_map(map_dir: Path) -> tuple[MapData | None, list[str]]:
    map_path = map_dir / "map.md"
    errors: list[str] = []
    try:
        content = read_text(map_path)
    except TrackerError as exc:
        return None, [str(exc)]

    title = first_h1(content)
    destination = section(content, "Destination")
    if is_placeholder(title):
        errors.append("map.md: missing Map title")
    if is_placeholder(destination):
        errors.append("map.md: missing Destination")
    for heading in MAP_HEADINGS:
        if section(content, heading) is None:
            errors.append(f"map.md: missing `## {heading}`")

    issues: list[Issue] = []
    issues_dir = map_dir / "issues"
    issue_files = sorted(issues_dir.glob("*.md")) if issues_dir.is_dir() else []
    seen_numbers: dict[int, Path] = {}
    for issue_path in issue_files:
        issue, issue_errors = parse_issue(issue_path)
        for message in issue_errors:
            errors.append(f"{issue_path.relative_to(map_dir).as_posix()}: {message}")
        if issue is None:
            continue
        if issue.number in seen_numbers:
            errors.append(
                f"{issue_path.relative_to(map_dir).as_posix()}: duplicate Issue ID "
                f"{issue.number_text} also used by {seen_numbers[issue.number].name}"
            )
        else:
            seen_numbers[issue.number] = issue_path
        issues.append(issue)

    issue_by_number = {issue.number: issue for issue in issues}
    for issue in issues:
        for blocker in issue.blocked_by:
            if blocker == issue.number:
                errors.append(f"issues/{issue.path.name}: Issue cannot block itself")
            elif blocker not in issue_by_number:
                errors.append(f"issues/{issue.path.name}: blocker {blocker:02d} does not exist")

    errors.extend(validate_dag(issues))

    tracked_files = [map_path, *issue_files]
    updated_at = max((path.stat().st_mtime for path in tracked_files), default=map_path.stat().st_mtime)
    return MapData(
        directory=map_dir,
        path=map_path,
        title=title,
        destination=destination or "",
        issues=issues,
        updated_at=updated_at,
    ), errors


def validate_dag(issues: list[Issue]) -> list[str]:
    graph = {issue.number: issue.blocked_by for issue in issues}
    visiting: set[int] = set()
    visited: set[int] = set()
    errors: list[str] = []

    def visit(node: int, trail: list[int]) -> None:
        if node in visiting:
            start = trail.index(node) if node in trail else 0
            cycle = trail[start:] + [node]
            rendered = " -> ".join(f"{number:02d}" for number in cycle)
            message = f"blocking graph contains a cycle: {rendered}"
            if message not in errors:
                errors.append(message)
            return
        if node in visited:
            return
        visiting.add(node)
        for blocker in graph.get(node, []):
            if blocker in graph:
                visit(blocker, trail + [node])
        visiting.remove(node)
        visited.add(node)

    for number in sorted(graph):
        visit(number, [])
    return errors


def load_maps(tracker_root: Path) -> tuple[list[MapData], list[str]]:
    maps: list[MapData] = []
    diagnostics: list[str] = []
    for child in sorted(tracker_root.iterdir()):
        if not child.is_dir() or not (child / "map.md").is_file():
            continue
        map_data, errors = parse_map(child)
        if map_data is not None:
            maps.append(map_data)
        diagnostics.extend(f"{child.name}: {message}" for message in errors)
    maps.sort(key=lambda item: item.updated_at, reverse=True)
    return maps, diagnostics


def repo_relative(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root).as_posix()


def compact_text(value: str) -> str:
    return " ".join(value.split())


def issue_is_unblocked(issue: Issue, issue_by_number: dict[int, Issue]) -> bool:
    return all(
        blocker in issue_by_number and issue_by_number[blocker].status == "closed"
        for blocker in issue.blocked_by
    )


def command_collect(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    maps, diagnostics = load_maps(tracker_root)

    print("# Wayfinder Context")
    print()
    print(f"Tracker root: `{repo_relative(tracker_root, repo_root)}`")
    print(f"Maps found: {len(maps)}")
    if maps:
        print("Order: latest activity first")

    for map_data in maps:
        issue_by_number = {issue.number: issue for issue in map_data.issues}
        frontier = [
            issue
            for issue in map_data.issues
            if issue.status == "open" and issue_is_unblocked(issue, issue_by_number)
        ]
        claimed = [issue for issue in map_data.issues if issue.status == "claimed"]
        blocked = [
            issue
            for issue in map_data.issues
            if issue.status == "open" and not issue_is_unblocked(issue, issue_by_number)
        ]
        active_count = len(frontier) + len(blocked) + len(claimed)
        updated = datetime.fromtimestamp(map_data.updated_at, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        print()
        print(f"## {map_data.title or map_data.directory.name}")
        print()
        print(f"Path: `{repo_relative(map_data.path, repo_root)}`")
        print(f"Updated: `{updated}`")
        print()
        print(f"Destination: {compact_text(map_data.destination) or '(missing)'}")
        print()
        print(
            f"Open issues: {active_count} — {len(frontier)} frontier, "
            f"{len(blocked)} blocked, {len(claimed)} claimed"
        )
        print()
        print("### Frontier")
        print()
        if frontier:
            for issue in sorted(frontier, key=lambda item: item.number):
                print(f"- `{issue.number_text}` {issue.title} — {issue.interaction}")
        else:
            print("None.")
        print()
        print("### Claimed")
        print()
        if claimed:
            for issue in sorted(claimed, key=lambda item: item.number):
                print(f"- `{issue.number_text}` {issue.title} — {issue.interaction}")
        else:
            print("None.")

    if diagnostics:
        print()
        print("## Diagnostics")
        print()
        for diagnostic in diagnostics:
            print(f"- {diagnostic}")
    return 0


def validate_slug(value: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise TrackerError("Slug must contain lowercase letters, digits, and single hyphens only.")
    return value


def command_create_map(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    slug = validate_slug(args.slug)
    map_dir = tracker_root / slug
    if map_dir.exists():
        raise TrackerError(f"Map already exists: {repo_relative(map_dir, repo_root)}")
    map_dir.mkdir(parents=True)
    (map_dir / "issues").mkdir()
    map_path = map_dir / "map.md"
    map_path.write_text(MAP_TEMPLATE, encoding="utf-8")
    print(repo_relative(map_path, repo_root))
    return 0


def resolve_map_dir(tracker_root: Path, map_ref: str) -> Path:
    candidate = (tracker_root / map_ref).resolve()
    try:
        candidate.relative_to(tracker_root)
    except ValueError as exc:
        raise TrackerError("Map reference must stay inside the Tracker root.") from exc
    if not candidate.is_dir() or not (candidate / "map.md").is_file():
        raise TrackerError(f"Map not found: {map_ref}")
    return candidate


def command_create_issue(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    slug = validate_slug(args.slug or "issue")
    issues_dir = map_dir / "issues"
    issues_dir.mkdir(exist_ok=True)
    numbers = []
    for path in issues_dir.glob("*.md"):
        match = ISSUE_FILE_RE.match(path.name)
        if match:
            numbers.append(int(match.group(1)))
    number = max(numbers, default=0) + 1
    issue_path = issues_dir / f"{number:02d}-{slug}.md"
    issue_path.write_text(ISSUE_TEMPLATE, encoding="utf-8")
    print(repo_relative(issue_path, repo_root))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    if args.map:
        map_dirs = [resolve_map_dir(tracker_root, args.map)]
    else:
        map_dirs = [
            child
            for child in sorted(tracker_root.iterdir())
            if child.is_dir() and (child / "map.md").is_file()
        ]

    errors: list[str] = []
    for map_dir in map_dirs:
        _, map_errors = parse_map(map_dir)
        errors.extend(f"{map_dir.name}: {message}" for message in map_errors)

    if errors:
        print(f"Validation found {len(errors)} error(s):")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validation passed for {len(map_dirs)} Map(s).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Wayfinder local Markdown tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect_parser = subparsers.add_parser("collect", help="Print low-resolution context for every Map")
    collect_parser.set_defaults(handler=command_collect)

    map_parser = subparsers.add_parser("create-map", help="Create an empty Map skeleton")
    map_parser.add_argument("slug", help="Map directory slug")
    map_parser.set_defaults(handler=command_create_map)

    issue_parser = subparsers.add_parser("create-issue", help="Create an empty Issue skeleton")
    issue_parser.add_argument("map", help="Map directory name")
    issue_parser.add_argument("slug", nargs="?", help="Issue filename slug (default: issue)")
    issue_parser.set_defaults(handler=command_create_issue)

    validate_parser = subparsers.add_parser("validate", help="Validate Markdown structure, enums, and blocking DAG")
    validate_parser.add_argument("map", nargs="?", help="Validate one Map (default: every Map)")
    validate_parser.set_defaults(handler=command_validate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return args.handler(args)
    except TrackerError as exc:
        print(f"Tracker error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
