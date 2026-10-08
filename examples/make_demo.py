"""Make a tiny demonstration release; these self-generated hashes are not trust anchors."""

import argparse
import gzip
import hashlib
import io
import tarfile
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", nargs="?", default="demo")
    destination = Path(parser.parse_args().destination)
    destination.mkdir(parents=True, exist_ok=True)
    payload = b"Example release for testing oss-release-guard.\n"
    archive = destination / "demo-release.tar.gz"
    with archive.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w") as release:
                member = tarfile.TarInfo("demo-release/README.txt")
                member.size = len(payload)
                member.mode = 0o644
                release.addfile(member, io.BytesIO(payload))
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (destination / "SHA256SUMS").write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    print(f"Artifact: {archive}")
    print(f"SHA256: {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
