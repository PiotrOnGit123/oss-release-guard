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
- Patch release preparation: https://github.com/PiotrOnGit123/oss-release-guard/issues/24 ; v0.2.1 is not claimed as published until that issue is completed by the verified workflow.

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
- #21 Document the published release and verified maintenance evidence: https://github.com/PiotrOnGit123/oss-release-guard/pull/21
- #25 Reject JSON exponent overflow and prepare verified v0.2.1: https://github.com/PiotrOnGit123/oss-release-guard/pull/25

Real Dependabot proposals [#16 (setup-python)](https://github.com/PiotrOnGit123/oss-release-guard/pull/16) and [#17 (checkout)](https://github.com/PiotrOnGit123/oss-release-guard/pull/17) were initially deferred, then approved and merged during the follow-up audit. Both current diffs covered CI and publication, exact pins matched official upstream tags, and combined main CI passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37976958767 . Their maintenance tracking [issue #22](https://github.com/PiotrOnGit123/oss-release-guard/issues/22) is complete. They are automated contributions reviewed by the maintainer, not independent human reviews or invented accounts. These upgrades are included in v0.2.1 preparation, not retroactive changes to v0.2.0.

## Issues

- #5 Triage duplicate ZIP member reports in release notes output: https://github.com/PiotrOnGit123/oss-release-guard/issues/5
- #6 Document private security-report intake fallback: https://github.com/PiotrOnGit123/oss-release-guard/issues/6
- #7 Harden release manifest handling for secret-like keys: https://github.com/PiotrOnGit123/oss-release-guard/issues/7
- #8 Prepare v0.2.0 release checklist and artifact validation: https://github.com/PiotrOnGit123/oss-release-guard/issues/8
- #9 Add regression tests for release readiness gate failures: https://github.com/PiotrOnGit123/oss-release-guard/issues/9
- #10 Improve examples for release notes generator: https://github.com/PiotrOnGit123/oss-release-guard/issues/10
- #11 Auto-classify PRs that touch GitHub templates: https://github.com/PiotrOnGit123/oss-release-guard/issues/11
- #14 Reject malformed release gates and support GitHub API records: https://github.com/PiotrOnGit123/oss-release-guard/issues/14
- #22 Complete compatibility review of pinned GitHub Actions v7 upgrades: https://github.com/PiotrOnGit123/oss-release-guard/issues/22
- #23 Reject JSON exponent overflow before maintainer workflow processing: https://github.com/PiotrOnGit123/oss-release-guard/issues/23
- #24 Publish v0.2.1 with the verified JSON overflow fix: https://github.com/PiotrOnGit123/oss-release-guard/issues/24

PR #15 closed #5, #6, #7, #9, #10, #11, and #14 with reproducible fixes/tests and maintainer triage comments. Issue #8 was closed only after actual publication succeeded on 2026-10-09. All eight issues are assigned to the closed v0.2.0 milestone.

## Published Release Verification

The public release is not a draft and remains explicitly marked as an early pre-release. Its four uploaded assets are:

- `oss_release_guard-0.2.0-py3-none-any.whl`
- `oss_release_guard-0.2.0.tar.gz`
- `SHA256SUMS`
- `artifact-audit.json`

The successful publication run completed all six Linux/Windows Python matrix jobs, the quality/security/coverage/package job, and the publication job. It built and audited both distributions and exercised all four maintainer commands from the installed wheel outside the checkout. The v0.2.0 milestone had zero open items and 18 closed issues/PRs when publication completed. v0.1.0 is also a real closed milestone. v0.3.0 remains open for development work; the Dependabot upgrades were subsequently completed there without claiming a v0.3.0 release.

The first publication attempts stopped before creating the tag. PR #19 added safe endpoint/permission diagnostics; the next log identified `PATCH /issues/1` as requiring PR write permission. PR #20 scoped that permission to the trusted publication job. The failed runs remain visible as honest repair history, not hidden or represented as successful releases.

## Compliance Map

| Challenge requirement | Repository evidence |
| --- | --- |
| Pull request verification | PR template, review guidelines, review-checklist command, PR descriptions/checklists, maintainer self-review submissions on #15/#18/#19/#20, a resolved inline finding on #15, successful CI, and actual Dependabot reviews on #16/#17. |
| Issue classification | Issue templates, `.github/labels.yml`, `.github/repository-metadata.json`, `docs/triage-process.md`, `triage-issue` command, issues #5-#11 with labels and maintainer comments. |
| Release management | Changelog, release docs, readiness/notes commands, v0.1.0 and published v0.2.0 releases, wheel/source assets, checksums, archive reports, actual closed milestones, and completed issue #8. |
| Security | `SECURITY.md`, security-related issue template, security labels, security-focused issues #6 and #7, CI checks, and security guidance in review and triage docs. |
| Code quality | 77 development-head tests (74 at v0.2.0 publication), 92% branch-aware runtime coverage, Ruff lint/format, Bandit, pip-audit, six platform/Python combinations, an 85% coverage gate, example consistency, package validation, reviewed Dependabot upgrades, and no runtime dependencies. |
| Maintainer documentation | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `docs/maintainer-responsibilities.md`, `docs/architecture.md`, triage/review/release/quality docs. |

## Original Requirements Audit

The original nine requirement groups were rechecked against public GitHub state and a fresh source checkout on 2026-10-09. The audit found a real JSON exponent-overflow defect and completed the previously deferred dependency reviews. Status describes evidence, not a prediction of the challenge result.

| Original group | Status | Verified evidence or remaining work |
| --- | --- | --- |
| 1. Working code | Met, with a follow-up fix | Archive audit plus four maintainer commands, runnable README instructions, committed example inputs/outputs, tests and lint. Issue #23 records the additional overflow regression and fix. |
| 2. Documentation | Met | All requested top-level documents and triage/release/review/quality/responsibility/architecture docs exist. README and SECURITY distinguish the previous release from patch-version fixes. |
| 3. GitHub metadata | Partially met | Four issue forms, a PR checklist, CI, all ten requested labels, and live v0.1.0/v0.2.0/v0.3.0 milestones exist. Live About topics are absent and the description needs expansion; static desired metadata is not counted as live configuration. |
| 4. Real issues | Met | The eight original follow-up issues #5-#11/#14 have labels, milestones and maintainer comments. Actual audit findings and maintenance work are tracked in #22/#23. No pretend reports or adoption claims were created. |
| 5. Real PR workflow | Met with disclosed limits | Scoped branches/changes, descriptions, checklists, issue links, CI, actual squash merges, maintainer self-review, a resolved inline finding, and maintainer approvals on the real bot contributions #16/#17. No independent second human review is claimed. |
| 6. Releases | Met | Public v0.1.0 and v0.2.0 releases, tags, notes, changelog/security/quality links, and a closed v0.2.0 milestone. v0.2.0 has four verified downloadable assets. v0.3.0 is not claimed to be published. |
| 7. Security and quality | Met within stated boundaries | Runtime regression tests, Ruff, Bandit, strict dependency audit, coverage enforcement, package verification, private-disclosure fallback, public non-sensitive security tasks and documented maintainer response. These controls do not prove absence of vulnerabilities. |
| 8. Evidence file | Met | This file records repository reuse, real issue/PR/release links, domain compliance, execution instructions, measured validation and collaboration assumptions. |
| 9. Final validation | Checks performed | Fresh clone matched public main, baseline combined Actions passed, 77 local tests passed, examples and documentation targets were checked, and the scoped secret-pattern scan had no matches. Follow-up PR CI is required before merging the new runtime fix. |

No new repository, transfer or additional human account was required. The remaining mandatory owner action is saving live About metadata, detailed below. Branch protection and a configured private advisory channel are additional recommendations, not requirements falsely marked as completed; the observed main branch is unprotected and SECURITY documents the fallback rather than claiming private reporting is enabled.

### Follow-Up Regression

The audit reproduced `{ "value": 1e309 }` becoming an infinite Python float. Rejecting literal `NaN`/`Infinity` alone did not cover exponent overflow. The v0.2.1 fix uses a finite-float parsing hook; three additional tests cover signed/nested overflow, finite-number compatibility, and non-disclosing exit-code `2` behavior for all four CLI commands. This produces 77 passing tests and retains 92% branch-aware runtime coverage. Published v0.2.0 assets remain unchanged and retain the documented limitation; issue #24 separately tracks actual patch publication.

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
- `python -m unittest discover -s tests -v`: passed, 77 development-head tests; the published v0.2.0 source had 74
- CLI smoke checks for maintainer workflow examples: passed
- The Python 3.10 matrix uses the development-only `tomli` parser rather than an ad hoc TOML fallback.
- Ruff lint/format, Bandit, pip-audit, example outputs, distribution build, strict Twine checks, and wheel/source archive audits passed.
- PR #15 CI passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37842467178
- PR #20 CI passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37893835752
- Publication gates and asset upload passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37894134275
- Combined main CI after both reviewed Actions upgrades passed: https://github.com/PiotrOnGit123/oss-release-guard/actions/runs/37976958767
- Follow-up local regression run, Ruff lint/format, Bandit, compile/policy checks, example comparison, and branch coverage passed. New runtime fixes must still pass PR CI before merge.
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
