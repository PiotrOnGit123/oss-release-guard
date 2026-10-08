# Quality Standards

OSS Release Guard favors predictable behavior, small changes, and no unnecessary runtime dependencies. The tool is used around release artifacts, so error paths and documentation matter as much as happy paths.

## Required gates

- `ruff check .` and `ruff format --check .`
- `bandit -r oss_release_guard -ll`
- `pip-audit -r requirements-dev.txt --strict`
- `python -m compileall oss_release_guard tests scripts`
- `python scripts/check_quality.py`
- `python -m unittest discover -s tests -v`
- CLI smoke tests for archive audit and maintainer workflow commands
- `coverage run -m unittest discover -s tests`, `coverage combine`, and `coverage report` (minimum 85%, including branches)
- `python scripts/check_examples.py`
- `python -m build`, `twine check --strict dist/*.whl dist/*.tar.gz`, and `python scripts/verify_dist.py`

## Code expectations

- Preserve backward-compatible CLI behavior unless a release notes entry calls out the change.
- Keep JSON output deterministic and machine-readable.
- Use synthetic fixtures for tests; do not commit private archives or secrets.
- Avoid runtime dependencies unless maintainers explicitly approve the release risk.
- Keep security claims precise and documented.

## CI expectations

The GitHub Actions workflow runs on Linux and Windows with Python 3.10, 3.12, and 3.14. Its separate quality job runs linting, formatting, security scans, dependency auditing, coverage, example checks, and package validation on Python 3.12. Install pinned tools with `python -m pip install -r requirements-dev.txt .`; only the Python 3.10 quality script needs the development-only `tomli` parser.

## Dependency and security checks

The project currently has no runtime dependencies. `scripts/check_quality.py` fails when runtime dependencies are added without review. If dependencies become necessary, maintainers should add dependency review, update security documentation, and explain the risk in the release notes.

Development tools and the build backend are pinned in `requirements-dev.txt`; pip-audit checks their resolved dependencies for known vulnerabilities. Dependabot proposes weekly pip and GitHub Actions updates. Review update PRs against this same CI rather than merging them merely because a bot opened them.
