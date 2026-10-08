"""Maintainer workflow helpers for issue triage, review, and releases."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


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
        record.get("labels"),
        record.get("changed_files"),
        record.get("files"),
    )
    return " ".join(_as_text(field) for field in fields).lower()


def _matches(text: str, *patterns: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def _labels_from(record: Mapping[str, Any]) -> set[str]:
    labels = record.get("labels", [])
    if isinstance(labels, str):
        return {labels}
    if isinstance(labels, Iterable):
        return {str(label) for label in labels if str(label).strip()}
    return set()


def classify_issue(record: Mapping[str, Any]) -> dict[str, Any]:
    """Classify an issue-like record into maintainer labels and priority."""
    text = _combined_text(record)
    labels = _labels_from(record)
    rationale: list[str] = []

    if _matches(text, r"\b(security|vulnerability|cve|secret|token|credential|path traversal|signature)\b"):
        labels.add("security")
        rationale.append("Security-sensitive terms were detected.")
    if _matches(text, r"\b(bug|crash|traceback|regression|broken|incorrect|mismatch|fails?|error)\b"):
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
    files = record.get("files") or record.get("changed_files") or []
    if isinstance(files, str):
        files = [files]
    files = [str(path) for path in files]
    rationale: list[str] = []
    focus: list[str] = []

    if any(path.startswith(".github/") for path in files):
        labels.add("maintenance")
        focus.append("Repository automation and GitHub metadata")
    if any(path.startswith("docs/") or path.endswith(".md") for path in files):
        labels.add("documentation")
        focus.append("Documentation accuracy and links")
    if any(path.startswith("tests/") for path in files) or _matches(text, r"\b(test|coverage|lint|quality)\b"):
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
    blocker_count = len(list(blockers))
    gates = [
        ("ci", manifest.get("ci_status") == "passing", "CI status is passing."),
        ("tests", manifest.get("tests_passed") is True, "Automated tests passed."),
        ("quality", manifest.get("quality_gate") in (True, "passing"), "Linting or repository quality gate passed."),
        ("security", manifest.get("security_review") in (True, "complete", "completed"), "Security review is complete."),
        ("artifacts", manifest.get("artifacts_verified") is True, "Release artifacts were verified."),
        ("docs", manifest.get("docs_updated") is True, "Documentation was updated."),
        ("changelog", manifest.get("changelog_updated") is True, "Changelog was updated."),
        ("notes", manifest.get("release_notes_ready") is True, "Release notes are ready."),
        ("blockers", blocker_count == 0, "No unresolved release blockers remain."),
    ]
    gate_reports = [
        {
            "name": name,
            "passed": bool(passed),
            "severity": "error" if not passed else "info",
            "evidence": evidence,
        }
        for name, passed, evidence in gates
    ]
    failed = [gate for gate in gate_reports if not gate["passed"]]
    return {
        "schema_version": 1,
        "kind": "release_readiness",
        "version": _as_text(manifest.get("version")).strip(),
        "ready": not failed,
        "failed_gates": [gate["name"] for gate in failed],
        "gates": gate_reports,
    }


def generate_release_notes(change_log: Mapping[str, Any]) -> str:
    """Generate grouped Markdown release notes from a structured change list."""
    version = _as_text(change_log.get("version") or "Unreleased").strip()
    date = _as_text(change_log.get("date")).strip()
    changes = change_log.get("changes", [])
    groups = {
        "Security": [],
        "Added": [],
        "Changed": [],
        "Fixed": [],
        "Documentation": [],
        "Quality": [],
    }
    for item in changes if isinstance(changes, list) else []:
        if not isinstance(item, Mapping):
            continue
        text = _as_text(item.get("summary")).strip()
        if not text:
            continue
        kind = _as_text(item.get("type")).lower()
        labels = {label.lower() for label in _labels_from(item)}
        if "security" in labels or kind == "security":
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
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"Cannot read JSON file: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Cannot parse JSON file: {error}") from error
    if not isinstance(data, dict):
        raise ValueError("JSON input must be an object.")
    return data
