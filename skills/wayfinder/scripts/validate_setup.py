#!/usr/bin/env python3
"""Validate Wayfinder's repository-local configuration structure."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


WAYFINDER_PATH = Path("docs/agents/wayfinder/wayfinder.md")
TICKET_TYPES_PATH = Path("docs/agents/wayfinder/ticket-types.md")
WAYFINDER_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "wayfinder.md"

TYPE_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^(#{1,2})\s+(.+?)\s*$", re.MULTILINE)
FIELD_RE = re.compile(r"^-\s+\*\*(.+?):\*\*\s*(.*?)\s*$", re.MULTILINE)
DEFINITION_RE = re.compile(r"^-\s+\*\*(.+?)\*\*:\s*(.*?)\s*$", re.MULTILINE)
TRACKER_ROOT_RE = re.compile(r"^Tracker root:\s*`([^`]+)`\s*$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"^<[^>\n]+>$")
REQUIRED_TYPE_FIELDS = ("Interaction", "Use when", "Resolve")
OPTIONAL_TYPE_FIELDS = ("After creation",)
KNOWN_TYPE_FIELDS = set(REQUIRED_TYPE_FIELDS + OPTIONAL_TYPE_FIELDS)
METHODS_HEADING = "Wayfinding methods"
OPERATIONS_HEADING = "Tracker operations"


@dataclass
class TypeSection:
    name: str
    body: str


class ValidationError(Exception):
    pass


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValidationError(f"Could not read {path}: {exc}") from exc


def find_repo_root(override: str | None = None) -> Path:
    configured = override or os.environ.get("WAYFINDER_REPO_ROOT")
    if configured:
        return Path(configured).resolve()

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
        if (candidate / ".git").exists() or (candidate / WAYFINDER_PATH).is_file():
            return candidate
    raise ValidationError("Could not locate the repository root")


def lexical_absolute(path: Path) -> Path:
    """Make a path absolute without resolving symlinks or junctions."""
    return Path(os.path.abspath(path))


def stays_within(path: Path, root: Path) -> bool:
    """Return whether a path stays lexically below a root."""
    try:
        lexical_absolute(path).relative_to(lexical_absolute(root))
    except ValueError:
        return False
    return True


def heading_sections(content: str, level: str = "##") -> list[tuple[str, str]]:
    headings = [match for match in HEADING_RE.finditer(content) if match.group(1) == level]
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
        sections.append((match.group(2).strip(), content[match.end() : end]))
    return sections


def named_definitions(content: str, heading: str) -> tuple[list[str], dict[str, list[str]]]:
    matching = [body for name, body in heading_sections(content) if name == heading]
    if len(matching) != 1:
        return [f"document must contain exactly one `## {heading}` section"], {}

    definitions: dict[str, list[str]] = {}
    for match in DEFINITION_RE.finditer(matching[0]):
        definitions.setdefault(match.group(1).strip(), []).append(match.group(2).strip())
    return [], definitions


def validate_definitions(
    content: str,
    heading: str,
    required_names: tuple[str, ...],
) -> list[str]:
    errors, definitions = named_definitions(content, heading)
    if errors:
        return errors
    for name in required_names:
        values = definitions.get(name, [])
        if len(values) != 1:
            errors.append(f"`{heading}` must define `{name}` exactly once")
        elif not values[0] or PLACEHOLDER_RE.fullmatch(values[0]):
            errors.append(f"`{heading}` has an empty or placeholder `{name}` definition")
    return errors


def required_definition_names(template: str, heading: str) -> tuple[str, ...]:
    errors, definitions = named_definitions(template, heading)
    if errors:
        raise ValidationError(f"Bundled Wayfinder template is invalid: {errors[0]}")
    if not definitions:
        raise ValidationError(
            f"Bundled Wayfinder template defines no entries under `## {heading}`"
        )
    return tuple(definitions)


def validate_wayfinder(content: str, template: str, repo_root: Path) -> list[str]:
    errors: list[str] = []
    h1s = [match.group(2).strip() for match in HEADING_RE.finditer(content) if match.group(1) == "#"]
    if h1s != ["Wayfinder"]:
        errors.append("document must contain exactly one `# Wayfinder` heading")

    roots = TRACKER_ROOT_RE.findall(content)
    if len(roots) != 1:
        errors.append("document must contain exactly one `Tracker root: `<path>`` setting")
    else:
        root_value = roots[0].strip()
        configured = Path(root_value)
        if not root_value or PLACEHOLDER_RE.fullmatch(root_value):
            errors.append("Tracker root must not be empty or a placeholder")
        elif configured.is_absolute():
            errors.append("Tracker root must be relative to the repository root")
        elif not stays_within(repo_root / configured, repo_root):
            errors.append("Tracker root must stay inside the repository")

    for heading in (METHODS_HEADING, OPERATIONS_HEADING):
        required = required_definition_names(template, heading)
        errors.extend(validate_definitions(content, heading, required))
    return errors


def parse_type_sections(content: str) -> tuple[list[str], list[TypeSection]]:
    headings = list(HEADING_RE.finditer(content))
    errors: list[str] = []
    h1s = [match for match in headings if match.group(1) == "#"]
    if len(h1s) != 1 or h1s[0].group(2).strip() != "Ticket Types":
        errors.append("document must contain exactly one `# Ticket Types` heading")

    type_headings = [match for match in headings if match.group(1) == "##"]
    if not type_headings:
        errors.append("document must define at least one `## <type>` section")

    sections: list[TypeSection] = []
    for index, match in enumerate(type_headings):
        end = type_headings[index + 1].start() if index + 1 < len(type_headings) else len(content)
        sections.append(TypeSection(name=match.group(2).strip(), body=content[match.end() : end]))
    return errors, sections


def validate_ticket_types(content: str) -> list[str]:
    errors, sections = parse_type_sections(content)
    if "<!-- wayfinder-setup" in content:
        errors.append("generated document still contains `wayfinder-setup` metadata")

    seen: set[str] = set()
    for section in sections:
        name = section.name
        if not TYPE_NAME_RE.fullmatch(name):
            errors.append(
                f"Type `{name}` must use lowercase letters, digits, and single hyphens only"
            )
        normalized = name.casefold()
        if normalized in seen:
            errors.append(f"duplicate Type `{name}`")
        seen.add(normalized)

        values: dict[str, list[str]] = {}
        for match in FIELD_RE.finditer(section.body):
            field_name = match.group(1).strip()
            field_value = match.group(2).strip()
            values.setdefault(field_name, []).append(field_value)
            if field_name not in KNOWN_TYPE_FIELDS:
                errors.append(f"Type `{name}` has unknown field `{field_name}`")

        for field_name in REQUIRED_TYPE_FIELDS:
            occurrences = values.get(field_name, [])
            if len(occurrences) != 1:
                errors.append(f"Type `{name}` must contain exactly one `{field_name}` field")
            elif not occurrences[0] or PLACEHOLDER_RE.fullmatch(occurrences[0]):
                errors.append(f"Type `{name}` has an empty or placeholder `{field_name}`")

        for field_name in OPTIONAL_TYPE_FIELDS:
            occurrences = values.get(field_name, [])
            if len(occurrences) > 1:
                errors.append(f"Type `{name}` contains duplicate `{field_name}` fields")
            elif occurrences and (
                not occurrences[0] or PLACEHOLDER_RE.fullmatch(occurrences[0])
            ):
                errors.append(f"Type `{name}` has an empty or placeholder `{field_name}`")

        interaction = values.get("Interaction", [""])[0]
        if interaction and not re.search(r"\b(?:HITL|AFK)\b", interaction):
            errors.append(f"Type `{name}` Interaction must name HITL, AFK, or both")

    return errors


def command_validate(repo_root: Path) -> int:
    try:
        template = read_text(WAYFINDER_TEMPLATE)
    except ValidationError as exc:
        print(f"Setup validator error: {exc}", file=sys.stderr)
        return 1

    checks = (
        (WAYFINDER_PATH, lambda content: validate_wayfinder(content, template, repo_root)),
        (TICKET_TYPES_PATH, validate_ticket_types),
    )
    diagnostics: list[str] = []
    for relative_path, validator in checks:
        try:
            content = read_text(repo_root / relative_path)
        except ValidationError as exc:
            diagnostics.append(f"{relative_path.as_posix()}: {exc}")
            continue
        diagnostics.extend(
            f"{relative_path.as_posix()}: {error}" for error in validator(content)
        )

    if diagnostics:
        print(f"Setup validation found {len(diagnostics)} error(s):")
        for diagnostic in diagnostics:
            print(f"- {diagnostic}")
        return 1
    print("Wayfinder setup validation passed.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate Wayfinder repository setup")
    parser.add_argument(
        "--repo-root",
        help="Repository root (default: WAYFINDER_REPO_ROOT, Git root, or current ancestors)",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        repo_root = find_repo_root(args.repo_root)
    except ValidationError as exc:
        print(f"Setup validator error: {exc}", file=sys.stderr)
        return 1
    return command_validate(repo_root)


if __name__ == "__main__":
    raise SystemExit(main())
