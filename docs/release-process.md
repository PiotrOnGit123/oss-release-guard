# Release Process

Release management is treated as a maintainer workflow, not just a tag. The release manager verifies code, tests, documentation, security posture, and notes before publishing.

## Release checklist

1. Create or update a milestone for the target version.
2. Confirm all release-blocking issues and pull requests are closed or explicitly deferred.
3. Run the local quality gate and full test suite.
4. Generate or update release notes from merged changes.
5. Verify release artifacts with `oss-release-guard` when archive artifacts are involved.
6. Update `CHANGELOG.md`.
7. Publish a GitHub release with test, quality, and security evidence.
8. Close the milestone or document remaining follow-up work.

## Readiness manifest

`examples/release-manifest.json` records the gates expected before release:

```sh
oss-release-guard release-readiness examples/release-manifest.json
```

The command exits `0` only when every required gate passes. Failed gates are suitable for release-preparation issues.

The manifest is a maintainer declaration, not live CI evidence. The version must be present, confirmations must be explicit booleans or documented status strings, and secret-like fields are rejected without echoing their contents. A valid but blocked manifest exits `1`; malformed input exits `2`.

## Verified publication

The [Verified Release workflow](../.github/workflows/release.yml) is run manually from GitHub Actions after the release metadata and notes are reviewed on `main`. Its initial v0.2.0 publication is triggered by the explicitly marked merge that installs the workflow. Ordinary PRs and pushes cannot publish a release.

1. Review `.github/repository-metadata.json`, the package version, changelog, and `docs/releases/vVERSION.md`. Preview the metadata with `python scripts/publish_release.py --plan`; this mode needs neither credentials nor network access.
2. The workflow reruns the full Linux/Windows matrix and quality/security gates.
3. It builds wheel/source distributions, checks package metadata, audits archive policy, and generates `SHA256SUMS` and `artifact-audit.json`.
4. It installs and exercises the wheel outside the source checkout.
5. Only its final publication step receives the job's temporary GitHub token. That job has `contents: write`, `issues: write`, and `pull-requests: write` (required to assign PR milestones); normal CI has read-only permissions and checkout credentials are not retained.
6. The publisher synchronizes canonical labels, creates version milestones, assigns tracked issues/PRs, creates a draft release at the verified commit, uploads the four assets, and publishes it. It completes the release tracking issue and closes the milestone.

Existing tags are never moved and existing assets are never overwritten. Repeating the same publication repairs unfinished milestone tracking without replacing an already published release. Repository description/topics and security settings require owner administration and are not changed by the release token. Uploaded checksums prove consistency, not independent authenticity or a signature.

## Release notes

Structured changes can be grouped into Markdown:

```sh
oss-release-guard release-notes examples/release-changes.json
```

Release notes should mention user-visible behavior, quality evidence, security handling, and known limitations. Avoid publishing exploit details before coordinated disclosure.
