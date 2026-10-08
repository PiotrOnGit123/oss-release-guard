# Contributing

Start with a reproducible issue or a focused pull request. Include the Python version, operating system, command, expected result, and actual result. Share a minimal synthetic archive when possible; do not upload private code, credentials, or exploit material to a public issue.

Install and run the tests from the repository root:

```sh
python -m pip install .
python -m unittest discover -s tests -v
```

Changes to archive policy should include a small fixture demonstrating the accepted or rejected case. Document compatibility effects, especially changes affecting legitimate release archives. Keep runtime dependencies minimal and preserve stable exit-code behavior.

Reviewers should check the failure path, resource implications, and whether documentation overstates the guarantee. Security reports follow [SECURITY.md](SECURITY.md).

By submitting a contribution, you agree that it may be distributed under this repository's MIT license.
