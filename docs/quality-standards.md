# Quality Standards

OSS Release Guard favors predictable behavior, small changes, and no unnecessary runtime dependencies. The tool is used around release artifacts, so error paths and documentation matter as much as happy paths.

## Required gates

- `python -m compileall oss_release_guard tests scripts`
- `python scripts/check_quality.py`
- `python -m unittest discover -s tests -v`
- CLI smoke tests for archive audit and maintainer workflow commands

## Code expectations

- Preserve backward-compatible CLI behavior unless a release notes entry calls out the change.
- Keep JSON output deterministic and machine-readable.
- Use synthetic fixtures for tests; do not commit private archives or secrets.
- Avoid runtime dependencies unless maintainers explicitly approve the release risk.
- Keep security claims precise and documented.

## CI expectations

The GitHub Actions workflow runs on Linux and Windows across supported Python versions. It verifies source compilation, repository quality checks, tests, installed CLI behavior, and maintainer workflow examples.

## Dependency and security checks

The project currently has no runtime dependencies. `scripts/check_quality.py` fails when runtime dependencies are added without review. If dependencies become necessary, maintainers should add dependency review, update security documentation, and explain the risk in the release notes.
