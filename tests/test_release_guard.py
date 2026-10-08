"""Exercise the real verifier with generated archives; no binary fixtures required."""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
import warnings
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = PROJECT_ROOT
sys.path.insert(0, str(SOURCE_ROOT))

from oss_release_guard.core import AuditError, inspect_release  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class ArchiveFixtureTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def make_tar(
        self,
        name: str = "release.tar.gz",
        entries: list[tuple[str, bytes]] | None = None,
        mode: str = "w:gz",
        special: list[tarfile.TarInfo] | None = None,
    ) -> Path:
        path = self.directory / name
        if entries is None:
            entries = [("project/README.md", b"Release notes\n"), ("project/src/main.c", b"int main(void) { return 0; }\n")]
        with tarfile.open(path, mode) as archive:
            for member_name, contents in entries:
                info = tarfile.TarInfo(member_name)
                info.size = len(contents)
                archive.addfile(info, io.BytesIO(contents))
            for info in special or []:
                archive.addfile(info)
        return path

    def make_zip(
        self,
        name: str = "release.zip",
        entries: list[tuple[str, bytes]] | None = None,
    ) -> Path:
        path = self.directory / name
        if entries is None:
            entries = [("project/README.md", b"Release notes\n"), ("project/src/main.c", b"int main(void) { return 0; }\n")]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for member_name, contents in entries:
                    archive.writestr(member_name, contents)
        return path

    def assert_report(self, report: dict, artifact: Path) -> None:
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["artifact"], artifact.name)
        self.assertEqual(report["sha256"], sha256(artifact))
        self.assertIsInstance(report["expected_sha256"], str)
        self.assertIsInstance(report["ok"], bool)
        self.assertIsInstance(report["member_count"], int)
        self.assertIsInstance(report["total_uncompressed_bytes"], int)
        self.assertIsInstance(report["findings"], list)
        for finding in report["findings"]:
            for field in ("code", "severity", "message"):
                self.assertIsInstance(finding[field], str)
                self.assertTrue(finding[field])

    def assert_unsafe(self, artifact: Path, **kwargs: int) -> dict:
        report = inspect_release(artifact, sha256(artifact), **kwargs)
        self.assert_report(report, artifact)
        self.assertFalse(report["ok"])
        self.assertTrue(report["findings"])
        return report


