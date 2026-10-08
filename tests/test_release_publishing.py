"""Verify publication boundaries without credentials or external writes."""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import publish_release as publisher

SHA = "a" * 40
URL = "https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.2.0"
RUN = "https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/123"


class PublicationTests(unittest.TestCase):
    def plan(self) -> dict:
        return {
            "release": {
                "tag_name": "v0.2.0",
                "name": "v0.2.0",
                "body": "Synthetic notes",
                "prerelease": True,
                "tracking_issue": 8,
            }
        }

    def test_existing_tag_is_never_moved_or_followed_by_metadata_writes(self) -> None:
        with patch.object(
            publisher,
            "github_request",
            return_value={"object": {"type": "commit", "sha": "b" * 40}},
        ) as request:
            with self.assertRaisesRegex(ValueError, "will not be moved"):
                publisher.publish(self.plan(), SHA, RUN)
            self.assertEqual(request.call_count, 1)

    def test_published_release_is_not_replaced_and_tracking_can_complete(self) -> None:
        calls = []

        def request(method, path, payload=None, **kwargs):
            calls.append((method, path, payload, kwargs))
            if path.startswith("/git/ref/"):
                return {"object": {"type": "commit", "sha": SHA}}
            if path.startswith("/releases/tags/"):
                return {"id": 1, "draft": False, "html_url": URL}
            if path == "/issues/8":
                return {"state": "open"}
            return {}

        with (
            patch.object(publisher, "github_request", side_effect=request),
            patch.object(publisher, "sync_metadata", return_value={"v0.2.0": {"number": 2}}),
        ):
            self.assertEqual(publisher.publish(self.plan(), SHA, RUN), URL)
        self.assertFalse(
            any(path.startswith("/releases/") and method != "GET" for method, path, _, _ in calls)
        )
        self.assertIn(
            ("PATCH", "/issues/8", {"state": "closed", "state_reason": "completed"}, {}), calls
        )
        self.assertIn(("PATCH", "/milestones/2", {"state": "closed"}, {}), calls)

    def test_incomplete_draft_assets_cannot_be_published(self) -> None:
        calls = []

        def request(method, path, payload=None, **kwargs):
            calls.append((method, path))
            if path.startswith("/git/ref/"):
                return {"object": {"type": "commit", "sha": SHA}}
            return {"id": 1, "draft": True, "html_url": URL}

        with (
            tempfile.TemporaryDirectory() as directory,
            patch.object(publisher, "ROOT", Path(directory)),
            patch.object(publisher, "github_request", side_effect=request),
            patch.object(publisher, "sync_metadata", return_value={"v0.2.0": {"number": 2}}),
        ):
            with self.assertRaises(ValueError):
                publisher.publish(self.plan(), SHA, RUN)
        self.assertNotIn(("PATCH", "/releases/1"), calls)

    def test_draft_uploads_all_four_assets_before_publication(self) -> None:
        calls = []

        def request(method, path, payload=None, **kwargs):
            calls.append((method, path, payload, kwargs))
            if path.startswith("/git/ref/"):
                return {"object": {"type": "commit", "sha": SHA}}
            if path.startswith("/releases/tags/"):
                return {"id": 1, "draft": True, "assets": [], "html_url": URL}
            if path == "/releases/1":
                return {"id": 1, "draft": False, "html_url": URL}
            if path == "/issues/8":
                return {"state": "closed"}
            return {}

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "dist").mkdir()
            for name in (
                "test-0.2.0.whl",
                "test-0.2.0.tar.gz",
                "SHA256SUMS",
                "artifact-audit.json",
            ):
                (root / "dist" / name).write_bytes(b"synthetic fixture")
            with (
                patch.object(publisher, "ROOT", root),
                patch.object(publisher, "github_request", side_effect=request),
                patch.object(publisher, "sync_metadata", return_value={"v0.2.0": {"number": 2}}),
            ):
                publisher.publish(self.plan(), SHA, RUN)
        uploads = [i for i, call in enumerate(calls) if call[3].get("upload")]
        publish_index = next(i for i, call in enumerate(calls) if call[1] == "/releases/1")
        self.assertEqual(len(uploads), 4)
        self.assertTrue(all(i < publish_index for i in uploads))

    def test_permission_failure_does_not_disclose_credential(self) -> None:
        error = HTTPError("https://api.github.com", 403, "denied", {}, None)
        with (
            patch.dict(os.environ, {"GH_TOKEN": "synthetic-not-a-credential"}),
            patch.object(publisher, "urlopen", side_effect=error),
        ):
            with self.assertRaises(RuntimeError) as caught:
                publisher.github_request("POST", "/releases", {})
        self.assertNotIn("synthetic-not-a-credential", str(caught.exception))
        self.assertIn("403", str(caught.exception))

    def test_missing_resource_only_returns_none_when_requested(self) -> None:
        error = HTTPError("https://api.github.com", 404, "missing", {}, None)
        with (
            patch.dict(os.environ, {"GH_TOKEN": "synthetic-not-a-credential"}),
            patch.object(publisher, "urlopen", side_effect=error),
        ):
            self.assertIsNone(
                publisher.github_request("GET", "/releases/tags/absent", missing_ok=True)
            )
            with self.assertRaises(RuntimeError):
                publisher.github_request("GET", "/releases/tags/absent")

    def test_publication_from_a_pull_request_branch_is_rejected(self) -> None:
        with (
            patch.dict(
                os.environ,
                {"GITHUB_REPOSITORY": publisher.REPOSITORY, "GITHUB_REF": "refs/heads/feature"},
                clear=True,
            ),
            patch.object(publisher, "release_plan", return_value=self.plan()),
            patch.object(publisher, "github_request") as request,
            patch("sys.argv", ["publish_release.py"]),
        ):
            with self.assertRaises(ValueError):
                publisher.main()
            request.assert_not_called()

    def test_plan_requires_no_credentials_or_network(self) -> None:
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("sys.argv", ["publish_release.py", "--plan"]),
            patch.object(publisher, "github_request") as request,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(publisher.main(), 0)
            request.assert_not_called()

    def test_tag_and_package_version_must_match(self) -> None:
        with patch.object(publisher, "__version__", "9.9.9"):
            with self.assertRaises(ValueError):
                publisher.release_plan()
