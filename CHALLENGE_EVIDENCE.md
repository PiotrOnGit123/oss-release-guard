# Challenge Evidence

## Repository

- Repository: https://github.com/PiotrOnGit123/oss-release-guard
- Existing repository was used: yes
- Existing release: https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.1.0

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

## Issues

- #5 Triage duplicate ZIP member reports in release notes output: https://github.com/PiotrOnGit123/oss-release-guard/issues/5
- #6 Document private security-report intake fallback: https://github.com/PiotrOnGit123/oss-release-guard/issues/6
- #7 Harden release manifest handling for secret-like keys: https://github.com/PiotrOnGit123/oss-release-guard/issues/7
- #8 Prepare v0.2.0 release checklist and artifact validation: https://github.com/PiotrOnGit123/oss-release-guard/issues/8
- #9 Add regression tests for release readiness gate failures: https://github.com/PiotrOnGit123/oss-release-guard/issues/9
- #10 Improve examples for release notes generator: https://github.com/PiotrOnGit123/oss-release-guard/issues/10
- #11 Auto-classify PRs that touch GitHub templates: https://github.com/PiotrOnGit123/oss-release-guard/issues/11

## Compliance Map

| Challenge requirement | Repository evidence |
| --- | --- |
| Pull request verification | PR template, `docs/review-guidelines.md`, `review-checklist` command, PRs #1-#4 and #12 with descriptions, checklists, labels, and maintainer comments. |
| Issue classification | Issue templates, `.github/labels.yml`, `.github/repository-metadata.json`, `docs/triage-process.md`, `triage-issue` command, issues #5-#11 with labels and maintainer comments. |
| Release management | `CHANGELOG.md`, `docs/release-process.md`, `release-readiness` command, `release-notes` command, existing `v0.1.0` GitHub release, and `v0.2.0` release metadata prepared in PR #4. |
| Security | `SECURITY.md`, security-related issue template, security labels, security-focused issues #6 and #7, CI checks, and security guidance in review and triage docs. |
| Code quality | 40 local tests, CI workflow, `scripts/check_quality.py`, `docs/quality-standards.md`, compile checks, and no runtime dependencies. |
| Maintainer documentation | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `docs/maintainer-responsibilities.md`, `docs/architecture.md`, triage/review/release/quality docs. |

## Run Instructions

```sh
python -m pip install .
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
- `python -m unittest discover -s tests -v`: passed, 40 tests
- CLI smoke checks for maintainer workflow examples: passed

## Assumptions And Notes

- The repository was not deleted or recreated.
- No additional GitHub accounts were used.
- No fake identities, signatures, or contributors were created.
- The authenticated tools could create files, branches, pull requests, issues, comments, labels on issues/PRs, and merges.
- A persistent workflow that would automatically mutate labels, milestones, and releases with `GITHUB_TOKEN` was not added because that would be broader write automation than necessary without explicit approval.
- Live GitHub milestones and a new `v0.2.0` GitHub release were therefore not force-created by automation. The existing `v0.1.0` release remains the real GitHub release, and `.github/repository-metadata.json` records the intended `v0.2.0` release and milestone metadata for explicit maintainer publication.
