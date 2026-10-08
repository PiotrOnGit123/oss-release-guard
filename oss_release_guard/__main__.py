"""Command-line entry point for release and maintainer checks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import AuditError, __version__, inspect_release
from .maintainer import (
    assess_release_readiness,
    build_review_checklist,
    classify_issue,
    classify_pull_request,
    generate_release_notes,
    load_json,
)

MAINTAINER_COMMANDS = {"triage-issue", "review-checklist", "release-readiness", "release-notes"}


def _print_json(data: dict) -> None:
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True))


def _run_maintainer_command(argv: list[str]) -> int:
    try:
        return _execute_maintainer_command(argv)
    except ValueError as error:
        message = str(error).encode("unicode_escape").decode("ascii")
        print(f"oss-release-guard: {message}", file=sys.stderr)
        return 2


def _execute_maintainer_command(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="oss-release-guard",
        description="Maintainer workflow helpers for issue triage, PR review, and releases.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    triage = subparsers.add_parser("triage-issue", help="Classify an issue JSON object")
    triage.add_argument("input", type=Path)
    triage.add_argument("--format", choices=("text", "json"), default="text")

    review = subparsers.add_parser("review-checklist", help="Generate a PR review checklist")
    review.add_argument("input", type=Path)
    review.add_argument("--format", choices=("markdown", "json"), default="markdown")

    readiness = subparsers.add_parser("release-readiness", help="Evaluate release readiness gates")
    readiness.add_argument("input", type=Path)
    readiness.add_argument("--format", choices=("text", "json"), default="text")

    notes = subparsers.add_parser("release-notes", help="Generate grouped release notes")
    notes.add_argument("input", type=Path)

    args = parser.parse_args(argv)
    data = load_json(args.input)

    if args.command == "triage-issue":
        result = classify_issue(data)
        if args.format == "json":
            _print_json(result)
        else:
            print(f"Priority: {result['priority']}")
            print(f"Risk: {result['risk']}")
            print(f"Routing: {result['routing']}")
            print(f"Labels: {', '.join(result['labels'])}")
            for item in result["rationale"]:
                print(f"- {item}")
        return 0
    if args.command == "review-checklist":
        if args.format == "json":
            result = classify_pull_request(data)
            result["checklist"] = build_review_checklist(data)
            _print_json(result)
        else:
            print(build_review_checklist(data), end="")
        return 0
    if args.command == "release-readiness":
        result = assess_release_readiness(data)
        if args.format == "json":
            _print_json(result)
        else:
            status = "READY" if result["ready"] else "NOT READY"
            print(f"{status}: {result['version']}")
            for gate in result["gates"]:
                marker = "PASS" if gate["passed"] else "FAIL"
                print(f"{marker}: {gate['name']} - {gate['evidence']}")
        return 0 if result["ready"] else 1
    if args.command == "release-notes":
        print(generate_release_notes(data), end="")
        return 0
    return 2


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] in MAINTAINER_COMMANDS:
        return _run_maintainer_command(argv)

    parser = argparse.ArgumentParser(
        prog="oss-release-guard",
        description="Check a local release digest and TAR/ZIP metadata without extracting files.",
        epilog="Maintainer commands: triage-issue, review-checklist, release-readiness, release-notes. Use COMMAND --help for details.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("artifact", type=Path, help="Local TAR or ZIP release artifact")
    parser.add_argument("--sha256", required=True, help="Expected SHA-256 from a source you trust")
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="Report output format"
    )
    parser.add_argument(
        "--max-members",
        type=int,
        default=100_000,
        help="Maximum accepted member count (default: 100000)",
    )
    parser.add_argument(
        "--max-total-size",
        type=int,
        default=1_073_741_824,
        help="Maximum declared uncompressed bytes (default: 1073741824)",
    )
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
        print(
            f"Members inspected: {report['member_count']}; declared uncompressed bytes: {report['total_uncompressed_bytes']}"
        )
        for finding in report["findings"]:
            member = f" ({ascii(finding['member'])})" if "member" in finding else ""
            print(f"{finding['code']}{member}: {finding['message']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
