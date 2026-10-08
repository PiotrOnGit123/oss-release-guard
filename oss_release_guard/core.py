"""Inspect a local release without extracting members or making network calls.

The supplied digest must come from a source the caller trusts. A matching hash
does not establish authorship. This strict metadata policy rejects links even
when those links would be legitimate in a particular source distribution.
Declared member sizes are bounded; this is not a malware or payload scanner.
ZIP local member names are checked against central-directory names without
reading or decompressing member payloads. Unsupported ZIP features are errors.
"""

from __future__ import annotations

import hashlib
import re
import stat
import tarfile
import zipfile
from pathlib import Path
from typing import BinaryIO


class AuditError(Exception):
    """An invalid input, unreadable artifact, or unparseable archive."""


class _StrictTarInfo(tarfile.TarInfo):
    """Do not silently treat a broken header after a valid member as EOF."""

    @classmethod
    def fromtarfile(cls, archive: tarfile.TarFile) -> tarfile.TarInfo:
        try:
            return super().fromtarfile(archive)
        except (tarfile.InvalidHeaderError, tarfile.TruncatedHeaderError) as error:
            # TarFile.next normally ignores these errors after the first
            # member. SubsequentHeaderError is propagated as a ReadError.
            raise tarfile.SubsequentHeaderError(str(error)) from error


def _finding(report: dict, code: str, message: str, member: str | None = None) -> None:
    finding = {"code": code, "severity": "error", "message": message}
    if member is not None:
        finding["member"] = member
    report["findings"].append(finding)


def _check_name(report: dict, name: str, is_directory: bool, seen: set[str]) -> None:
    """Apply a portable path policy and track normalized archive destinations."""
    if name.startswith(("/", "\\")):
        _finding(report, "absolute_path", "Absolute or UNC member paths are rejected.", name)
    if re.match(r"^[A-Za-z]:", name):
        _finding(report, "windows_drive", "Windows drive member paths are rejected.", name)
    if "\\" in name:
        _finding(
            report, "backslash_path", "Backslashes are rejected for portable path safety.", name
        )
    if any(ord(char) < 32 or 127 <= ord(char) <= 159 for char in name):
        _finding(
            report,
            "control_character",
            "Member names cannot contain NUL or control characters.",
            name,
        )

    parts = name.replace("\\", "/").split("/")
    if ".." in parts:
        _finding(report, "parent_traversal", "Parent traversal components are rejected.", name)
    normalized = "/".join(part for part in parts if part not in ("", "."))
    if not normalized:
        # A root directory marker has no destination to overwrite. Tar archives
        # often contain a './' entry, so these harmless markers are allowed.
        if not is_directory:
            _finding(report, "empty_name", "A file must have a nonempty destination path.", name)
        return
    if normalized in seen:
        _finding(
            report,
            "duplicate_member",
            "Multiple members share a normalized destination path.",
            name,
        )
    seen.add(normalized)


def _record_size(report: dict, name: str, size: int, max_members: int, max_total_size: int) -> bool:
    if size < 0:
        raise AuditError("Archive member declares a negative size.")
    report["member_count"] += 1
    report["total_uncompressed_bytes"] += size
    exceeded = False
    if report["member_count"] > max_members:
        _finding(
            report,
            "max_members_exceeded",
            f"Archive exceeds the limit of {max_members} members.",
            name,
        )
        exceeded = True
    if report["total_uncompressed_bytes"] > max_total_size:
        _finding(
            report,
            "max_total_size_exceeded",
            f"Archive exceeds the declared-size limit of {max_total_size} bytes.",
            name,
        )
        exceeded = True
    return not exceeded


