# Contributing

Start with a reproducible issue or a focused pull request. Include the Python version, operating system, command, expected result, and actual result. Share a minimal synthetic archive when possible; do not upload private code, credentials, or exploit material to a public issue.

Use the issue templates so maintainers can triage consistently:

- Bug reports should include expected behavior, observed behavior, and a minimal reproducer.
- Documentation tasks should include the page or workflow that is confusing.
- Security-related public reports must describe only the high-level concern and request a private channel when sensitive details are involved.
- Feature requests should describe a concrete maintainer workflow and acceptance criteria.

Install and run the tests from the repository root:

```sh
python -m pip install -r requirements-dev.txt .
ruff check .
ruff format --check .
bandit -r oss_release_guard -ll
python scripts/check_quality.py
python -m unittest discover -s tests -v
python scripts/check_examples.py
```

Changes to archive policy or maintainer workflow output should include a small fixture demonstrating the accepted or rejected case. Document compatibility effects, especially changes affecting legitimate release archives or release automation. Keep runtime dependencies minimal and preserve stable exit-code behavior.

Use `ruff format .` for formatting. When example behavior changes intentionally, run `python scripts/check_examples.py --update` and review the input/output diff. CI also checks coverage, audits development dependencies, and builds and validates wheel/source distributions; see [quality standards](docs/quality-standards.md).

Reviewers should check failure paths, resource implications, user-facing output, documentation accuracy, and whether security guarantees are overstated. Security reports follow [SECURITY.md](SECURITY.md). Release-facing PRs must update [CHANGELOG.md](CHANGELOG.md) or explain why no changelog entry is needed.

Maintainers may add labels such as `triage`, `needs-review`, `security`, `release`, `documentation`, `quality`, `good first issue`, `breaking-change`, and `maintenance` to make ownership and risk visible. See [docs/triage-process.md](docs/triage-process.md) and [docs/review-guidelines.md](docs/review-guidelines.md).

By submitting a contribution, you agree that it may be distributed under this repository's MIT license.