class InspectReleaseTests(ArchiveFixtureTest):
    def test_clean_tar_compression_formats_and_zip(self) -> None:
        entries = [("project/a.txt", b"abc"), ("project/b.txt", b"defgh")]
        formats = [
            ("release.tar", "w"),
            ("release.tar.gz", "w:gz"),
            ("release.tar.bz2", "w:bz2"),
            ("release.tar.xz", "w:xz"),
        ]
        artifacts = [self.make_tar(name, entries, mode) for name, mode in formats]
        artifacts.append(self.make_zip(entries=entries))
        for artifact in artifacts:
            with self.subTest(artifact=artifact.name):
                report = inspect_release(artifact, sha256(artifact))
                self.assert_report(report, artifact)
                self.assertTrue(report["ok"])
                self.assertEqual(report["findings"], [])
                self.assertEqual(report["member_count"], 2)
                self.assertEqual(report["total_uncompressed_bytes"], 8)

    def test_checksum_mismatch_is_a_reported_failure(self) -> None:
        artifact = self.make_tar()
        expected = "0" * 64
        report = inspect_release(artifact, expected)
        self.assert_report(report, artifact)
        self.assertFalse(report["ok"])
        self.assertTrue(report["findings"])
        self.assertEqual(report["expected_sha256"], expected)

    def test_uppercase_expected_checksum_is_accepted(self) -> None:
        artifact = self.make_zip()
        report = inspect_release(artifact, sha256(artifact).upper())
        self.assert_report(report, artifact)
        self.assertTrue(report["ok"])
        self.assertEqual(report["findings"], [])

    def test_tar_rejects_paths_that_escape_the_extraction_directory(self) -> None:
        dangerous_paths = [
            "../escape.txt",
            "project/../../escape.txt",
            "/absolute.txt",
            r"C:\Windows\escape.txt",
            r"..\escape.txt",
            r"\\server\share\escape.txt",
        ]
        for index, member_name in enumerate(dangerous_paths):
            with self.subTest(member_name=member_name):
                artifact = self.make_tar(f"unsafe-{index}.tar.gz", [(member_name, b"bad")])
                self.assert_unsafe(artifact)

    def test_zip_rejects_paths_that_escape_the_extraction_directory(self) -> None:
        dangerous_paths = [
            "../escape.txt",
            "project/../../escape.txt",
            "/absolute.txt",
            r"C:\Windows\escape.txt",
            r"..\escape.txt",
            r"\\server\share\escape.txt",
        ]
        for index, member_name in enumerate(dangerous_paths):
            with self.subTest(member_name=member_name):
                artifact = self.make_zip(f"unsafe-{index}.zip", [(member_name, b"bad")])
                self.assert_unsafe(artifact)

    def test_tar_rejects_symbolic_and_hard_links(self) -> None:
        for type_flag in (tarfile.SYMTYPE, tarfile.LNKTYPE):
            with self.subTest(type_flag=type_flag):
                link = tarfile.TarInfo("project/link")
                link.type = type_flag
                link.linkname = "project/README.md"
                artifact = self.make_tar(special=[link])
                self.assert_unsafe(artifact)

    def test_tar_rejects_device_nodes_and_named_pipes(self) -> None:
        for type_flag in (tarfile.CHRTYPE, tarfile.BLKTYPE, tarfile.FIFOTYPE):
            with self.subTest(type_flag=type_flag):
                special = tarfile.TarInfo("project/special")
                special.type = type_flag
                special.devmajor = 1
                special.devminor = 3
                artifact = self.make_tar(special=[special])
                self.assert_unsafe(artifact)

    def test_duplicate_names_are_reported_in_tar_and_zip(self) -> None:
        entries = [("project/README.md", b"first"), ("project/README.md", b"replacement")]
        for artifact in (self.make_tar(entries=entries), self.make_zip(entries=entries)):
            with self.subTest(artifact=artifact.name):
                self.assert_unsafe(artifact)

    def test_member_limit_is_enforced_in_tar_and_zip(self) -> None:
        for artifact in (self.make_tar(), self.make_zip()):
            with self.subTest(artifact=artifact.name):
                self.assert_unsafe(artifact, max_members=1)

    def test_total_uncompressed_byte_limit_is_enforced_in_tar_and_zip(self) -> None:
        entries = [("project/a", b"a" * 16), ("project/b", b"b" * 16)]
        for artifact in (self.make_tar(entries=entries), self.make_zip(entries=entries)):
            with self.subTest(artifact=artifact.name):
                self.assert_unsafe(artifact, max_total_size=31)

    def test_limits_allow_the_exact_boundary(self) -> None:
        entries = [("project/a", b"abc"), ("project/b", b"defgh")]
        for artifact in (self.make_tar(entries=entries), self.make_zip(entries=entries)):
            with self.subTest(artifact=artifact.name):
                report = inspect_release(artifact, sha256(artifact), max_members=2, max_total_size=8)
                self.assertTrue(report["ok"])

    def test_inspection_does_not_extract_or_overwrite_files(self) -> None:
        protected = self.directory / "protected.txt"
        protected.write_text("original", encoding="utf-8")
        artifact = self.make_tar(entries=[("../protected.txt", b"replacement")])
        before = set(self.directory.iterdir())
        self.assert_unsafe(artifact)
        self.assertEqual(protected.read_text(encoding="utf-8"), "original")
        self.assertEqual(set(self.directory.iterdir()), before)

    def test_invalid_checksums_raise_audit_error(self) -> None:
        artifact = self.make_tar()
        for invalid in ("", "a" * 63, "a" * 65, "g" * 64, " " + "a" * 64):
            with self.subTest(invalid=invalid):
                with self.assertRaises(AuditError):
                    inspect_release(artifact, invalid)

    def test_invalid_limits_raise_audit_error(self) -> None:
        artifact = self.make_tar()
        for arguments in (
            {"max_members": 0},
            {"max_members": -1},
            {"max_total_size": 0},
            {"max_total_size": -1},
        ):
            with self.subTest(arguments=arguments):
                with self.assertRaises(AuditError):
                    inspect_release(artifact, sha256(artifact), **arguments)

    def test_missing_file_raises_audit_error(self) -> None:
        with self.assertRaises(AuditError):
            inspect_release(self.directory / "absent.tar.gz", "0" * 64)

    def test_directory_raises_audit_error(self) -> None:
        with self.assertRaises(AuditError):
            inspect_release(self.directory, "0" * 64)

    def test_unsupported_file_raises_audit_error(self) -> None:
        artifact = self.directory / "not-an-archive.txt"
        artifact.write_bytes(b"ordinary text, not an archive\n")
        with self.assertRaises(AuditError):
            inspect_release(artifact, sha256(artifact))

    def test_malformed_archive_raises_audit_error(self) -> None:
        artifact = self.make_zip()
        artifact.write_bytes(artifact.read_bytes()[:16])
        with self.assertRaises(AuditError):
            inspect_release(artifact, sha256(artifact))

    def test_zip_local_filename_must_match_central_directory(self) -> None:
        artifact = self.make_zip(entries=[("safe.txt", b"data")])
        with zipfile.ZipFile(artifact) as archive:
            local_header = archive.infolist()[0].header_offset
        raw = bytearray(artifact.read_bytes())
        # Preserve lengths and the safe central name; only the local name changes.
        raw[local_header + 30:local_header + 38] = b"../x.txt"
        artifact.write_bytes(raw)
        with self.assertRaises(AuditError):
            inspect_release(artifact, sha256(artifact))

    def test_tar_corrupt_or_truncated_header_after_valid_member_is_not_eof(self) -> None:
        for malformed in ("corrupt", "truncated"):
            with self.subTest(malformed=malformed):
                artifact = self.make_tar("release.tar", [("first.txt", b"a"), ("second.txt", b"b")], "w")
                raw = bytearray(artifact.read_bytes())
                # One 512-byte header and one padded payload precede header two.
                if malformed == "corrupt":
                    raw[1024:1536] = b"X" * 512
                else:
                    raw = raw[:1024 + 128]
                artifact.write_bytes(raw)
                with self.assertRaises(AuditError):
                    inspect_release(artifact, sha256(artifact))

    def test_encrypted_zip_is_a_reported_failure(self) -> None:
        artifact = self.make_zip(entries=[("safe.txt", b"data")])
        raw = bytearray(artifact.read_bytes())
        central_header = raw.index(b"PK\x01\x02")
        # Set encryption bit zero consistently in both ZIP headers.
        for offset in (6, central_header + 8):
            flags = int.from_bytes(raw[offset:offset + 2], "little") | 1
            raw[offset:offset + 2] = flags.to_bytes(2, "little")
        artifact.write_bytes(raw)
        self.assert_unsafe(artifact)

    def test_zip_symbolic_link_is_a_reported_failure(self) -> None:
        artifact = self.directory / "symlink.zip"
        info = zipfile.ZipInfo("project/link")
        info.create_system = 3
        info.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(artifact, "w") as archive:
            archive.writestr(info, "../outside")
        self.assert_unsafe(artifact)


