# v0.2.0 - 2026-10-08

## Breaking Changes

- Reject malformed, duplicate-key and oversized maintainer JSON inputs; release readiness now requires a version and blocks secret-like fields (#14)

## Security

- Add security-aware issue triage for release maintenance workflows (#1)

## Fixed

- Use a compatible TOML parser for the Python 3.10 quality gate (#13)

## Documentation

- Document triage, review, release, quality, and maintainer responsibilities (#2)

## Quality

- Add local quality gate covering documentation, text hygiene, and dependency policy (#3)
