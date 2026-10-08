"""Repository quality and security policy checks used by CI."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 uses the development-only parser.
    import tomli as tomllib


ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTENSIONS = {".md", ".py", ".toml", ".yml", ".yaml", ".json"}
REQUIRED_FILES = [
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "docs/triage-process.md",
    "docs/release-process.md",
    "docs/review-guidelines.md",
    "docs/quality-standards.md",
    "docs/maintainer-responsibilities.md",
    "docs/architecture.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
    ".github/ISSUE_TEMPLATE/feature_request.yml",
    ".github/ISSUE_TEMPLATE/documentation_task.yml",
    ".github/ISSUE_TEMPLATE/security_related.yml",
    ".github/repository-metadata.json",
]


def iter_text_files() -> list[Path]:
    ignored = {
        ".git",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".venv",
        "__pycache__",
        "build",
        "dist",
    }
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_EXTENSIONS:
            files.append(path)
    return files


def check_required_files(errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required maintenance file: {relative}")


def check_text_hygiene(errors: list[str]) -> None:
    for path in iter_text_files():
        relative = path.relative_to(ROOT)
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            errors.append(f"not utf-8: {relative}")
            continue
        for number, line in enumerate(lines, start=1):
            if "\t" in line:
                errors.append(f"tab character: {relative}:{number}")
            if line.rstrip() != line:
                errors.append(f"trailing whitespace: {relative}:{number}")


def load_project_metadata() -> dict[str, Any]:
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    return tomllib.loads(pyproject_text).get("project", {})


def check_dependency_policy(errors: list[str]) -> None:
    dependencies = load_project_metadata().get("dependencies", [])
    if dependencies:
        errors.append("runtime dependencies must be reviewed before release")
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8").lower()
    for phrase in ("vulnerability", "security", "maintainer"):
        if phrase not in security:
            errors.append(f"SECURITY.md must mention {phrase}")


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)
    check_text_hygiene(errors)
    check_dependency_policy(errors)
    if errors:
        print("Quality gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(
        "Quality gate passed: docs, text hygiene, dependency policy, and security policy are in place."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
