# Triage Process

Triage turns public reports into maintainable work. The goal is to identify risk, ownership, reproduction steps, and the next action quickly without overstating certainty.

## Intake checklist

1. Confirm the report is safe to discuss publicly.
2. Check whether the issue is a bug, security report, release task, documentation task, quality task, feature request, or support question.
3. Ask for a minimal synthetic fixture when the report involves archives, generated output, or release metadata.
4. Add labels that describe the work and risk.
5. Decide whether the item belongs in the next release milestone.
6. Leave a maintainer comment explaining the next step.

## Label guide

| Label | Meaning |
| --- | --- |
| `bug` | Incorrect behavior, crash, or regression. |
| `security` | Vulnerability report, hardening task, or disclosure-sensitive concern. |
| `triage` | Needs maintainer classification before implementation. |
| `needs-review` | Needs maintainer review before merge. |
| `release` | Blocks or supports a versioned release. |
| `documentation` | Docs, examples, README, or guidance work. |
| `quality` | Tests, CI, linting, maintainability, or reliability work. |
| `good first issue` | Small, low-risk, well-scoped task. |
| `breaking-change` | User-visible incompatibility or contract change. |
| `maintenance` | Repository hygiene, automation, process, or metadata. |

## Priority guide

- `P0`: confirmed credential leak, exploit path, or release-blocking security risk.
- `P1`: release blocker, high-risk security hardening, or severe regression.
- `P2`: ordinary bug, compatibility issue, or missing quality gate.
- `P3`: documentation, examples, cleanup, and low-risk enhancements.

## CLI support

Maintainers can run:

```sh
oss-release-guard triage-issue examples/issue-security.json --format json
```

The classifier suggests labels, priority, risk, routing, and rationale. Its output is advisory. Maintainers keep final responsibility for labels and user-facing comments.
