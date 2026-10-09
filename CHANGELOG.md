# Changelog

## 0.2.0 - 2026-10-09

### Security And Input Compatibility

- Release readiness requires a version and accepts explicit boolean/status confirmations rather than numeric truthy substitutes.
- Secret-like manifest fields block readiness; reports disclose only the count, not field names or values.
- Maintainer JSON commands reject duplicate keys, invalid UTF-8, non-finite numbers, files over 1 MiB, and nesting deeper than 32 levels. Invalid inputs exit `2` without a traceback.
- Security-sensitive tasks are not recommended as `good first issue` work.

### Fixed

- Recognize GitHub API label and changed-file objects during issue and PR classification.
- Failed release gates show unmet requirements rather than claiming successful verification.
- Support a real TOML parser on Python 3.10 for the repository quality gate.
- Include all maintainer commands in top-level CLI help.

### Added

- Added maintainer workflow helpers for issue triage, pull request review checklists, release readiness gates, and release notes generation.
- Added example JSON inputs for security triage, review checklist generation, release readiness, and release notes.
- Added a local quality gate covering required maintenance documentation, text hygiene, dependency policy, and security policy coverage.
- Expanded GitHub templates and documentation for triage, review, release management, quality standards, security handling, and maintainer responsibilities.
- Added Ruff linting/formatting, Bandit, dependency auditing, an 85% coverage gate, Dependabot, reproducible example outputs, and wheel/source distribution validation.
- Added regression tests for every release gate, malformed inputs, GitHub records, duplicate ZIP finding release notes, and disclosure-safe manifest reports.
- Published verified wheel/source assets, SHA-256 checksums, and archive reports; synchronized live labels and version milestones through the gated release workflow.

## 0.1.0 - 2026-10-08

Initial implementation: streaming SHA-256 verification, TAR/ZIP archive metadata
policy checks, bounded member/declared-size scanning, and text/JSON CLI reports.

This is an early project. External adoption and production use have not been measured.
