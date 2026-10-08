# Validation record

Checked on 2026-10-08 with Python 3.12.14 on Windows.

- 31 local `unittest` tests passed, including malformed TAR headers, unsafe paths,
  ZIP local/central filename disagreement, checksum mismatch and CLI exit codes.
- The package built as a wheel and installed locally with pip without runtime dependencies.
- A historical official PostgreSQL 18.0 source archive passed the checksum and metadata checks.

## PostgreSQL compatibility check

The original archive and digest were downloaded from the official PostgreSQL
distribution endpoint. This demonstrates compatibility with this particular
release artifact; it does not mean PostgreSQL endorses or uses the tool.
This historical version is not a production recommendation.

```sh
curl --fail --location --output postgresql-18.0.tar.bz2 https://ftp.postgresql.org/pub/source/v18.0/postgresql-18.0.tar.bz2
curl --fail --location --output postgresql-18.0.tar.bz2.sha256 https://ftp.postgresql.org/pub/source/v18.0/postgresql-18.0.tar.bz2.sha256
python -m oss_release_guard postgresql-18.0.tar.bz2 --sha256 0d5b903b1e5fe361bca7aa9507519933773eb34266b1357c4e7780fdee6d6078 --format json
```

The archived [JSON report](validation/postgresql-18.0.json) records 7,868 members
and 140,153,830 declared uncompressed bytes, with no policy findings.
The expected checksum in this example matches the official `.sha256` file
retrieved for this check. For a new release, establish trust in the publisher
and expected digest through its authenticated release process.

The large upstream archive is not committed to this repository. Unit tests make
their own small synthetic archives and do not use the network. The test workflow
in `.github/workflows/ci.yml` separately runs tests and package installation on
Linux and Windows with Python 3.10, 3.12, and 3.14. Its results are recorded by
GitHub Actions rather than asserted here.
