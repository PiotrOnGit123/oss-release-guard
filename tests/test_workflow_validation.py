"""Regression coverage for release decisions and real GitHub input shapes."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from oss_release_guard.maintainer import (
    MAX_JSON_BYTES,
    assess_release_readiness,
    classify_issue,
    classify_pull_request,
    generate_release_notes,
    load_json,
)
from tests import test_maintainer_workflows as cli_support


def ready_manifest() -> dict:
    return {
        "version": "v0.2.0",
        "ci_status": "passing",
        "tests_passed": True,
        "quality_gate": "passing",
        "security_review": "complete",
        "artifacts_verified": True,
        "docs_updated": True,
        "changelog_updated": True,
        "release_notes_ready": True,
        "unresolved_blockers": [],
    }


class ReleaseDecisionTests(unittest.TestCase):
    def test_complete_manifest_passes(self) -> None:
        report = assess_release_readiness(ready_manifest())
        self.assertTrue(report["ready"])
        self.assertEqual(report["failed_gates"], [])

    def test_each_required_gate_blocks_release_individually(self) -> None:
        failures = {
            "version": ("version", "invalid"),
            "ci": ("ci_status", "failing"),
            "tests": ("tests_passed", False),
            "quality": ("quality_gate", False),
            "security": ("security_review", "pending"),
            "artifacts": ("artifacts_verified", False),
            "docs": ("docs_updated", False),
            "changelog": ("changelog_updated", False),
            "notes": ("release_notes_ready", False),
            "blockers": ("unresolved_blockers", ["regression"]),
            "sensitive_fields": ("api_token", "synthetic-value"),
        }
        for gate, (field, value) in failures.items():
            with self.subTest(gate=gate):
                manifest = ready_manifest()
                manifest[field] = value
                report = assess_release_readiness(manifest)
                self.assertFalse(report["ready"])
                self.assertEqual(report["failed_gates"], [gate])
                failed = next(item for item in report["gates"] if item["name"] == gate)
                self.assertTrue(failed["evidence"].startswith("Requirement not met:"))

    def test_missing_version_never_passes(self) -> None:
        manifest = ready_manifest()
        del manifest["version"]
        self.assertEqual(assess_release_readiness(manifest)["failed_gates"], ["version"])

    def test_integer_one_is_not_a_confirmation(self) -> None:
        for field, gate in (("quality_gate", "quality"), ("security_review", "security")):
            for value in (1, 0, [], {}, None):
                with self.subTest(field=field, value=value):
                    manifest = ready_manifest()
                    manifest[field] = value
                    self.assertIn(gate, assess_release_readiness(manifest)["failed_gates"])

    def test_boolean_confirmations_and_prerelease_version(self) -> None:
        manifest = ready_manifest()
        manifest.update(version="v0.2.0-rc.1", quality_gate=True, security_review=True)
        self.assertTrue(assess_release_readiness(manifest)["ready"])

    def test_malformed_blockers_are_input_errors(self) -> None:
        for value in (None, 3, {}, [False], [""]):
            with self.subTest(value=value):
                manifest = ready_manifest()
                manifest["unresolved_blockers"] = value
                with self.assertRaises(ValueError):
                    assess_release_readiness(manifest)

    def test_string_blocker_is_supported(self) -> None:
        manifest = ready_manifest()
        manifest["unresolved_blockers"] = "pending fix"
        self.assertIn("blockers", assess_release_readiness(manifest)["failed_gates"])

    def test_numeric_version_is_an_input_error(self) -> None:
        with self.assertRaises(ValueError):
            assess_release_readiness({"version": 1})

    def test_nested_secret_names_are_detected_without_disclosing_values(self) -> None:
        manifest = ready_manifest()
        manifest["metadata"] = {
            "apiToken": "dummy-sensitive-value",
            "items": [{"private_key": "dummy-key-value"}],
        }
        report = assess_release_readiness(manifest)
        self.assertEqual(report["sensitive_field_count"], 2)
        self.assertFalse(report["ready"])
        encoded = json.dumps(report)
        for value in ("dummy-sensitive-value", "dummy-key-value", "apiToken", "private_key"):
            self.assertNotIn(value, encoded)


class GithubRecordTests(unittest.TestCase):
    def test_label_objects_are_preserved_as_names(self) -> None:
        report = classify_issue({"title": "A typo", "labels": [{"name": "documentation"}]})
        self.assertIn("documentation", report["labels"])
        self.assertFalse(any("{" in label for label in report["labels"]))

    def test_template_file_objects_trigger_maintenance_review(self) -> None:
        for field in ("files", "changed_files"):
            with self.subTest(field=field):
                report = classify_pull_request(
                    {
                        "title": "Template adjustment",
                        field: [{"filename": ".github/ISSUE_TEMPLATE/bug_report.yml"}],
                    }
                )
                self.assertIn("maintenance", report["labels"])
                self.assertIn("needs-review", report["labels"])
                self.assertIn("Repository automation and GitHub metadata", report["review_focus"])

    def test_security_work_is_not_assigned_to_first_time_contributors(self) -> None:
        report = classify_issue(
            {"title": "Small security docs task", "labels": ["good first issue"]}
        )
        self.assertIn("security", report["labels"])
        self.assertNotIn("good first issue", report["labels"])

    def test_malformed_labels_and_files_raise_input_errors(self) -> None:
        for record in ({"labels": None}, {"labels": [{}]}, {"files": 3}, {"files": [{}]}):
            with self.subTest(record=record):
                with self.assertRaises(ValueError):
                    classify_pull_request(record)

    def test_string_labels_and_file_are_supported(self) -> None:
        report = classify_pull_request({"labels": "quality", "files": "docs/review-guidelines.md"})
        self.assertIn("documentation", report["labels"])
        self.assertIn("quality", report["labels"])

    def test_large_and_security_pull_requests_require_high_risk_review(self) -> None:
        for record in (
            {"files": [f"module{i}.py" for i in range(9)]},
            {"title": "Security fix"},
            {"title": "Breaking API change"},
        ):
            with self.subTest(record=record):
                self.assertEqual(classify_pull_request(record)["risk"], "high")

    def test_release_notes_keep_duplicate_archive_findings_under_fixed(self) -> None:
        notes = generate_release_notes(
            {
                "changes": [
                    {
                        "labels": [{"name": "bug"}],
                        "summary": "Reject duplicate ZIP destinations",
                        "reference": "#5",
                    }
                ]
            }
        )
        self.assertIn("## Fixed\n\n- Reject duplicate ZIP destinations (#5)", notes)

    def test_breaking_changes_are_visible_in_notes(self) -> None:
        notes = generate_release_notes(
            {"changes": [{"labels": ["breaking-change"], "summary": "Reject duplicate JSON keys"}]}
        )
        self.assertIn("## Breaking Changes", notes)

    def test_bad_change_lists_are_not_silently_discarded(self) -> None:
        for changes in ({}, [None], [{}]):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    generate_release_notes({"changes": changes})


class JsonInputTests(unittest.TestCase):
    def test_invalid_input_is_rejected_without_echoing_content(self) -> None:
        cases = [
            b"\xff",
            b'{"api_token":"synthetic-value",',
            b'{"gate":true,"gate":false}',
            b'{"value":NaN}',
            b"[]",
            b"{" + b" " * MAX_JSON_BYTES + b"}",
            b'{"a":' * 35 + b"0" + b"}" * 35,
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for raw in cases:
                with self.subTest(raw=raw[:30]):
                    path.write_bytes(raw)
                    with self.assertRaises(ValueError) as caught:
                        load_json(path)
                    self.assertNotIn("synthetic-value", str(caught.exception))

    def test_missing_file_has_a_controlled_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                load_json(Path(directory) / "absent.json")


class WorkflowCliValidationTests(unittest.TestCase):
    run_cli = cli_support.MaintainerCliTests.run_cli
    write_json = cli_support.MaintainerCliTests.write_json

    def test_help_lists_maintainer_commands(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("release-readiness", result.stdout)

    def test_all_cli_gate_failures_return_one(self) -> None:
        for field, value in (
            ("ci_status", "failing"),
            ("tests_passed", False),
            ("quality_gate", 1),
            ("security_review", 1),
            ("artifacts_verified", False),
            ("docs_updated", False),
            ("changelog_updated", False),
            ("release_notes_ready", False),
            ("unresolved_blockers", ["pending"]),
            ("version", ""),
            ("api_token", "synthetic-value"),
        ):
            with self.subTest(field=field):
                manifest = ready_manifest()
                manifest[field] = value
                result = self.run_cli(
                    "release-readiness", str(self.write_json(manifest)), "--format", "json"
                )
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertFalse(json.loads(result.stdout)["ready"])
                self.assertNotIn("synthetic-value", result.stdout + result.stderr)

    def test_malformed_inputs_return_two_without_tracebacks(self) -> None:
        for command, payload in (
            ("triage-issue", {"labels": None}),
            ("review-checklist", {"files": [{}]}),
            ("release-readiness", {"unresolved_blockers": None}),
            ("release-notes", {"changes": {}}),
        ):
            with self.subTest(command=command):
                result = self.run_cli(command, str(self.write_json(payload)))
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("Traceback", result.stderr)

    def test_valid_release_cli_passes_and_review_json_has_checklist(self) -> None:
        result = self.run_cli("release-readiness", str(self.write_json(ready_manifest())))
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli(
            "review-checklist",
            str(self.write_json({"files": ["docs/review-guidelines.md"]})),
            "--format",
            "json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("## Security", json.loads(result.stdout)["checklist"])
