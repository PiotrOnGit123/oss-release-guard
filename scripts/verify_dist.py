"""Audit built archives and record digests for release assets."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from oss_release_guard import __version__, inspect_release  # noqa: E402


def main() -> int:
    dist = ROOT / "dist"
    archives = sorted([*dist.glob("*.whl"), *dist.glob("*.tar.gz")])
    if len(archives) != 2 or not any(path.suffix == ".whl" for path in archives):
        print("Expected exactly one wheel and one source distribution.")
        return 1
    reports = []
    checksums = []
    for artifact in archives:
        if f"-{__version__}" not in artifact.name:
            print("Distribution version does not match the source version.")
            return 1
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        report = inspect_release(artifact, digest)
        if not report["ok"]:
            print(json.dumps(report, indent=2))
            return 1
        reports.append(report)
        checksums.append(f"{digest}  {artifact.name}")
    (dist / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")
    (dist / "artifact-audit.json").write_text(
        json.dumps(reports, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("Wheel and source distribution passed archive policy; digests and reports recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
