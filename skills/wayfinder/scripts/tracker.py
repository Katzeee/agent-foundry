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


CONFIG_PATH = Path("docs/agents/wayfinder/wayfinder.md")
TICKET_TYPES_PATH = Path("docs/agents/wayfinder/ticket-types.md")
TRACKER_ROOT_RE = re.compile(r"^Tracker root:\s*`([^`]+)`\s*$", re.MULTILINE)
TICKET_FILE_RE = re.compile(r"^(\d+)-([a-z0-9]+(?:-[a-z0-9]+)*)\.md$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
STATES = {"open", "claimed", "closed"}
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
    ticket_type: str
    state: str
    blocked_by: list[int]
    question: str
    answer: str | None


@dataclass(frozen=True)
class IndexEntry:
    section_name: str
    title: str
    target: str
    gist: str


@dataclass
class MapData:
    directory: Path
    path: Path
    title: str
    destination: str
    tickets: list[Ticket]
    index_entries: list[IndexEntry]
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


def lexical_absolute(path: Path) -> Path:
    """Make a path absolute without resolving symlinks or junctions."""
    return Path(os.path.abspath(path))


def stays_within(path: Path, root: Path, *, resolve: bool = False) -> bool:
    """Return whether a path stays below a root, lexically or after link resolution."""
    if resolve:
        path, root = path.resolve(), root.resolve()
    else:
        path, root = lexical_absolute(path), lexical_absolute(root)
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


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

    logical = lexical_absolute(repo_root / configured)
    if not stays_within(logical, repo_root):
        raise TrackerError("Tracker root must stay inside the repository.")

    if ensure:
        try:
            logical.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise TrackerError(f"Could not create Tracker root {configured.as_posix()}: {exc}") from exc
    return logical


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TrackerError(f"Could not read {path}: {exc}") from exc


def write_text(path: Path, content: str) -> None:
    """Create a tracker file without exposing a partially-written document."""
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


def h2_count(content: str, heading: str) -> int:
    return len(re.findall(rf"^##\s+{re.escape(heading)}\s*$", content, re.MULTILINE))


def h1_count(content: str) -> int:
    return len(re.findall(r"^#\s+.+?\s*$", content, re.MULTILINE))


def pre_question_metadata(content: str) -> str:
    match = re.search(r"^##\s+Question\s*$", content, re.MULTILINE)
    return content[: match.start()] if match else content


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


def parse_ticket(path: Path) -> tuple[Ticket | None, list[str]]:
    errors: list[str] = []
    match = TICKET_FILE_RE.match(path.name)
    if not match:
        return None, ["filename must use `NN-<type>-<slug>.md`"]

    try:
        content = read_text(path)
    except TrackerError as exc:
        return None, [str(exc)]

    number_text = match.group(1)
    title = first_h1(content)
    metadata = pre_question_metadata(content)
    raw_ticket_type = field(metadata, "Type")
    raw_state = field(metadata, "State")
    raw_blocked_by = field(metadata, "Blocked by")
    state = raw_state or ""
    blocked_by, blocker_errors = parse_blockers(raw_blocked_by)
    question = section(content, "Question")
    answer = section(content, "Answer")

    if h1_count(content) != 1 or is_placeholder(title):
        errors.append("missing Ticket title")
    for name, value in (
        ("Type", raw_ticket_type),
        ("State", raw_state),
        ("Blocked by", raw_blocked_by),
    ):
        count = len(re.findall(rf"^{re.escape(name)}:[ \t]*.*$", metadata, re.MULTILINE))
        if count != 1:
            errors.append(f"must contain exactly one `{name}:` field before `## Question`")
        elif name == "Type" and is_placeholder(value):
            errors.append("missing Type")
    if raw_ticket_type and not is_placeholder(raw_ticket_type):
        expected_prefix = f"{raw_ticket_type}-"
        filename_tail = match.group(2)
        if not filename_tail.startswith(expected_prefix):
            errors.append(
                "filename must be `NN-<type>-<slug>.md` with "
                f"`{raw_ticket_type}` matching the `Type:` field"
            )
    if state not in STATES:
        errors.append(f"State must be one of: {', '.join(sorted(STATES))}")
    if h2_count(content, "Question") != 1 or is_placeholder(question):
        errors.append("must contain exactly one non-empty `## Question`")
    answer_count = h2_count(content, "Answer")
    if state == "closed" and (answer_count != 1 or is_placeholder(answer)):
        errors.append("closed Ticket must contain exactly one non-empty `## Answer`")
    if state in {"open", "claimed"} and answer_count:
        errors.append(f"{state} Ticket must not contain `## Answer`")
    raw_legacy_claim = field(metadata, "Claimed by")
    legacy_claim_count = len(
        re.findall(r"^Claimed by:[ \t]*.*$", metadata, re.MULTILINE)
    )
    if legacy_claim_count:
        if raw_legacy_claim:
            errors.append(
                "legacy `Claimed by:` field is unsupported; "
                "change `State:` to `claimed` and remove the field"
            )
        else:
            errors.append("legacy `Claimed by:` field is unsupported; remove the field")
    errors.extend(blocker_errors)
    if len(blocked_by) != len(set(blocked_by)):
        errors.append("Blocked by contains duplicate Ticket IDs")

    ticket = Ticket(
        path=path,
        number=int(number_text),
        number_text=number_text,
        title=title,
        ticket_type=raw_ticket_type or "",
        state=state,
        blocked_by=blocked_by,
        question=question or "",
        answer=answer,
    )
    return ticket, errors


INDEX_ITEM_RE = re.compile(
    r"^-\s+\[([^\]]+)\]\(([^)\s]+)\)\s+—\s+(.+?)\s*$"
)


def parse_index_entries(
    content: str, heading: str, *, strict: bool
) -> tuple[list[IndexEntry], list[str]]:
    body = section(content, heading)
    if body is None:
        return [], []
    entries: list[IndexEntry] = []
    errors: list[str] = []
    in_comment = False
    for line_number, line in enumerate(body.splitlines(), start=1):
        if not line.strip():
            continue
        if in_comment:
            in_comment = "-->" not in line
            continue
        if line.lstrip().startswith("<!--"):
            in_comment = "-->" not in line
            continue
        match = INDEX_ITEM_RE.fullmatch(line)
        if not match:
            if strict:
                errors.append(
                    f"`## {heading}` line {line_number} must be "
                    "`- [Ticket title](issues/NN-type-slug.md) — gist`"
                )
            continue
        entries.append(
            IndexEntry(
                section_name=heading,
                title=match.group(1).strip(),
                target=match.group(2).strip(),
                gist=match.group(3).strip(),
            )
        )
    return entries, errors


def parse_map(map_dir: Path) -> tuple[MapData | None, list[str]]:
    map_path = map_dir / "map.md"
    domain_path = map_dir / "domain.md"
    errors: list[str] = []
    try:
        content = read_text(map_path)
    except TrackerError as exc:
        return None, [str(exc)]
    try:
        domain_content = read_text(domain_path)
    except TrackerError as exc:
        domain_content = None
        errors.append(str(exc))

    title = first_h1(content)
    destination = section(content, "Destination")
    if h1_count(content) != 1 or is_placeholder(title):
        errors.append("map.md: missing Map title")
    if is_placeholder(destination):
        errors.append("map.md: missing Destination")
    for heading in MAP_HEADINGS:
        count = h2_count(content, heading)
        if count != 1:
            errors.append(f"map.md: must contain exactly one `## {heading}`")

    headings = [
        match.group(1).strip()
        for match in re.finditer(r"^##\s+(.+?)\s*$", content, re.MULTILINE)
    ]
    if headings != list(MAP_HEADINGS):
        errors.append("map.md: top-level sections must be exactly the Wayfinder sections in template order")

    if domain_content is not None:
        domain_title = first_h1(domain_content)
        if h1_count(domain_content) != 1 or is_placeholder(domain_title):
            errors.append("domain.md: must contain exactly one non-placeholder H1 heading")
        domain_description_match = re.search(
            r"^#\s+.+?\s*$\n(.*?)(?=^##\s+|\Z)",
            domain_content,
            re.MULTILINE | re.DOTALL,
        )
        domain_description = (
            domain_description_match.group(1).strip() if domain_description_match else None
        )
        if is_placeholder(domain_description):
            errors.append("domain.md: must contain a non-placeholder description below its H1")
        if h2_count(domain_content, "Language") != 1:
            errors.append("domain.md: must contain exactly one `## Language` section")

    index_entries: list[IndexEntry] = []
    for heading, strict in (("Decisions so far", True), ("Out of scope", False)):
        entries, index_errors = parse_index_entries(content, heading, strict=strict)
        index_entries.extend(entries)
        errors.extend(f"map.md: {message}" for message in index_errors)

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
    errors.extend(validate_index_entries(map_dir, tickets, index_entries))

    tracked_files = [map_path, *([domain_path] if domain_path.is_file() else []), *ticket_files]
    updated_at = max((path.stat().st_mtime for path in tracked_files), default=map_path.stat().st_mtime)
    return MapData(
        directory=map_dir,
        path=map_path,
        title=title,
        destination=destination or "",
        tickets=tickets,
        index_entries=index_entries,
        updated_at=updated_at,
    ), errors


def validate_index_entries(
    map_dir: Path, tickets: list[Ticket], entries: list[IndexEntry]
) -> list[str]:
    errors: list[str] = []
    ticket_by_path = {f"issues/{ticket.path.name}": ticket for ticket in tickets}
    entries_by_ticket: dict[int, list[IndexEntry]] = {}

    for entry in entries:
        if entry.target not in ticket_by_path:
            errors.append(
                f"map.md: `{entry.section_name}` links to invalid Ticket path `{entry.target}`"
            )
            continue
        ticket = ticket_by_path[entry.target]
        entries_by_ticket.setdefault(ticket.number, []).append(entry)
        if entry.title != ticket.title:
            errors.append(
                f"map.md: index title `{entry.title}` must match Ticket {ticket.number_text} title `{ticket.title}`"
            )
        if not entry.gist:
            errors.append(f"map.md: index entry for Ticket {ticket.number_text} is missing a gist")

    for ticket in tickets:
        ticket_entries = entries_by_ticket.get(ticket.number, [])
        if ticket.state != "closed" and ticket_entries:
            errors.append(
                f"map.md: {ticket.state} Ticket {ticket.number_text} "
                "must not appear in a closed index"
            )
        if ticket.state == "closed" and len(ticket_entries) != 1:
            errors.append(
                f"map.md: closed Ticket {ticket.number_text} must appear exactly once in a closed index"
            )
        if len(ticket_entries) > 1:
            errors.append(f"map.md: Ticket {ticket.number_text} appears more than once in closed indexes")
    return errors


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


def configured_ticket_types(repo_root: Path) -> set[str]:
    try:
        content = read_text(repo_root / TICKET_TYPES_PATH)
    except TrackerError:
        return set()
    return {
        match.group(1).strip()
        for match in re.finditer(r"^##\s+([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", content, re.MULTILINE)
    }


def validate_ticket_types(map_data: MapData, allowed_types: set[str]) -> list[str]:
    if not allowed_types:
        return [f"could not load configured Ticket Types from {TICKET_TYPES_PATH.as_posix()}"]
    return [
        f"issues/{ticket.path.name}: Type `{ticket.ticket_type}` is not configured"
        for ticket in map_data.tickets
        if ticket.ticket_type not in allowed_types
    ]


def discover_map_dirs(tracker_root: Path) -> tuple[list[Path], list[str]]:
    """Find maps while rejecting directory links that escape the Tracker root."""
    map_dirs: list[Path] = []
    diagnostics: list[str] = []
    for child in sorted(tracker_root.iterdir()):
        if not child.is_dir() or not (child / "map.md").is_file():
            continue
        if not stays_within(child, tracker_root, resolve=True):
            diagnostics.append(f"{child.name}: Map path must stay inside the Tracker root.")
            continue
        map_dirs.append(child)
    return map_dirs, diagnostics


def load_maps(tracker_root: Path, allowed_types: set[str]) -> tuple[list[MapData], list[str]]:
    maps: list[MapData] = []
    map_dirs, diagnostics = discover_map_dirs(tracker_root)
    for child in map_dirs:
        map_data, errors = parse_map(child)
        if map_data is not None:
            maps.append(map_data)
            errors.extend(validate_ticket_types(map_data, allowed_types))
        diagnostics.extend(f"{child.name}: {message}" for message in errors)
    maps.sort(key=lambda item: item.updated_at, reverse=True)
    return maps, diagnostics


def repo_relative(path: Path, repo_root: Path) -> str:
    return lexical_absolute(path).relative_to(repo_root).as_posix()


def compact_text(value: str) -> str:
    return " ".join(value.split())


def ticket_is_unblocked(ticket: Ticket, ticket_by_number: dict[int, Ticket]) -> bool:
    return all(
        blocker in ticket_by_number and ticket_by_number[blocker].state == "closed"
        for blocker in ticket.blocked_by
    )


def resolve_map_dir(tracker_root: Path, map_ref: str) -> Path:
    candidate = lexical_absolute(tracker_root / map_ref)
    if not stays_within(candidate, tracker_root) or not stays_within(
        candidate, tracker_root, resolve=True
    ):
        raise TrackerError("Map reference must stay inside the Tracker root.")
    if not candidate.is_dir() or not (candidate / "map.md").is_file():
        raise TrackerError(f"Map not found: {map_ref}")
    return candidate


def command_collect(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    maps, diagnostics = load_maps(tracker_root, configured_ticket_types(repo_root))

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
            and ticket_is_unblocked(ticket, ticket_by_number)
        ]
        claimed = [
            ticket
            for ticket in map_data.tickets
            if ticket.state == "claimed"
        ]
        blocked = [
            ticket
            for ticket in map_data.tickets
            if ticket.state == "open"
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
            f"Active tickets: {active_count} — {len(frontier)} frontier, "
            f"{len(blocked)} blocked, {len(claimed)} claimed"
        )
        print()
        print("### Frontier")
        print()
        if frontier:
            for ticket in sorted(frontier, key=lambda item: item.number):
                print(f"- `{ticket.number_text}` {ticket.title} — {ticket.ticket_type}")
        else:
            print("None.")
        print()
        print("### Claimed")
        print()
        if claimed:
            for ticket in sorted(claimed, key=lambda item: item.number):
                print(f"- `{ticket.number_text}` {ticket.title} — {ticket.ticket_type}")
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


def validate_type_name(value: str) -> str:
    if not SLUG_RE.fullmatch(value):
        raise TrackerError("Type must contain lowercase letters, digits, and single hyphens only.")
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
    domain_path = map_dir / "domain.md"
    content = """# <Map title>

## Destination

<what reaching the end of this map looks like>

## Notes

<standing context and preferences>

## Decisions so far

## Not yet specified

<in-scope fog that cannot yet be stated as a Ticket>

## Out of scope

<work consciously ruled beyond this map's destination>
"""
    write_text(map_path, content)
    domain_content = """# <Context name>

<one or two sentence description of what this context is and why it exists>

## Language
"""
    write_text(domain_path, domain_content)
    print(repo_relative(map_path, repo_root))
    return 0


def command_create_ticket(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    map_dir = resolve_map_dir(tracker_root, args.map)
    ticket_type = validate_type_name(args.type)
    allowed_types = configured_ticket_types(repo_root)
    if ticket_type not in allowed_types:
        configured = ", ".join(sorted(allowed_types)) or "none"
        raise TrackerError(
            f"Type `{ticket_type}` is not configured. Configured Types: {configured}."
        )
    slug = validate_slug(args.slug)
    issues_dir = map_dir / "issues"
    issues_dir.mkdir(exist_ok=True)
    numbers = []
    for path in issues_dir.glob("*.md"):
        match = TICKET_FILE_RE.match(path.name)
        if match:
            numbers.append(int(match.group(1)))
    number = max(numbers, default=0) + 1
    issue_path = issues_dir / f"{number:02d}-{ticket_type}-{slug}.md"
    content = f"""# <Ticket title>

Type: {ticket_type}

State: open

Blocked by:

## Question

<the decision or investigation this Ticket resolves>
"""
    write_text(issue_path, content)
    print(repo_relative(issue_path, repo_root))
    return 0


def command_validate(args: argparse.Namespace) -> int:
    repo_root = find_repo_root()
    tracker_root = load_tracker_root(repo_root)
    discovery_errors: list[str] = []
    if args.map:
        map_dirs = [resolve_map_dir(tracker_root, args.map)]
    else:
        map_dirs, discovery_errors = discover_map_dirs(tracker_root)

    errors = discovery_errors
    allowed_types = configured_ticket_types(repo_root)
    for map_dir in map_dirs:
        map_data, map_errors = parse_map(map_dir)
        errors.extend(f"{map_dir.name}: {message}" for message in map_errors)
        if map_data is not None:
            errors.extend(
                f"{map_dir.name}: {message}"
                for message in validate_ticket_types(map_data, allowed_types)
            )

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
    map_parser.set_defaults(handler=command_create_map)

    ticket_parser = subparsers.add_parser("create-ticket", help="Create a child Ticket template")
    ticket_parser.add_argument("map", help="Map directory name")
    ticket_parser.add_argument("type", help="Configured Ticket Type")
    ticket_parser.add_argument("slug", help="Ticket filename slug")
    ticket_parser.set_defaults(handler=command_create_ticket)

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
