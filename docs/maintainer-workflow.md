# Maintainer workflow

This is a suggested human workflow. Labels, approvals, and downstream integrations are not automated by the tool.

## Review pull requests

1. Reproduce the reported behavior with a minimal archive.
2. Review path handling, entry types, resource use, and failure behavior.
3. Run the test suite and check supported Python versions.
4. Explain compatibility changes in documentation before merging.

## Triage issues

Suggested labels are `bug`, `archive-compatibility`, `security`, `documentation`, and `enhancement`. A link-containing upstream archive may be an expected policy rejection. Keep compatibility reports distinct from vulnerabilities; route sensitive details through the security policy.

## Prepare a release or downstream package

1. Obtain the artifact and independently trusted expected digest.
2. Run OSS Release Guard with limits appropriate to that project.
3. Investigate every rejected check; retain the JSON report with the release review.
4. Verify upstream signatures separately when provided.
5. Complete source review, build tests, and the project's usual release approvals.

A successful audit is one recorded check. It does not replace the remaining release process.
