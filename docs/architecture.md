# Architecture

OSS Release Guard is a small Python package with two main responsibility areas:

- `oss_release_guard.core` audits local release archives.
- `oss_release_guard.maintainer` supports issue triage, pull request review, release readiness, and release notes.

## Archive audit path

The archive audit computes SHA-256 in chunks, compares it to a caller-supplied expected digest, and inspects TAR or ZIP metadata without extracting files. The audit records findings in a deterministic JSON-compatible report.

Important boundaries:

- The tool does not authenticate the publisher.
- The tool does not verify signatures.
- The tool does not scan malware.
- The tool does not guarantee that an archive is safe to extract.

## Maintainer workflow path

Maintainer helpers accept JSON objects and return deterministic text, Markdown, or JSON. They do not call GitHub APIs, change labels, or make release decisions automatically. This keeps the CLI safe for local use while still modeling real maintainer work.

## CLI structure

`oss_release_guard.__main__` preserves the original archive audit invocation:

```sh
oss-release-guard artifact.tar.gz --sha256 EXPECTED_SHA256
```

It also dispatches explicit maintainer commands:

```sh
oss-release-guard triage-issue input.json
oss-release-guard review-checklist input.json
oss-release-guard release-readiness input.json
oss-release-guard release-notes input.json
```

## Test strategy

Tests generate archives dynamically, so binary fixtures are not required. Maintainer workflow tests use small JSON objects to exercise classification, checklist generation, readiness gates, release notes, and CLI behavior.
