# Challenge Evidence

## Repository

- Repository: https://github.com/PiotrOnGit123/oss-release-guard
- Existing repository was used: yes
- Existing release: https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.1.0
- Current release publication target: https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.2.0
- Verified release workflow: `.github/workflows/release.yml`; issue #8 is completed only after publication succeeds.

## Existing Repository Assessment

`oss-release-guard` already had a sensible base: a Python CLI for offline release archive verification, tests, CI, documentation, MIT license, and an existing `v0.1.0` GitHub release. The name fits the challenge because it connects open-source maintenance, release management, quality gates, and security checks.

The repository was expanded instead of deleted or recreated. No transfer was needed. No additional GitHub accounts were used, and no contributor identities were simulated. Collaboration is represented through real issues, pull requests, labels, review-style comments, templates, and maintainer documentation created from the available authenticated account.

## Added Or Improved

- Maintainer workflow CLI commands:
  - `triage-issue`
  - `review-checklist`
  - `release-readiness`
  - `release-notes`
- Tests for maintainer workflow behavior and CLI output.
- Example JSON inputs for issue triage, PR review, release readiness, and release notes.
- CI quality gates using source compilation, repository quality policy checks, tests, installed CLI verification, and maintainer workflow smoke tests.
- Documentation for triage, reviews, release process, quality standards, maintainer responsibilities, and architecture.
- GitHub issue templates for bugs, features, documentation tasks, and security-related reports.
- Pull request template with review and security checklist.
- Code of conduct, expanded contributing guide, expanded security policy, changelog, canonical label files, and static repository metadata.

## Pull Requests

- #1 Add maintainer workflow CLI helpers: https://github.com/PiotrOnGit123/oss-release-guard/pull/1
- #2 Document maintainer processes and GitHub templates: https://github.com/PiotrOnGit123/oss-release-guard/pull/2
- #3 Add CI quality gates: https://github.com/PiotrOnGit123/oss-release-guard/pull/3
- #4 Prepare v0.2.0 release metadata: https://github.com/PiotrOnGit123/oss-release-guard/pull/4
- #12 Add challenge evidence summary: https://github.com/PiotrOnGit123/oss-release-guard/pull/12
- #13 Fix Python 3.10 quality gate compatibility: https://github.com/PiotrOnGit123/oss-release-guard/pull/13
- #15 Harden release decisions and enforce lint, security and package gates: https://github.com/PiotrOnGit123/oss-release-guard/pull/15
- #18 Publish verified v0.2.0 assets and complete GitHub release tracking: https://github.com/PiotrOnGit123/oss-release-guard/pull/18

Real Dependabot proposals #16 (setup-python) and #17 (checkout) received maintainer reviews and are deferred to the next milestone. They are automated contributions, not independent human reviews or invented accounts.

## Issues

- #5 Triage duplicate ZIP member reports in release notes output: https://github.com/PiotrOnGit123/oss-release-guard/issues/5
- #6 Document private security-report intake fallback: https://github.com/PiotrOnGit123/oss-release-guard/issues/6
- #7 Harden release manifest handling for secret-like keys: https://github.com/PiotrOnGit123/oss-release-guard/issues/7
- #8 Prepare v0.2.0 release checklist and artifact validation: https://github.com/PiotrOnGit123/oss-release-guard/issues/8
- #9 Add regression tests for release readiness gate failures: https://github.com/PiotrOnGit123/oss-release-guard/issues/9
- #10 Improve examples for release notes generator: https://github.com/PiotrOnGit123/oss-release-guard/issues/10
- #11 Auto-classify PRs that touch GitHub templates: https://github.com/PiotrOnGit123/oss-release-guard/issues/11
- #14 Reject malformed release gates and support GitHub API records: https://github.com/PiotrOnGit123/oss-release-guard/issues/14

PR #15 closes #5, #6, #7, #9, #10, #11, and #14 with reproducible fixes/tests and maintainer triage comments. Issue #8 tracks the actual publication separately.

## Compliance Map

| Challenge requirement | Repository evidence |
| --- | --- |
| Pull request verification | PR template, review guidelines, review-checklist command, PR descriptions/checklists, self-review submissions on #15/#18, a resolved inline finding on #15, successful CI, and actual Dependabot reviews on #16/#17. |
| Issue classification | Issue templates, `.github/labels.yml`, `.github/repository-metadata.json`, `docs/triage-process.md`, `triage-issue` command, issues #5-#11 with labels and maintainer comments. |
| Release management | Changelog, release docs, readiness/notes commands, v0.1.0 release, and verified v0.2.0 publication workflow with wheel/source assets, checksums, archive reports, and live milestone synchronization. Publication completion is tracked in #8. |
| Security | `SECURITY.md`, security-related issue template, security labels, security-focused issues #6 and #7, CI checks, and security guidance in review and triage docs. |
| Code quality | 73 tests, 92% branch-aware runtime coverage at #15, Ruff lint/format, Bandit, pip-audit, six platform/Python combinations, an 85% coverage gate, example consistency, package validation, Dependabot, and no runtime dependencies. |
| Maintainer documentation | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `docs/maintainer-responsibilities.md`, `docs/architecture.md`, triage/review/release/quality docs. |

## Run Instructions

```sh
python -m pip install -r requirements-dev.txt .
ruff check .
ruff format --check .
bandit -r oss_release_guard -ll
pip-audit -r requirements-dev.txt --strict
python -m compileall oss_release_guard tests scripts
python scripts/check_quality.py
python -m unittest discover -s tests -v
oss-release-guard triage-issue examples/issue-security.json --format json
oss-release-guard review-checklist examples/pr-review.json
oss-release-guard release-readiness examples/release-manifest.json
oss-release-guard release-notes examples/release-changes.json
```

## Local Validation Result

Validated locally on 2026-10-08:

- `python -m compileall oss_release_guard tests scripts`: passed
- `python scripts/check_quality.py`: passed
- `python -m unittest discover -s tests -v`: passed, 73 tests
- CLI smoke checks for maintainer workflow examples: passed
- The Python 3.10 matrix uses the development-only `tomli` parser rather than an ad hoc TOML fallback.
- Ruff lint/format, Bandit, pip-audit, example outputs, distribution build, strict Twine checks, and wheel/source archive audits passed.
- PR #15 CI passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37842467178

## Assumptions And Notes

- The repository was not deleted or recreated.
- No additional GitHub accounts were used.
- No fake identities, signatures, or contributors were created.
- The authenticated tools could create files, branches, pull requests, issues, comments, labels on issues/PRs, and merges.
- The authorized release workflow uses a temporary job token for contents/issues writes only after CI and artifact validation. No token is stored in the repository, and ordinary CI is read-only.
- The workflow creates the actual version milestones and synchronizes canonical labels; the final publication run and issue #8 provide evidence of completion.
- Repository description/topics administration is not exposed by the current connector. Desired topics are recorded in `.github/repository-metadata.json`, but they are not claimed to exist as live GitHub topics.
- This is an early functional project. External adoption, independent human review, and winning the challenge have not been established.
