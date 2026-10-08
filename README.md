# OSS Release Guard

A small release-archive verification tool for open-source maintainers and downstream packagers. It checks a local archive against an expected SHA-256 digest and inspects archive metadata before an artifact enters a release or packaging workflow.

Version **0.1.0** is an early project. It supports TAR, TAR.GZ, TAR.BZ2, TAR.XZ, and ZIP. The audit command does not extract files or access the network. Python 3.10 or newer is required; the runtime uses the Python standard library.

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

See [CONTRIBUTING.md](CONTRIBUTING.md), the [maintainer workflow](docs/maintainer-workflow.md), and the [impact evidence record](docs/impact.md). The project is MIT-licensed. Adoption, ecosystem impact, and eligibility for any maintainer program have not been established.
