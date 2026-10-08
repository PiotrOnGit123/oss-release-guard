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

## Release notes

Structured changes can be grouped into Markdown:

```sh
oss-release-guard release-notes examples/release-changes.json
```

Release notes should mention user-visible behavior, quality evidence, security handling, and known limitations. Avoid publishing exploit details before coordinated disclosure.
