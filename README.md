# OSS Release Guard

[![Tests](https://github.com/PiotrOnGit123/oss-release-guard/actions/workflows/ci.yml/badge.svg)](https://github.com/PiotrOnGit123/oss-release-guard/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/PiotrOnGit123/oss-release-guard?include_prereleases)](https://github.com/PiotrOnGit123/oss-release-guard/releases)

A small maintainer toolkit for open-source release work. It helps maintainers check release archive readiness, classify issues and pull requests, generate review checklists, and prepare release notes before a project ships.

Version **0.2.1** is an early pre-release. Its [published patch release](https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.2.1) includes a wheel, source distribution, checksums and archive reports from the [verified publication run](https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37979848886). The previous [v0.2.0 release](https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.2.0) remains immutable. The archive audit supports TAR, TAR.GZ, TAR.BZ2, TAR.XZ, and ZIP. The audit command does not extract files or access the network. Python 3.10 or newer is required; the runtime uses the Python standard library.

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

They accept simple JSON records and GitHub API label (`{"name": "security"}`) and changed-file (`{"filename": "SECURITY.md"}`) objects. The readiness manifest records maintainer declarations; it does not query live CI or authenticate the evidence supplied by a caller. Missing or invalid versions, failed gates, unresolved blockers, and secret-like fields prevent a ready result. Invalid input exits `2`; a valid but blocked release exits `1`.

The JSON exponent-overflow fix is part of version 0.2.1 and is not in the already published v0.2.0 assets; see [issue #23](https://github.com/PiotrOnGit123/oss-release-guard/issues/23) and the [changelog](CHANGELOG.md). Release tags and assets are not retroactively replaced.

Example triage result:

```json
{
  "labels": ["release", "security", "triage"],
  "priority": "P0",
  "risk": "high",
  "routing": "security-maintainers"
}
```

Full reproducible outputs are in [examples/expected](examples/expected). Release notes separate security, fixes, documentation, quality, and breaking changes. Input validation changes are described in [CHANGELOG.md](CHANGELOG.md).

| Workflow | Command | Output |
| --- | --- | --- |
| Issue triage | `triage-issue` | Suggested labels, priority, risk, routing, and rationale. |
| Pull request review | `review-checklist` | Markdown checklist plus suggested PR labels in JSON mode. |
| Release management | `release-readiness` | Required gate report with a failing exit code when not ready. |
| Release notes | `release-notes` | Grouped Markdown notes from structured change data. |

## Quality gates

CI runs tests on Linux and Windows with Python 3.10, 3.12, and 3.14. A separate job enforces Ruff linting/formatting, Bandit security checks, dependency auditing, an 85% minimum branch-aware coverage score, example consistency, and wheel/source distribution validation. The runtime has no third-party dependencies; development tools and the build backend are pinned and audited.

```sh
python -m pip install -r requirements-dev.txt .
python -m compileall oss_release_guard tests scripts
python scripts/check_quality.py
ruff check .
ruff format --check .
bandit -r oss_release_guard -ll
pip-audit -r requirements-dev.txt --strict
python -m unittest discover -s tests -v
python scripts/check_examples.py
```

Run `coverage run -m unittest discover -s tests`, then `coverage combine` and `coverage report` for the coverage gate. Use `python -m build`, `twine check --strict dist/*.whl dist/*.tar.gz`, and `python scripts/verify_dist.py` to validate release artifacts. [Dependabot](.github/dependabot.yml) proposes updates to development tools and pinned GitHub Actions.

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

See [CONTRIBUTING.md](CONTRIBUTING.md), [triage process](docs/triage-process.md), [review guidelines](docs/review-guidelines.md), [release process](docs/release-process.md), [quality standards](docs/quality-standards.md), [maintainer responsibilities](docs/maintainer-responsibilities.md), and [architecture](docs/architecture.md). The project is MIT-licensed and maintained through public [issues](https://github.com/PiotrOnGit123/oss-release-guard/issues), [pull requests](https://github.com/PiotrOnGit123/oss-release-guard/pulls?q=is%3Apr), and [releases](https://github.com/PiotrOnGit123/oss-release-guard/releases). External adoption and production use have not been measured.

The [maintenance evidence](CHALLENGE_EVIDENCE.md) maps the working commands, reviewed changes, issue triage, quality results, and published release to the challenge requirements, including the remaining GitHub About metadata step.
