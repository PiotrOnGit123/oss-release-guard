"""Tests for maintainer workflow helpers and CLI commands."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT
sys.path.insert(0, str(SOURCE_ROOT))

from oss_release_guard.maintainer import (  # noqa: E402
    assess_release_readiness,
    build_review_checklist,
    classify_issue,
    classify_pull_request,
    generate_release_notes,
)


class MaintainerWorkflowTests(unittest.TestCase):
    def test_security_issue_gets_security_triage_and_high_priority(self) -> None:
        result = classify_issue(
            {
                "title": "Potential token leak in release manifest",
                "body": "A generated JSON report may include a credential-like token in logs.",
            }
        )
        self.assertIn("security", result["labels"])
        self.assertIn("triage", result["labels"])
        self.assertEqual(result["priority"], "P0")
        self.assertEqual(result["routing"], "security-maintainers")

    def test_documentation_issue_can_be_good_first_issue(self) -> None:
        result = classify_issue(
            {
                "title": "Document a small release notes example",
                "body": "This is a low risk docs task suitable for a first contribution.",
            }
        )
        self.assertIn("documentation", result["labels"])
        self.assertIn("good first issue", result["labels"])
        self.assertEqual(result["risk"], "low")

    def test_pull_request_classifier_reads_files_and_text(self) -> None:
        result = classify_pull_request(
            {
                "title": "Add release readiness notes",
                "body": "Updates release checklist and quality gate docs.",
                "files": ["docs/release-process.md", ".github/pull_request_template.md", "tests/test_maintainer_workflows.py"],
            }
        )
        for label in ("documentation", "maintenance", "quality", "release", "needs-review"):
            self.assertIn(label, result["labels"])
        self.assertEqual(result["risk"], "medium")

    def test_review_checklist_includes_security_and_quality_sections(self) -> None:
        checklist = build_review_checklist({"title": "Security hardening", "body": "path traversal", "files": ["oss_release_guard/core.py"]})
        self.assertIn("## Security", checklist)
        self.assertIn("## Quality", checklist)
        self.assertIn("Suggested labels:", checklist)

    def test_release_readiness_reports_failed_gates(self) -> None:
        result = assess_release_readiness(
            {
                "version": "v0.2.0",
                "ci_status": "failing",
                "tests_passed": True,
                "quality_gate": "passing",
                "security_review": "complete",
                "artifacts_verified": True,
                "docs_updated": True,
                "changelog_updated": True,
                "release_notes_ready": False,
                "unresolved_blockers": ["release notes missing"],
            }
        )
        self.assertFalse(result["ready"])
        self.assertEqual(result["failed_gates"], ["ci", "notes", "blockers"])

    def test_release_notes_are_grouped_by_maintenance_domain(self) -> None:
        notes = generate_release_notes(
            {
                "version": "v0.2.0",
                "date": "2026-10-08",
                "changes": [
                    {"type": "security", "summary": "Harden archive path policy", "reference": "#3"},
                    {"labels": ["bug"], "summary": "Fix duplicate member reporting", "reference": "#1"},
                    {"type": "docs", "summary": "Document triage rotation"},
                    {"type": "quality", "summary": "Add local quality gate"},
                ],
            }
        )
        for heading in ("## Security", "## Fixed", "## Documentation", "## Quality"):
            self.assertIn(heading, notes)
        self.assertIn("Harden archive path policy (#3)", notes)


class MaintainerCliTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SOURCE_ROOT) + os.pathsep + environment.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "oss_release_guard", *arguments],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )

    def write_json(self, payload: dict) -> Path:
        temp = tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False)
        self.addCleanup(lambda: Path(temp.name).unlink(missing_ok=True))
        with temp:
            json.dump(payload, temp)
        return Path(temp.name)

    def test_triage_issue_cli_outputs_json(self) -> None:
        path = self.write_json({"title": "Release blocker bug", "body": "Tests fail before publishing"})
        result = self.run_cli("triage-issue", str(path), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertIn("bug", report["labels"])
        self.assertIn("release", report["labels"])

    def test_release_readiness_cli_exits_one_when_not_ready(self) -> None:
        path = self.write_json({"version": "v0.2.0", "ci_status": "failing"})
        result = self.run_cli("release-readiness", str(path))
        self.assertEqual(result.returncode, 1)
        self.assertIn("NOT READY", result.stdout)

    def test_release_notes_cli_outputs_markdown(self) -> None:
        path = self.write_json({"version": "v0.2.0", "changes": [{"type": "docs", "summary": "Add review guidelines"}]})
        result = self.run_cli("release-notes", str(path))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Documentation", result.stdout)


if __name__ == "__main__":
    unittest.main()
