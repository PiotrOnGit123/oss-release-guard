"""Publish verified assets and release metadata to this repository only."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = "PiotrOnGit123/oss-release-guard"
sys.path.insert(0, str(ROOT))

from oss_release_guard import __version__  # noqa: E402


def release_plan() -> dict:
    metadata = json.loads((ROOT / ".github/repository-metadata.json").read_text(encoding="utf-8"))
    release = metadata["release"]
    if release["tag_name"] != f"v{__version__}":
        raise ValueError("Release tag and package version must match.")
    notes = ROOT / release["notes_file"]
    if not notes.resolve().is_relative_to((ROOT / "docs/releases").resolve()):
        raise ValueError("Release notes must be inside docs/releases.")
    release["body"] = notes.read_text(encoding="utf-8")
    return metadata


def github_request(
    method: str, path: str, payload=None, *, missing_ok: bool = False, upload: bool = False
):
    # The host and repository are fixed; the credential is supplied only by the publish job.
    host = "uploads.github.com" if upload else "api.github.com"
    url = f"https://{host}/repos/{REPOSITORY}{path}"
    data = (
        payload if upload else json.dumps(payload).encode("utf-8") if payload is not None else None
    )
    request = Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/octet-stream" if upload else "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        error.close()
        if error.code == 404 and missing_ok:
            return None
        raise RuntimeError(f"GitHub {method} request failed with HTTP {error.code}.") from None


def sync_metadata(plan: dict) -> dict[str, dict]:
    labels = {item["name"] for item in github_request("GET", "/labels?per_page=100")}
    for label in plan["labels"]:
        name = label["name"]
        path = "/labels/" + quote(name, safe="") if name in labels else "/labels"
        github_request("PATCH" if name in labels else "POST", path, label)
    milestones = {
        item["title"]: item for item in github_request("GET", "/milestones?state=all&per_page=100")
    }
    for desired in plan["milestones"]:
        title = desired["title"]
        initial = {**desired, "state": "open"} if title == plan["release"]["tag_name"] else desired
        if title not in milestones:
            milestones[title] = github_request("POST", "/milestones", initial)
    for title, numbers in plan["milestone_items"].items():
        for number in numbers:
            github_request("PATCH", f"/issues/{number}", {"milestone": milestones[title]["number"]})
    return milestones


def publish(plan: dict, sha: str, run_url: str) -> str:
    release_spec = plan["release"]
    tag = release_spec["tag_name"]
    tag_ref = github_request("GET", "/git/ref/tags/" + quote(tag, safe=""), missing_ok=True)
    if tag_ref and (tag_ref["object"]["type"] != "commit" or tag_ref["object"]["sha"] != sha):
        raise ValueError("Existing release tag points elsewhere; it will not be moved.")
    milestones = sync_metadata(plan)
    if not tag_ref:
        github_request("POST", "/git/refs", {"ref": "refs/tags/" + tag, "sha": sha})
    release = github_request("GET", "/releases/tags/" + quote(tag, safe=""), missing_ok=True)
    if release is None:
        body = (
            release_spec["body"]
            + f"\n\nVerified publication run: [{run_url}]({run_url}).\nSource commit: `{sha}`.\n"
        )
        release = github_request(
            "POST",
            "/releases",
            {
                "tag_name": tag,
                "target_commitish": sha,
                "name": release_spec["name"],
                "body": body,
                "draft": True,
                "prerelease": release_spec["prerelease"],
            },
        )
    if release["draft"]:
        dist = ROOT / "dist"
        assets = sorted(
            [
                *dist.glob("*.whl"),
                *dist.glob("*.tar.gz"),
                dist / "SHA256SUMS",
                dist / "artifact-audit.json",
            ]
        )
        if len(assets) != 4 or not all(path.is_file() for path in assets):
            raise ValueError("Exactly four verified release assets are required.")
        existing = {item["name"]: item for item in release.get("assets", [])}
        for path in assets:
            content = path.read_bytes()
            if path.name in existing:
                if (
                    existing[path.name].get("digest")
                    != "sha256:" + hashlib.sha256(content).hexdigest()
                ):
                    raise ValueError("An existing asset differs; it will not be overwritten.")
                continue
            github_request(
                "POST",
                f"/releases/{release['id']}/assets?name=" + quote(path.name, safe=""),
                content,
                upload=True,
            )
        release = github_request("PATCH", f"/releases/{release['id']}", {"draft": False})
    issue_number = release_spec["tracking_issue"]
    issue = github_request("GET", f"/issues/{issue_number}")
    if issue["state"] == "open":
        github_request(
            "POST",
            f"/issues/{issue_number}/comments",
            {
                "body": f"Verified release published: {release['html_url']}\n\nCI, package validation, installed-wheel smoke checks, checksums, and archive audit completed in {run_url}. The milestone records the completed release work."
            },
        )
        github_request(
            "PATCH", f"/issues/{issue_number}", {"state": "closed", "state_reason": "completed"}
        )
    github_request("PATCH", f"/milestones/{milestones[tag]['number']}", {"state": "closed"})
    return release["html_url"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan", action="store_true", help="Show metadata without network access or credentials"
    )
    args = parser.parse_args()
    plan = release_plan()
    if args.plan:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0
    if (
        os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
        or os.environ.get("GITHUB_REF") != "refs/heads/main"
    ):
        raise ValueError("Publication is restricted to this repository's main branch.")
    sha = os.environ.get("GITHUB_SHA", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha) or not run_id.isdigit():
        raise ValueError("A valid workflow commit and run ID are required.")
    run_url = f"https://github.com/{REPOSITORY}/actions/runs/{run_id}"
    print(publish(plan, sha, run_url))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, KeyError) as error:
        print(f"Release publication stopped: {error}", file=sys.stderr)
        raise SystemExit(1) from None
