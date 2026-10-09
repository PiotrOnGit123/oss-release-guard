# Challenge Evidence

## Repository

- Repository: https://github.com/PiotrOnGit123/oss-release-guard
- Existing repository was used: yes
- Existing release: https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.1.0
- Published pre-release: https://github.com/PiotrOnGit123/oss-release-guard/releases/tag/v0.2.0
- Successful verified publication: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37894134275
- Immutable release source: `367a2e4551c205254f3ccb3ede22737c180f3620`.
- Closed v0.2.0 milestone: https://github.com/PiotrOnGit123/oss-release-guard/milestone/2
- Open v0.3.0 follow-up milestone: https://github.com/PiotrOnGit123/oss-release-guard/milestone/3

## Existing Repository Assessment

`oss-release-guard` already had a sensible base: a Python CLI for offline release archive verification, tests, CI, documentation, MIT license, and an existing `v0.1.0` GitHub release. The name fits the challenge because it connects open-source maintenance, release management, quality gates, and security checks.

The repository was expanded instead of deleted or recreated. No transfer or additional human account was needed, and no contributor identities were simulated. The single-account maintainer workflow is represented through real issues, pull requests, labels, self-review submissions, templates, and maintainer documentation. Dependabot subsequently opened real dependency proposals; GitHub Actions published the verified release. Neither bot activity nor maintainer self-review is presented as independent human review.

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
- Fail-closed release gates, disclosure-safe manifest handling, bounded JSON parsing, and support for GitHub API records, backed by regression tests.
- Ruff lint/format, Bandit, dependency auditing, coverage enforcement, Dependabot, and wheel/source validation.
- Actual GitHub labels and version milestones, verified publication with four downloadable assets, and a completed release issue.

## Pull Requests

- #1 Add maintainer workflow CLI helpers: https://github.com/PiotrOnGit123/oss-release-guard/pull/1
- #2 Document maintainer processes and GitHub templates: https://github.com/PiotrOnGit123/oss-release-guard/pull/2
- #3 Add CI quality gates: https://github.com/PiotrOnGit123/oss-release-guard/pull/3
- #4 Prepare v0.2.0 release metadata: https://github.com/PiotrOnGit123/oss-release-guard/pull/4
- #12 Add challenge evidence summary: https://github.com/PiotrOnGit123/oss-release-guard/pull/12
- #13 Fix Python 3.10 quality gate compatibility: https://github.com/PiotrOnGit123/oss-release-guard/pull/13
- #15 Harden release decisions and enforce lint, security and package gates: https://github.com/PiotrOnGit123/oss-release-guard/pull/15
- #18 Publish verified v0.2.0 assets and complete GitHub release tracking: https://github.com/PiotrOnGit123/oss-release-guard/pull/18
- #19 Fix label update payloads and diagnose release API permissions: https://github.com/PiotrOnGit123/oss-release-guard/pull/19
- #20 Allow the gated publisher to assign PR milestones: https://github.com/PiotrOnGit123/oss-release-guard/pull/20