class CommandLineTests(ArchiveFixtureTest):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(SOURCE_ROOT) + os.pathsep + environment.get("PYTHONPATH", "")
        return subprocess.run(
            [sys.executable, "-m", "oss_release_guard", *arguments],
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=15,
            check=False,
        )

    def test_json_success_exit_code_and_machine_readable_report(self) -> None:
        artifact = self.make_tar()
        result = self.run_cli(str(artifact), "--sha256", sha256(artifact), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assert_report(report, artifact)
        self.assertTrue(report["ok"])
        self.assertEqual(report["findings"], [])

    def test_text_success_includes_the_artifact_name(self) -> None:
        artifact = self.make_zip()
        result = self.run_cli(str(artifact), "--sha256", sha256(artifact), "--format", "text")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(artifact.name, result.stdout)

    def test_checksum_mismatch_exits_one(self) -> None:
        artifact = self.make_tar()
        result = self.run_cli(str(artifact), "--sha256", "0" * 64, "--format", "json")
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertTrue(report["findings"])

    def test_unsafe_archive_exits_one(self) -> None:
        artifact = self.make_zip(entries=[("../escape", b"bad")])
        result = self.run_cli(str(artifact), "--sha256", sha256(artifact), "--format", "json")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(result.stdout)["ok"])

    def test_cli_limits_are_applied(self) -> None:
        artifact = self.make_tar()
        for option, value in (("--max-members", "1"), ("--max-total-size", "1")):
            with self.subTest(option=option):
                result = self.run_cli(str(artifact), "--sha256", sha256(artifact), option, value, "--format", "json")
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertFalse(json.loads(result.stdout)["ok"])

    def test_invalid_checksum_and_arguments_exit_two(self) -> None:
        artifact = self.make_tar()
        for arguments in (
            (str(artifact), "--sha256", "not-hex"),
            (str(artifact),),
            (str(artifact), "--sha256", sha256(artifact), "--max-members", "0"),
            (str(artifact), "--sha256", sha256(artifact), "--format", "yaml"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr.strip())

    def test_missing_file_exits_two(self) -> None:
        result = self.run_cli(str(self.directory / "missing.tar.gz"), "--sha256", "0" * 64)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.strip())

    def test_unsupported_file_exits_two(self) -> None:
        artifact = self.directory / "readme.txt"
        artifact.write_bytes(b"not an archive")
        result = self.run_cli(str(artifact), "--sha256", sha256(artifact))
        self.assertEqual(result.returncode, 2)
        self.assertTrue(result.stderr.strip())

    def test_version(self) -> None:
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("0.1.0", result.stdout)


if __name__ == "__main__":
    unittest.main()
