"""Maintainer workflow helpers for issue triage, review, and releases."""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

MAX_JSON_BYTES = 1_048_576
VERSION_PATTERN = re.compile(
    r"v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z]+(?:[.-][0-9A-Za-z]+)*)?"
)


def _string_items(value: Any, field: str, object_key: str) -> list[str]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a string or a list of strings or GitHub objects.")
    items = []
    for item in value:
        if isinstance(item, Mapping):
            item = item.get(object_key)
        if not isinstance(item, str):
            raise ValueError(f"{field} entries must contain a string {object_key}.")
        if item.strip():
            items.append(item.strip())
    return items


def _files_from(record: Mapping[str, Any]) -> list[str]:
    return _string_items(record.get("files", record.get("changed_files", [])), "files", "filename")


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, Iterable) and not isinstance(value, (bytes, bytearray, Mapping)):
        return " ".join(_as_text(item) for item in value)
    return str(value)


def _combined_text(record: Mapping[str, Any]) -> str:
    fields = (
        record.get("title"),
        record.get("body"),
        record.get("summary"),
        sorted(_labels_from(record)),
        _files_from(record),
    )
    return " ".join(_as_text(field) for field in fields).lower()


def _matches(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _labels_from(record: Mapping[str, Any]) -> set[str]:
    return set(_string_items(record.get("labels", []), "labels", "name"))


def classify_issue(record: Mapping[str, Any]) -> dict[str, Any]:
    """Classify an issue-like record into maintainer labels and priority."""
    text = _combined_text(record)
    labels = _labels_from(record)
    rationale: list[str] = []

    if _matches(
        text, r"\b(security|vulnerability|cve|secret|token|credential|path traversal|signature)\b"
    ):
        labels.add("security")
        rationale.append("Security-sensitive terms were detected.")
    if _matches(
        text, r"\b(bug|crash|traceback|regression|broken|incorrect|mismatch|fails?|error)\b"
    ):
        labels.add("bug")
        rationale.append("Failure or regression language was detected.")
    if _matches(text, r"\b(release|changelog|version|tag|milestone|publish|cut)\b"):
        labels.add("release")
        rationale.append("Release-management language was detected.")
    if _matches(text, r"\b(doc|docs|readme|tutorial|example|guide|typo)\b"):
        labels.add("documentation")
        rationale.append("Documentation or example language was detected.")
    if _matches(text, r"\b(test|lint|coverage|refactor|quality|flaky|maintainability|typing)\b"):
        labels.add("quality")
        rationale.append("Quality-gate or maintainability language was detected.")
    if _matches(text, r"\b(good first issue|starter|small|typo|first contribution|low risk)\b"):
        labels.add("good first issue")
        rationale.append("The scope appears suitable for a first contribution.")

    if "security" in labels:
        labels.discard("good first issue")
        priority = "P0" if _matches(text, r"\b(exploit|leak|credential|token|cve)\b") else "P1"
        routing = "security-maintainers"
        risk = "high"
    elif "release" in labels and _matches(text, r"\b(blocker|ship|publish|tag|milestone)\b"):
        priority = "P1"
        routing = "release-manager"
        risk = "medium"
    elif "bug" in labels:
        priority = "P2"
        routing = "core-maintainers"
        risk = "medium"
    elif "documentation" in labels and labels <= {"documentation", "good first issue"}:
        priority = "P3"
        routing = "docs-maintainers"
        risk = "low"
    else:
        priority = "P3"
        routing = "triage-rotation"
        risk = "low"

    labels.add("triage")
    if not rationale:
        rationale.append("No strong keyword match was found; send through standard triage.")

    return {
        "schema_version": 1,
        "kind": "issue_triage",
        "title": _as_text(record.get("title")).strip(),
        "labels": sorted(labels),
        "priority": priority,
        "risk": risk,
        "routing": routing,
        "rationale": rationale,
    }


def classify_pull_request(record: Mapping[str, Any]) -> dict[str, Any]:
    """Classify a pull-request-like record and suggest review focus areas."""
    text = _combined_text(record)
    labels = _labels_from(record)
    files = _files_from(record)
    rationale: list[str] = []
    focus: list[str] = []

    if any(path.startswith(".github/") for path in files):
        labels.add("maintenance")
        focus.append("Repository automation and GitHub metadata")
    if any(path.startswith("docs/") or path.endswith(".md") for path in files):
        labels.add("documentation")
        focus.append("Documentation accuracy and links")
    if any(path.startswith("tests/") for path in files) or _matches(
        text, r"\b(test|coverage|lint|quality)\b"
    ):
        labels.add("quality")
        focus.append("Test coverage and quality gates")
    if _matches(text, r"\b(security|vulnerability|secret|token|path traversal|signature)\b"):
        labels.add("security")
        focus.append("Security impact and disclosure handling")
    if _matches(text, r"\b(release|changelog|version|notes|milestone)\b"):
        labels.add("release")
        focus.append("Release notes, changelog, and migration impact")
    if _matches(text, r"\b(breaking|incompatible|remove|deprecate)\b"):
        labels.add("breaking-change")
        focus.append("Backward compatibility")

    if len(files) > 8:
        labels.add("needs-review")
        risk = "high"
        rationale.append("Large file count requires extra review attention.")
    elif "security" in labels or "breaking-change" in labels:
        labels.add("needs-review")
        risk = "high"
        rationale.append("Security or compatibility impact requires maintainer review.")
    elif "release" in labels:
        labels.add("needs-review")
        risk = "medium"
        rationale.append("Release-facing changes require release-manager review.")
    else:
        labels.add("needs-review")
        risk = "low"
        rationale.append("Standard review checklist applies.")

    if not focus:
        focus.append("Correctness, tests, and user-facing behavior")

    return {
        "schema_version": 1,
        "kind": "pull_request_review",
        "title": _as_text(record.get("title")).strip(),
        "labels": sorted(labels),
        "risk": risk,
        "review_focus": focus,
        "rationale": rationale,
    }


def build_review_checklist(record: Mapping[str, Any]) -> str:
    """Generate a Markdown checklist for a pull request."""
    classification = classify_pull_request(record)
    lines = [
        "# Pull Request Review Checklist",
        "",
        f"Risk: {classification['risk']}",
        f"Suggested labels: {', '.join(classification['labels'])}",
        "",
        "## Scope",
        "- [ ] The PR description explains the user-visible change.",
        "- [ ] Related issues, release notes, and migration notes are linked.",
        "- [ ] The change is small enough to review or explicitly split into phases.",
        "",
        "## Quality",
        "- [ ] Tests cover success, failure, and boundary cases.",
        "- [ ] Local quality gates pass before merge.",
        "- [ ] Documentation and examples match the implemented behavior.",
        "",
        "## Security",
        "- [ ] Inputs, file paths, and generated output are validated.",
        "- [ ] No secrets, tokens, private data, or unsafe defaults are introduced.",
        "- [ ] Security-sensitive findings have a private handling path if needed.",
        "",
        "## Reviewer Focus",
    ]
    lines.extend(f"- [ ] {item}" for item in classification["review_focus"])
    return "\n".join(lines) + "\n"


def assess_release_readiness(manifest: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate release readiness gates from a manifest."""
    blockers = manifest.get("unresolved_blockers", [])
    if isinstance(blockers, str):
        blockers = [blockers]
    if not isinstance(blockers, list) or any(
        not isinstance(item, str) or not item.strip() for item in blockers
    ):
        raise ValueError("unresolved_blockers must be a string or a list of nonempty strings.")
    version = manifest.get("version", "")
    if not isinstance(version, str):
        raise ValueError("version must be a string.")
    sensitive_count = _count_sensitive_keys(manifest)
    gates = [
        (
            "version",
            VERSION_PATTERN.fullmatch(version) is not None,
            "A release version such as v0.2.0 is required.",
        ),
        ("ci", manifest.get("ci_status") == "passing", "CI status is passing."),
        ("tests", manifest.get("tests_passed") is True, "Automated tests passed."),
        (
            "quality",
            _confirmed(manifest.get("quality_gate"), {"passing"}),
            "Linting or repository quality gate passed.",
        ),
        (
            "security",
            _confirmed(manifest.get("security_review"), {"complete", "completed"}),
            "Security review is complete.",
        ),
        (
            "artifacts",
            manifest.get("artifacts_verified") is True,
            "Release artifacts were verified.",
        ),
        ("docs", manifest.get("docs_updated") is True, "Documentation was updated."),
        ("changelog", manifest.get("changelog_updated") is True, "Changelog was updated."),
        ("notes", manifest.get("release_notes_ready") is True, "Release notes are ready."),
        ("blockers", len(blockers) == 0, "No unresolved release blockers remain."),
        (
            "sensitive_fields",
            sensitive_count == 0,
            "The manifest must not contain secret-like field names.",
        ),
    ]
    gate_reports = [
        {
            "name": name,
            "passed": bool(passed),
            "severity": "error" if not passed else "info",
            "evidence": evidence if passed else f"Requirement not met: {evidence}",
        }
        for name, passed, evidence in gates
    ]
    failed = [gate for gate in gate_reports if not gate["passed"]]
    return {
        "schema_version": 1,
        "kind": "release_readiness",
        "version": version if VERSION_PATTERN.fullmatch(version) else "",
        "ready": not failed,
        "sensitive_field_count": sensitive_count,
        "failed_gates": [gate["name"] for gate in failed],
        "gates": gate_reports,
    }


def _confirmed(value: Any, statuses: set[str]) -> bool:
    return value is True or (isinstance(value, str) and value in statuses)


def _count_sensitive_keys(value: Any) -> int:
    """Count suspect names without copying either names or values into reports."""
    count = 0
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = re.sub(r"([a-z])([A-Z])", r"\1_\2", str(key)).lower()
            if re.search(
                r"(?:^|[_-])(token|password|passwd|secret|credentials?|authorization|api[_-]?key|private[_-]?key)(?:$|[_-])",
                normalized,
            ):
                count += 1
            count += _count_sensitive_keys(item)
    elif isinstance(value, list):
        count += sum(_count_sensitive_keys(item) for item in value)
    return count


def generate_release_notes(change_log: Mapping[str, Any]) -> str:
    """Generate grouped Markdown release notes from a structured change list."""
    version = _as_text(change_log.get("version") or "Unreleased").strip()
    date = _as_text(change_log.get("date")).strip()
    changes = change_log.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError("changes must be a list of change objects.")
    groups = {
        "Breaking Changes": [],
        "Security": [],
        "Added": [],
        "Changed": [],
        "Fixed": [],
        "Documentation": [],
        "Quality": [],
    }
    for item in changes:
        if not isinstance(item, Mapping):
            raise ValueError("Each change must be an object.")
        text = _as_text(item.get("summary")).strip()
        if not text:
            raise ValueError("Each change must have a nonempty summary.")
        kind = _as_text(item.get("type")).lower()
        labels = {label.lower() for label in _labels_from(item)}
        if "breaking-change" in labels or kind == "breaking":
            group = "Breaking Changes"
        elif "security" in labels or kind == "security":
            group = "Security"
        elif "bug" in labels or kind in {"fix", "fixed", "bugfix"}:
            group = "Fixed"
        elif "documentation" in labels or kind in {"docs", "documentation"}:
            group = "Documentation"
        elif "quality" in labels or kind in {"quality", "test", "tests"}:
            group = "Quality"
        elif kind in {"change", "changed"}:
            group = "Changed"
        else:
            group = "Added"
        reference = _as_text(item.get("reference")).strip()
        groups[group].append(f"{text} ({reference})" if reference else text)

    heading = f"# {version}"
    if date:
        heading += f" - {date}"
    lines = [heading, ""]
    for group, entries in groups.items():
        if entries:
            lines.extend([f"## {group}", ""])
            lines.extend(f"- {entry}" for entry in entries)
            lines.append("")
    if len(lines) == 2:
        lines.extend(["## Changed", "", "- No user-facing changes recorded.", ""])
    return "\n".join(lines).rstrip() + "\n"


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object for CLI helper commands."""
    try:
        with Path(path).open("rb") as source:
            raw = source.read(MAX_JSON_BYTES + 1)
    except OSError as error:
        raise ValueError("Cannot read JSON input.") from error
    if len(raw) > MAX_JSON_BYTES:
        raise ValueError("JSON input exceeds the 1 MiB limit.")
    try:
        data = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
            parse_float=_finite_float,
        )
        _check_depth(data)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError("Input must be a valid UTF-8 JSON object.") from error
    if not isinstance(data, dict):
        raise ValueError("JSON input must be an object.")
    return data


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON keys are not allowed.")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError("Non-finite JSON numbers are not allowed.")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Non-finite JSON numbers are not allowed.")
    return number


def _check_depth(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise ValueError("JSON nesting exceeds the 32-level limit.")
    items = value.values() if isinstance(value, dict) else value if isinstance(value, list) else []
    for item in items:
        _check_depth(item, depth + 1)