Real Dependabot proposals [#16 (setup-python)](https://github.com/PiotrOnGit123/oss-release-guard/pull/16) and [#17 (checkout)](https://github.com/PiotrOnGit123/oss-release-guard/pull/17) received maintainer reviews and are deferred to v0.3.0. They are automated contributions, not independent human reviews or invented accounts. Their matching action pins must be reviewed across CI and publication before merging.

## Issues

- #5 Triage duplicate ZIP member reports in release notes output: https://github.com/PiotrOnGit123/oss-release-guard/issues/5
- #6 Document private security-report intake fallback: https://github.com/PiotrOnGit123/oss-release-guard/issues/6
- #7 Harden release manifest handling for secret-like keys: https://github.com/PiotrOnGit123/oss-release-guard/issues/7
- #8 Prepare v0.2.0 release checklist and artifact validation: https://github.com/PiotrOnGit123/oss-release-guard/issues/8
- #9 Add regression tests for release readiness gate failures: https://github.com/PiotrOnGit123/oss-release-guard/issues/9
- #10 Improve examples for release notes generator: https://github.com/PiotrOnGit123/oss-release-guard/issues/10
- #11 Auto-classify PRs that touch GitHub templates: https://github.com/PiotrOnGit123/oss-release-guard/issues/11
- #14 Reject malformed release gates and support GitHub API records: https://github.com/PiotrOnGit123/oss-release-guard/issues/14

PR #15 closed #5, #6, #7, #9, #10, #11, and #14 with reproducible fixes/tests and maintainer triage comments. Issue #8 was closed only after actual publication succeeded on 2026-10-09. All eight issues are assigned to the closed v0.2.0 milestone.

## Published Release Verification

The public release is not a draft and remains explicitly marked as an early pre-release. Its four uploaded assets are:

- `oss_release_guard-0.2.0-py3-none-any.whl`
- `oss_release_guard-0.2.0.tar.gz`
- `SHA256SUMS`
- `artifact-audit.json`

The successful publication run completed all six Linux/Windows Python matrix jobs, the quality/security/coverage/package job, and the publication job. It built and audited both distributions and exercised all four maintainer commands from the installed wheel outside the checkout. The v0.2.0 milestone had zero open items and 18 closed issues/PRs when publication completed. v0.1.0 is also a real closed milestone; v0.3.0 contains the two reviewed Dependabot follow-ups.

The first publication attempts stopped before creating the tag. PR #19 added safe endpoint/permission diagnostics; the next log identified `PATCH /issues/1` as requiring PR write permission. PR #20 scoped that permission to the trusted publication job. The failed runs remain visible as honest repair history, not hidden or represented as successful releases.

## Compliance Map

| Challenge requirement | Repository evidence |
| --- | --- |
| Pull request verification | PR template, review guidelines, review-checklist command, PR descriptions/checklists, maintainer self-review submissions on #15/#18/#19/#20, a resolved inline finding on #15, successful CI, and actual Dependabot reviews on #16/#17. |
| Issue classification | Issue templates, `.github/labels.yml`, `.github/repository-metadata.json`, `docs/triage-process.md`, `triage-issue` command, issues #5-#11 with labels and maintainer comments. |
| Release management | Changelog, release docs, readiness/notes commands, v0.1.0 and published v0.2.0 releases, wheel/source assets, checksums, archive reports, actual closed milestones, and completed issue #8. |
| Security | `SECURITY.md`, security-related issue template, security labels, security-focused issues #6 and #7, CI checks, and security guidance in review and triage docs. |
| Code quality | 74 tests, 92% branch-aware runtime coverage, Ruff lint/format, Bandit, pip-audit, six platform/Python combinations, an 85% coverage gate, example consistency, package validation, Dependabot, and no runtime dependencies. |
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

Validated locally on 2026-10-08 and rechecked after publication on 2026-10-09:

- `python -m compileall oss_release_guard tests scripts`: passed
- `python scripts/check_quality.py`: passed
- `python -m unittest discover -s tests -v`: passed, 74 tests
- CLI smoke checks for maintainer workflow examples: passed
- The Python 3.10 matrix uses the development-only `tomli` parser rather than an ad hoc TOML fallback.
- Ruff lint/format, Bandit, pip-audit, example outputs, distribution build, strict Twine checks, and wheel/source archive audits passed.
- PR #15 CI passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37842467178
- PR #20 CI passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37893835752
- Publication gates and asset upload passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37894134275
- A fresh clone of published `main` was clean before the final documentation update. Local Markdown targets were checked, and no token/private-key pattern was found in tracked text files. These checks are bounded validation, not proof that all possible secrets or vulnerabilities are absent.

## Remaining GitHub Administration

The public repository description is relevant to archive verification but does not yet mention all four maintainer helpers. Live GitHub topics are still missing; desired values in `.github/repository-metadata.json` are not a substitute. The connector does not expose these administration mutations, and browser automation was unavailable for the GitHub page.

The owner should open the repository's **About** gear and save:

- Description: `Offline release auditing, issue triage, PR review checklists and release readiness for open-source maintainers.`
- Topics: `open-source`, `maintainer-tools`, `release-management`, `security`, `quality-assurance`, `python`, `cli`, `issue-triage`.

This is the remaining metadata gap, not an unimplemented code or release workflow. No claim of complete metadata compliance is made until the live settings are saved.

## Assumptions And Notes

- The repository was not deleted or recreated.
- No additional human GitHub account was required; automated Dependabot and GitHub Actions activity is identified as such.
- No fake identities, signatures, or contributors were created.
- The authenticated tools could create files, branches, pull requests, issues, comments, labels on issues/PRs, and merges.
- The authorized release workflow uses a temporary job token for contents/issues/PR writes only after CI and artifact validation. PR write permission is required by GitHub to assign milestones to PRs. No token is stored in the repository, and ordinary CI is read-only.
- The workflow created the actual version milestones, synchronized canonical labels, published the release, and closed issue #8 and the v0.2.0 milestone.
- Repository description/topics administration is not exposed by the current connector. Desired topics are recorded in `.github/repository-metadata.json`, but they are not claimed to exist as live GitHub topics.
- This is an early functional project. External adoption, independent human review, and winning the challenge have not been established.
