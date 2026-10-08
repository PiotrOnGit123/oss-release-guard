"""Command-line entry point for offline release checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import AuditError, __version__, inspect_release


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="oss-release-guard",
        description="Check a local release digest and TAR/ZIP metadata without extracting files.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("artifact", type=Path, help="Local TAR or ZIP release artifact")
    parser.add_argument("--sha256", required=True, help="Expected SHA-256 from a source you trust")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Report output format")
    parser.add_argument("--max-members", type=int, default=100_000, help="Maximum accepted member count (default: 100000)")
    parser.add_argument("--max-total-size", type=int, default=1_073_741_824, help="Maximum declared uncompressed bytes (default: 1073741824)")
    args = parser.parse_args(argv)
    try:
        report = inspect_release(
            args.artifact,
            args.sha256,
            max_members=args.max_members,
            max_total_size=args.max_total_size,
        )
    except AuditError as error:
        # Escape embedded control characters from filenames/parser messages.
        message = str(error).encode("unicode_escape").decode("ascii")
        print(f"oss-release-guard: {message}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        status = "PASS" if report["ok"] else "FAIL"
        print(f"{status}: {ascii(report['artifact'])}")
        print(f"SHA-256: {report['sha256']}")
        print(f"Members inspected: {report['member_count']}; declared uncompressed bytes: {report['total_uncompressed_bytes']}")
        for finding in report["findings"]:
            member = f" ({ascii(finding['member'])})" if "member" in finding else ""
            print(f"{finding['code']}{member}: {finding['message']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
