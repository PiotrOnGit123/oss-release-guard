"""Keep the public input/output examples in sync with the tool."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from oss_release_guard.maintainer import (  # noqa: E402
    assess_release_readiness,
    build_review_checklist,
    classify_issue,
    generate_release_notes,
    load_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    examples = ROOT / "examples"
    outputs = {
        "issue-security.json": classify_issue(load_json(examples / "issue-security.json")),
        "pr-review.md": build_review_checklist(load_json(examples / "pr-review.json")),
        "release-readiness.json": assess_release_readiness(
            load_json(examples / "release-manifest.json")
        ),
        "release-notes.md": generate_release_notes(load_json(examples / "release-changes.json")),
    }
    errors = []
    for name, report in outputs.items():
        content = (
            report
            if isinstance(report, str)
            else json.dumps(report, indent=2, sort_keys=True) + "\n"
        )
        path = examples / "expected" / name
        if args.update:
            path.parent.mkdir(exist_ok=True)
            path.write_text(content, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != content:
            errors.append(name)
    if errors:
        print("Example outputs differ: " + ", ".join(errors))
        return 1
    print("All four maintainer example outputs match.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
