#!/usr/bin/env python3
"""Local Markdown implementation of Wayfinder's tracker operations."""

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
TICKET_FILE_RE = re.compile(r"^(\d+)(?:-([a-z0-9][a-z0-9-]*))?\.md$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
STATES = {"open", "closed"}
MAP_HEADINGS = (
    "Destination",
    "Notes",
    "Decisions so far",
    "Not yet specified",
    "Out of scope",
)


class TrackerError(Exception):
    pass


@dataclass
class Ticket:
    path: Path
    number: int
    number_text: str
    title: str
    state: str
    claimed_by: str
    blocked_by: list[int]
    question: str
    answer: str | None


@dataclass
class MapData:
    directory: Path
    path: Path
    title: str
    destination: str
    tickets: list[Ticket]
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


def write_text(path: Path, content: str) -> None:
    """Replace one tracker file without exposing a partially-written document."""
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    except OSError as exc:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise TrackerError(f"Could not write {path}: {exc}") from exc


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


def replace_field(content: str, name: str, value: str) -> str:
    pattern = re.compile(rf"^{re.escape(name)}:[ \t]*.*$", re.MULTILINE)
    if not pattern.search(content):
        raise TrackerError(f"Ticket is missing `{name}:`.")
    return pattern.sub(f"{name}: {value}", content, count=1)


def append_section_item(content: str, heading: str, item: str) -> str:
    pattern = re.compile(
        rf"(^##\s+{re.escape(heading)}\s*$\n)(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        raise TrackerError(f"Map is missing `## {heading}`.")
    existing = match.group(2).strip()
    body = f"\n{existing}\n\n{item}\n\n" if existing else f"\n{item}\n\n"
    return content[: match.start(2)] + body + content[match.end(2) :]


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


def parse_ticket(path: Path) -> tuple[Ticket | None, list[str]]:
    errors: list[str] = []
    match = TICKET_FILE_RE.match(path.name)
    if not match:
        return None, ["filename must start with a numeric Ticket ID"]

    try:
        content = read_text(path)
    except TrackerError as exc:
        return None, [str(exc)]

    number_text = match.group(1)
    title = first_h1(content)
    raw_state = field(content, "State")
    raw_claimed_by = field(content, "Claimed by")
    raw_blocked_by = field(content, "Blocked by")
    state = raw_state or ""
    claimed_by = raw_claimed_by or ""
    blocked_by, blocker_errors = parse_blockers(raw_blocked_by)
    question = section(content, "Question")
    answer = section(content, "Answer")

    if is_placeholder(title):
        errors.append("missing Ticket title")
    if raw_claimed_by is None:
        errors.append("missing `Claimed by:` field")
    if raw_blocked_by is None:
        errors.append("missing `Blocked by:` field")
    if state not in STATES:
        errors.append(f"State must be one of: {', '.join(sorted(STATES))}")
    if is_placeholder(question):
        errors.append("missing Question")
    if state == "closed" and is_placeholder(answer):
        errors.append("closed Ticket is missing Answer")
    errors.extend(blocker_errors)
    if len(blocked_by) != len(set(blocked_by)):
        errors.append("Blocked by contains duplicate Ticket IDs")

    ticket = Ticket(
        path=path,
        number=int(number_text),
        number_text=number_text,
        title=title,
        state=state,
        claimed_by=claimed_by,
        blocked_by=blocked_by,
        question=question or "",
        answer=answer,
    )
    return ticket, errors


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

    tickets: list[Ticket] = []
    issues_dir = map_dir / "issues"
    ticket_files = sorted(issues_dir.glob("*.md")) if issues_dir.is_dir() else []
    seen_numbers: dict[int, Path] = {}
    for ticket_path in ticket_files:
        ticket, ticket_errors = parse_ticket(ticket_path)
        for message in ticket_errors:
            errors.append(f"issues/{ticket_path.name}: {message}")
        if ticket is None:
            continue
        if ticket.number in seen_numbers:
            errors.append(
                f"issues/{ticket_path.name}: duplicate Ticket ID "
                f"{ticket.number_text} also used by {seen_numbers[ticket.number].name}"
            )
        else:
            seen_numbers[ticket.number] = ticket_path
        tickets.append(ticket)

    ticket_by_number = {ticket.number: ticket for ticket in tickets}
    for ticket in tickets:
        for blocker in ticket.blocked_by:
            if blocker == ticket.number:
                errors.append(f"issues/{ticket.path.name}: Ticket cannot block itself")
            elif blocker not in ticket_by_number:
                errors.append(f"issues/{ticket.path.name}: blocker {blocker:02d} does not exist")

    errors.extend(validate_dag(tickets))

    tracked_files = [map_path, *ticket_files]
    updated_at = max((path.stat().st_mtime for path in tracked_files), default=map_path.stat().st_mtime)
    return MapData(
        directory=map_dir,
        path=map_path,
        title=title,
        destination=destination or "",
        tickets=tickets,
        updated_at=updated_at,
    ), errors


def validate_dag(tickets: list[Ticket]) -> list[str]:
    graph = {ticket.number: ticket.blocked_by for ticket in tickets}
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


def ticket_is_unblocked(ticket: Ticket, ticket_by_number: dict[int, Ticket]) -> bool:
    return all(
        blocker in ticket_by_number and ticket_by_number[blocker].state == "closed"
        for blocker in ticket.blocked_by
    )


def require_valid_map(map_dir: Path) -> MapData:
    map_data, errors = parse_map(map_dir)
    if map_data is None:
        raise TrackerError(f"Could not read Map: {map_dir.name}")
    if errors:
        rendered = "\n".join(f"- {message}" for message in errors)
        raise TrackerError(f"Map `{map_dir.name}` is invalid:\n{rendered}")
    return map_data


def resolve_map_dir(tracker_root: Path, map_ref: str) -> Path:
    candidate = (tracker_root / map_ref).resolve()
    try:
        candidate.relative_to(tracker_root)
    except ValueError as exc:
        raise TrackerError("Map reference must stay inside the Tracker root.") from exc
    if not candidate.is_dir() or not (candidate / "map.md").is_file():
        raise TrackerError(f"Map not found: {map_ref}")
    return candidate


def resolve_ticket(map_data: MapData, ticket_ref: str) -> Ticket:
    if ticket_ref.isdigit():
        number = int(ticket_ref)
        matches = [ticket for ticket in map_data.tickets if ticket.number == number]
    else:
        matches = [ticket for ticket in map_data.tickets if ticket.path.name == ticket_ref]
    if len(matches) != 1:
        raise TrackerError(f"Ticket not found: {ticket_ref}")
    return matches[0]


def require_open(ticket: Ticket) -> None:
    if ticket.state != "open":
        raise TrackerError(f"Ticket {ticket.number_text} is already closed.")


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
        ticket_by_number = {ticket.number: ticket for ticket in map_data.tickets}
        frontier = [
            ticket
            for ticket in map_data.tickets
            if ticket.state == "open"
            and not ticket.claimed_by
            and ticket_is_unblocked(ticket, ticket_by_number)
        ]
        claimed = [
            ticket
            for ticket in map_data.tickets
            if ticket.state == "open" and ticket.claimed_by
        ]
        blocked = [
            ticket
            for ticket in map_data.tickets
            if ticket.state == "open"
            and not ticket.claimed_by
            and not ticket_is_unblocked(ticket, ticket_by_number)
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
            f"Open tickets: {active_count} — {len(frontier)} frontier, "
            f"{len(blocked)} blocked, {len(claimed)} claimed"
        )
        print()
        print("### Frontier")
        print()
        if frontier:
            for ticket in sorted(frontier, key=lambda item: item.number):
                print(f"- `{ticket.number_text}` {ticket.title}")
        else:
            print("None.")
        print()
        print("### Claimed")
        print()
        if claimed:
            for ticket in sorted(claimed, key=lambda item: item.number):
                print(
                    f"- `{ticket.number_text}` {ticket.title} — claimed by {ticket.claimed_by}"
                )
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
    content = f"""# {args.title.strip()}

## Destination

{args.destination.strip()}

## Notes

{args.notes.strip()}

## Decisions so far

## Not yet specified

{args.not_yet_specified.strip()}

## Out of scope

{args.out_of_scope.strip()}
"""
    write_text(map_path, content)
    print(repo_relative(map_path, repo_root))
    return 0


def command_create_ticket(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    require_valid_map(map_dir)
    slug = validate_slug(args.slug)
    issues_dir = map_dir / "issues"
    issues_dir.mkdir(exist_ok=True)
    numbers = []
    for path in issues_dir.glob("*.md"):
        match = TICKET_FILE_RE.match(path.name)
        if match:
            numbers.append(int(match.group(1)))
    number = max(numbers, default=0) + 1
    issue_path = issues_dir / f"{number:02d}-{slug}.md"
    content = f"""# {args.title.strip()}

State: open
Claimed by:
Blocked by:

## Question

{args.question.strip()}
"""
    write_text(issue_path, content)
    print(repo_relative(issue_path, repo_root))
    return 0


def command_add_blocker(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    map_data = require_valid_map(map_dir)
    ticket = resolve_ticket(map_data, args.ticket)
    blocker = resolve_ticket(map_data, args.blocker)
    require_open(ticket)
    if blocker.number == ticket.number:
        raise TrackerError("A Ticket cannot block itself.")
    if blocker.number in ticket.blocked_by:
        raise TrackerError(
            f"Ticket {ticket.number_text} is already blocked by {blocker.number_text}."
        )

    ticket.blocked_by.append(blocker.number)
    dag_errors = validate_dag(map_data.tickets)
    if dag_errors:
        raise TrackerError(dag_errors[0])
    content = read_text(ticket.path)
    blockers = ", ".join(f"{number:02d}" for number in ticket.blocked_by)
    write_text(ticket.path, replace_field(content, "Blocked by", blockers))
    print(repo_relative(ticket.path, repo_root))
    return 0


def command_remove_blocker(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    map_data = require_valid_map(map_dir)
    ticket = resolve_ticket(map_data, args.ticket)
    blocker = resolve_ticket(map_data, args.blocker)
    require_open(ticket)
    if blocker.number not in ticket.blocked_by:
        raise TrackerError(
            f"Ticket {ticket.number_text} is not blocked by {blocker.number_text}."
        )
    remaining = [number for number in ticket.blocked_by if number != blocker.number]
    content = read_text(ticket.path)
    blockers = ", ".join(f"{number:02d}" for number in remaining)
    write_text(ticket.path, replace_field(content, "Blocked by", blockers))
    print(repo_relative(ticket.path, repo_root))
    return 0


def default_actor() -> str:
    return (
        os.environ.get("WAYFINDER_ACTOR")
        or os.environ.get("USERNAME")
        or os.environ.get("USER")
        or "local-agent"
    )


def command_claim_ticket(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    map_data = require_valid_map(map_dir)
    ticket = resolve_ticket(map_data, args.ticket)
    require_open(ticket)
    if ticket.claimed_by:
        raise TrackerError(
            f"Ticket {ticket.number_text} is already claimed by {ticket.claimed_by}."
        )
    ticket_by_number = {item.number: item for item in map_data.tickets}
    if not ticket_is_unblocked(ticket, ticket_by_number):
        raise TrackerError(f"Ticket {ticket.number_text} is blocked and cannot be claimed.")
    actor = (args.actor or default_actor()).strip()
    if not actor:
        raise TrackerError("Claim actor must not be empty.")
    content = read_text(ticket.path)
    write_text(ticket.path, replace_field(content, "Claimed by", actor))
    print(repo_relative(ticket.path, repo_root))
    return 0


def command_release_ticket(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    map_data = require_valid_map(map_dir)
    ticket = resolve_ticket(map_data, args.ticket)
    require_open(ticket)
    if not ticket.claimed_by:
        raise TrackerError(f"Ticket {ticket.number_text} is not claimed.")
    if args.actor and args.actor != ticket.claimed_by:
        raise TrackerError(
            f"Ticket {ticket.number_text} is claimed by {ticket.claimed_by}, not {args.actor}."
        )
    content = read_text(ticket.path)
    write_text(ticket.path, replace_field(content, "Claimed by", ""))
    print(repo_relative(ticket.path, repo_root))
    return 0


def close_ticket(
    map_dir: Path,
    ticket: Ticket,
    *,
    answer: str,
    gist: str,
    index_heading: str,
) -> None:
    require_open(ticket)
    if not ticket.claimed_by:
        raise TrackerError(f"Ticket {ticket.number_text} must be claimed before it can be closed.")
    if not answer.strip():
        raise TrackerError("Answer must not be empty.")
    if not gist.strip():
        raise TrackerError("Gist must not be empty.")

    ticket_content = read_text(ticket.path).rstrip()
    ticket_content = replace_field(ticket_content, "State", "closed")
    ticket_content = f"{ticket_content}\n\n## Answer\n\n{answer.strip()}\n"
    relative_link = ticket.path.relative_to(map_dir).as_posix()
    pointer = f"- [{ticket.title}]({relative_link}) — {gist.strip()}"
    map_path = map_dir / "map.md"
    map_content = append_section_item(read_text(map_path), index_heading, pointer)

    # The ticket is written first so a crash cannot expose a decision pointer
    # whose linked ticket still appears open. Validation can surface a missing
    # index update if a later semantic validator chooses to enforce it.
    write_text(ticket.path, ticket_content)
    write_text(map_path, map_content)


def command_resolve_ticket(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    map_data = require_valid_map(map_dir)
    ticket = resolve_ticket(map_data, args.ticket)
    close_ticket(
        map_dir,
        ticket,
        answer=args.answer,
        gist=args.gist,
        index_heading="Decisions so far",
    )
    print(repo_relative(ticket.path, repo_root))
    return 0


def command_exclude_ticket(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    map_data = require_valid_map(map_dir)
    ticket = resolve_ticket(map_data, args.ticket)
    close_ticket(
        map_dir,
        ticket,
        answer=args.reason,
        gist=args.gist,
        index_heading="Out of scope",
    )
    print(repo_relative(ticket.path, repo_root))
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

    collect_parser = subparsers.add_parser(
        "collect", help="Print the low-resolution index of every Map"
    )
    collect_parser.set_defaults(handler=command_collect)

    map_parser = subparsers.add_parser("create-map", help="Create a Map")
    map_parser.add_argument("slug", help="Map directory slug")
    map_parser.add_argument("--title", required=True, help="Map title")
    map_parser.add_argument("--destination", required=True, help="Map destination")
    map_parser.add_argument("--notes", default="", help="Standing notes")
    map_parser.add_argument(
        "--not-yet-specified", default="", help="Initial in-scope fog"
    )
    map_parser.add_argument("--out-of-scope", default="", help="Initial scope exclusions")
    map_parser.set_defaults(handler=command_create_map)

    ticket_parser = subparsers.add_parser("create-ticket", help="Create a child Ticket")
    ticket_parser.add_argument("map", help="Map directory name")
    ticket_parser.add_argument("slug", help="Ticket filename slug")
    ticket_parser.add_argument("--title", required=True, help="Ticket title")
    ticket_parser.add_argument("--question", required=True, help="Question the Ticket resolves")
    ticket_parser.set_defaults(handler=command_create_ticket)

    blocker_parser = subparsers.add_parser("add-blocker", help="Add a blocking edge")
    blocker_parser.add_argument("map")
    blocker_parser.add_argument("ticket")
    blocker_parser.add_argument("blocker")
    blocker_parser.set_defaults(handler=command_add_blocker)

    unblock_parser = subparsers.add_parser("remove-blocker", help="Remove a blocking edge")
    unblock_parser.add_argument("map")
    unblock_parser.add_argument("ticket")
    unblock_parser.add_argument("blocker")
    unblock_parser.set_defaults(handler=command_remove_blocker)

    claim_parser = subparsers.add_parser("claim-ticket", help="Claim a frontier Ticket")
    claim_parser.add_argument("map")
    claim_parser.add_argument("ticket")
    claim_parser.add_argument("--actor", help="Claim owner (default: local environment user)")
    claim_parser.set_defaults(handler=command_claim_ticket)

    release_parser = subparsers.add_parser("release-ticket", help="Release a claimed Ticket")
    release_parser.add_argument("map")
    release_parser.add_argument("ticket")
    release_parser.add_argument("--actor", help="Require this actor to own the claim")
    release_parser.set_defaults(handler=command_release_ticket)

    resolve_parser = subparsers.add_parser("resolve-ticket", help="Resolve a claimed Ticket")
    resolve_parser.add_argument("map")
    resolve_parser.add_argument("ticket")
    resolve_parser.add_argument("--answer", required=True)
    resolve_parser.add_argument("--gist", required=True)
    resolve_parser.set_defaults(handler=command_resolve_ticket)

    exclude_parser = subparsers.add_parser(
        "exclude-ticket", help="Close a claimed Ticket as out of scope"
    )
    exclude_parser.add_argument("map")
    exclude_parser.add_argument("ticket")
    exclude_parser.add_argument("--reason", required=True)
    exclude_parser.add_argument("--gist", required=True)
    exclude_parser.set_defaults(handler=command_exclude_ticket)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate local tracker structure and the blocking DAG"
    )
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