def _inspect_tar(source: BinaryIO, report: dict, max_members: int, max_total_size: int) -> None:
    seen: set[str] = set()
    # Streaming avoids unpacking contents and permits stopping at the first
    # policy limit. Advancing to the next header can still read compressed data.
    with tarfile.open(fileobj=source, mode="r|*", tarinfo=_StrictTarInfo) as archive:
        for member in archive:
            within_limits = _record_size(
                report, member.name, member.size, max_members, max_total_size
            )
            _check_name(report, member.name, member.isdir(), seen)
            if member.issym() or member.islnk():
                _finding(
                    report,
                    "unsafe_link",
                    "Strict policy rejects symbolic and hard links; legitimate releases may contain links.",
                    member.name,
                )
            elif not (member.isfile() or member.isdir()):
                _finding(
                    report,
                    "special_member",
                    "Only regular files and directories are accepted; devices, FIFOs and special entries are rejected.",
                    member.name,
                )
            if not within_limits:
                break


def _inspect_zip(source: BinaryIO, report: dict, max_members: int, max_total_size: int) -> None:
    seen: set[str] = set()
    # ZipFile reads the central directory before iteration. The member bound
    # limits further inspection, not that initial directory allocation.
    with zipfile.ZipFile(source) as archive:
        for member in archive.infolist():
            name = member.orig_filename
            within_limits = _record_size(
                report, name, member.file_size, max_members, max_total_size
            )
            _check_name(report, name, member.is_dir(), seen)
            if member.flag_bits & 1:
                _finding(
                    report,
                    "encrypted_member",
                    "Encrypted ZIP members are unsupported by this audit.",
                    name,
                )
            elif within_limits:
                # ZipFile.open compares local and central member names and
                # applies its supported-feature and data-range checks. Closing
                # immediately inspects no member payload and extracts nothing.
                with archive.open(member, "r"):
                    pass
            file_type = stat.S_IFMT(member.external_attr >> 16)
            if file_type == stat.S_IFLNK:
                _finding(
                    report,
                    "unsafe_link",
                    "Strict policy rejects symbolic links; legitimate releases may contain links.",
                    name,
                )
            elif file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                _finding(
                    report,
                    "special_member",
                    "Only regular files and directories are accepted; special ZIP entries are rejected.",
                    name,
                )
            if not within_limits:
                break


def inspect_release(
    artifact: Path,
    expected_sha256: str,
    *,
    max_members: int = 100_000,
    max_total_size: int = 1_073_741_824,
) -> dict:
    """Return a JSON-compatible report, or raise :class:`AuditError`.

    Checksums are computed in fixed-size chunks. A mismatch returns a failed
    report immediately, without auditing archive metadata. TAR (plain, gzip,
    bzip2, xz) and ZIP formats are detected from their contents. Files are never
    extracted. The counts include the member that first exceeds either bound.
    """
    if not isinstance(expected_sha256, str) or not re.fullmatch(
        r"[0-9a-fA-F]{64}", expected_sha256
    ):
        raise AuditError("Expected SHA-256 must be exactly 64 hexadecimal characters.")
    for name, value in (("max_members", max_members), ("max_total_size", max_total_size)):
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise AuditError(f"{name} must be a positive integer.")
    try:
        path = Path(artifact)
    except (TypeError, ValueError) as error:
        raise AuditError("Artifact must be a filesystem path.") from error
    expected_sha256 = expected_sha256.lower()
    report = {
        "schema_version": 1,
        "artifact": path.name,
        "sha256": "",
        "expected_sha256": expected_sha256,
        "ok": False,
        "findings": [],
        "member_count": 0,
        "total_uncompressed_bytes": 0,
    }
    try:
        with path.open("rb") as source:
            digest = hashlib.sha256()
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
            report["sha256"] = digest.hexdigest()
            if report["sha256"] != expected_sha256:
                _finding(
                    report,
                    "sha256_mismatch",
                    "Artifact SHA-256 does not match the supplied expected digest.",
                )
                return report
            source.seek(0)
            is_zip = zipfile.is_zipfile(source)
            source.seek(0)
            if is_zip:
                _inspect_zip(source, report, max_members, max_total_size)
            else:
                _inspect_tar(source, report, max_members, max_total_size)
    except (
        OSError,
        EOFError,
        ValueError,
        UnicodeError,
        RuntimeError,
        NotImplementedError,
        tarfile.TarError,
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
    ) as error:
        raise AuditError(
            f"Cannot read artifact or parse a supported TAR/ZIP archive: {error}"
        ) from error
    report["ok"] = not report["findings"]
    return report
