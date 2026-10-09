# Security policy

This is an early archive-verification tool. Only the current development version is reviewed for fixes; there is no promised response time or long-term support schedule.

Maintainers treat vulnerability handling as release-critical work. A confirmed vulnerability should receive the `security` label, private coordination when needed, a regression test when safe to publish, and release notes that avoid exploit details until disclosure is appropriate.

## Report a vulnerability

If GitHub offers **Report a vulnerability** under this repository's Security tab, use that private advisory channel. Availability depends on repository settings. If it is unavailable, open an issue requesting a private reporting channel without publishing exploit details, sensitive archives, or confidential information.

A safe public placeholder is: "I have a potentially sensitive report affecting the current release. Please provide a private reporting channel." Wait for a confirmed private destination before sending a reproduction. If no private channel is available, retain the details locally; a public issue is not a substitute for private disclosure. The [security-related issue form](.github/ISSUE_TEMPLATE/security_related.yml) is only for placeholders and non-sensitive hardening tasks.

Include the affected version, a minimal reproduction, expected policy behavior, and potential impact when a private channel is available.

Do not publish exploit archives, private source releases, credentials, tokens, or personal data in a public issue or pull request. If a public placeholder is needed, describe the class of risk and ask maintainers to open a private channel.

## Maintainer response

1. Acknowledge the report and confirm whether the details are private or public.
2. Reproduce with a minimal synthetic archive or JSON workflow fixture.
3. Assign severity and decide whether the fix blocks the next release.
4. Patch with tests and documentation.
5. Publish release notes once the fix is available, omitting sensitive exploit details when appropriate.

## Trust boundaries

Maintainer JSON inputs are limited to 1 MiB and 32 nesting levels. Invalid UTF-8, duplicate object keys, and non-finite numbers are rejected. The release gate counts secret-like field names, including nested names, and blocks the release without echoing those names or values. This is a conservative field-name rule, not a complete secret scanner: values under unrelated names can still contain sensitive information. Sanitize inputs before committing or sharing them. Readiness results reflect caller declarations rather than independently verified live CI state.

The published v0.2.0 JSON parser rejects literal `NaN` and `Infinity`, but exponent overflow such as `1e309` can still become a non-finite float. Version 0.2.1 fixes overflow as well; see [issue #23](https://github.com/PiotrOnGit123/oss-release-guard/issues/23), the [changelog](CHANGELOG.md), and [publication tracking #24](https://github.com/PiotrOnGit123/oss-release-guard/issues/24). Existing v0.2.0 assets have not been silently replaced. This is a confirmed input-validation defect, not an established code-execution or credential-disclosure vulnerability.

CI runs Bandit on the runtime Python package and audits pinned development dependencies with pip-audit. Passing those checks does not establish the absence of vulnerabilities.

The audit reads local files and parses archive metadata. It does not extract members or fetch an expected digest. Obtain the digest independently through a trusted release process. The parser and Python runtime remain part of the attack surface.

ZIP checks compare local member names with central-directory names. They do not decompress payloads or verify payload CRCs. TAR scanning can decompress data while advancing to subsequent metadata headers. The Python ZIP parser allocates its central directory before the member-count limit is applied. Audits assume the local artifact is not modified while the command is running.

Declared-size and member-count limits do not constrain all decompression work. Process hostile archives with external CPU, memory, and time limits. SHA-256 agreement and accepted metadata do not establish publisher identity, signature validity, malware absence, safe extraction, or source-code security.
