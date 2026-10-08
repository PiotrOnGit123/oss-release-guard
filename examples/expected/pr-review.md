# Pull Request Review Checklist

Risk: medium
Suggested labels: documentation, maintenance, needs-review, quality, release

## Scope
- [ ] The PR description explains the user-visible change.
- [ ] Related issues, release notes, and migration notes are linked.
- [ ] The change is small enough to review or explicitly split into phases.

## Quality
- [ ] Tests cover success, failure, and boundary cases.
- [ ] Local quality gates pass before merge.
- [ ] Documentation and examples match the implemented behavior.

## Security
- [ ] Inputs, file paths, and generated output are validated.
- [ ] No secrets, tokens, private data, or unsafe defaults are introduced.
- [ ] Security-sensitive findings have a private handling path if needed.

## Reviewer Focus
- [ ] Repository automation and GitHub metadata
- [ ] Documentation accuracy and links
- [ ] Test coverage and quality gates
- [ ] Release notes, changelog, and migration impact
