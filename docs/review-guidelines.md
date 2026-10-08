# Review Guidelines

Pull request review protects users, downstream packagers, and maintainers. A review is not only a style pass; it checks behavior, tests, security, documentation, and release impact.

## Review checklist

- Confirm the PR has a clear problem statement and scoped implementation.
- Check whether the change affects CLI output, JSON fields, exit codes, archive policy, or release process.
- Review tests for success, failure, and boundary cases.
- Run local quality gates when the change touches code or repository policy.
- Check documentation and examples for consistency.
- Confirm security-sensitive changes avoid public exploit details.
- Confirm release-facing changes update `CHANGELOG.md` or explain why not.

## Generated checklist

Use the helper for a consistent starting point:

```sh
oss-release-guard review-checklist examples/pr-review.json
```

The checklist includes scope, quality, security, and reviewer focus areas. Maintainers should add any project-specific context before approving.

## Merge expectations

A PR should normally pass CI, include tests for behavior changes, and have maintainer review before merge. High-risk, security, release, or breaking-change PRs should receive extra scrutiny and clear release notes.
