# OSS Release Guard

A small maintainer toolkit for open-source release work. It helps maintainers check release archive readiness, classify issues and pull requests, generate review checklists, and prepare release notes before a project ships.

Version **0.2.0** is an early project. The archive audit supports TAR, TAR.GZ, TAR.BZ2, TAR.XZ, and ZIP. The audit command does not extract files or access the network. Python 3.10 or newer is required; the runtime uses the Python standard library.

## Get started

```sh
git clone https://github.com/PiotrOnGit123/oss-release-guard.git
cd oss-release-guard
python -m pip install .
python -m oss_release_guard artifact.tar.gz --sha256 EXPECTED_SHA256
```

Replace `EXPECTED_SHA256` with the 64-character digest obtained through a trusted, independently authenticated release process. A digest calculated from the same untrusted download only establishes consistency; it does not authenticate the publisher.

For a machine-readable report and explicit limits:

```sh
python -m oss_release_guard artifact.tar.gz --sha256 EXPECTED_SHA256 --format json --max-members 100000 --max-total-size 1073741824
```

| Exit code | Meaning |
| --- | --- |
| `0` | The supported checks passed. |
| `1` | Digest mismatch, rejected archive metadata, or exceeded limits. |
| `2` | Input error, unsupported archive, or malformed format. |

## What it checks

The tool compares SHA-256 digests and applies a conservative policy to member paths, entry types, duplicates, member counts, and declared total size. Links are rejected, including legitimate symlinks and hardlinks. Treat that outcome as a policy incompatibility requiring review, rather than evidence that a release is malicious.

Limits concern archive metadata. They are not a decompression sandbox or a guarantee against excessive CPU or memory use. A passing audit does not verify signatures, scan malware, validate source code, establish reproducible builds, or prove an archive safe to extract. Run audits of hostile inputs in an environment with external resource limits. See [SECURITY.md](SECURITY.md).

## Why this workflow matters

Maintainers can use the report as one pre-release check; packagers can use it before accepting a source artifact. For a concrete compatibility example, PostgreSQL publishes a [PostgreSQL 18.0 source archive and SHA-256 files](https://www.postgresql.org/ftp/source/v18.0/). That historical release is a test fixture, not a production-version recommendation. OpenSSL publishes [release checksums and separate signature information](https://openssl-library.org/source/); verify signatures through its own documented process.

These projects illustrate relevant release practices. This repository has no affiliation with them and does not imply that their maintainers use this tool.

The [validation record](docs/validation.md) includes a successful check of the official PostgreSQL 18.0 artifact and a saved JSON report.

## Maintainer workflow helpers

The same CLI also supports maintainer operations around issues, pull requests, and releases:

```sh
oss-release-guard triage-issue examples/issue-security.json --format json
oss-release-guard review-checklist examples/pr-review.json
oss-release-guard release-readiness examples/release-manifest.json
oss-release-guard release-notes examples/release-changes.json
```

These commands are deterministic helpers, not bots. A maintainer still makes the final call, but the output gives a consistent starting point for labels, review focus, release gates, and release notes.

| Workflow | Command | Output |
| --- | --- | --- |
| Issue triage | `triage-issue` | Suggested labels, priority, risk, routing, and rationale. |
| Pull request review | `review-checklist` | Markdown checklist plus suggested PR labels in JSON mode. |
| Release management | `release-readiness` | Required gate report with a failing exit code when not ready. |
| Release notes | `release-notes` | Grouped Markdown notes from structured change data. |

## Quality gates

CI runs the test suite on Linux and Windows, compiles Python sources, executes a repository quality gate, and exercises the maintainer workflow commands. The quality gate checks required maintenance documents, text hygiene, dependency policy, and the security policy:

```sh
python -m compileall oss_release_guard tests scripts
python scripts/check_quality.py
python -m unittest discover -s tests -v
```

## Try a local demonstration

```sh
python examples/make_demo.py
```

This creates `demo/demo-release.tar.gz` and prints a SHA-256 digest. Pass the printed digest to the audit command:

```sh
python -m oss_release_guard demo/demo-release.tar.gz --sha256 PRINTED_DIGEST --format json
```

This synthetic example demonstrates the command; the digest generated alongside the artifact is not independent evidence of publisher authenticity.

## Contribute

```sh
python -m unittest discover -s tests -v
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [triage process](docs/triage-process.md), [review guidelines](docs/review-guidelines.md), [release process](docs/release-process.md), [quality standards](docs/quality-standards.md), [maintainer responsibilities](docs/maintainer-responsibilities.md), and [architecture](docs/architecture.md). The project is MIT-licensed. Adoption, ecosystem impact, and eligibility for any maintainer program have not been established.
