#!/usr/bin/env python3
"""Validate the six published Codex skills without third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
KEY_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*)$")
PRIVATE_WINDOWS_PATH_RE = re.compile(r"[A-Za-z]:\\Users\\[^\\\r\n]+\\")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def read_utf8(path: Path, errors: list[str]) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        fail(errors, f"{path}: not valid UTF-8 ({exc})")
        return None


def parse_frontmatter(path: Path, text: str, errors: list[str]) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail(errors, f"{path}: missing YAML frontmatter delimited by ---")
        return {}

    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key_match = KEY_RE.match(line)
        if not key_match:
            fail(errors, f"{path}: unsupported frontmatter line: {line!r}")
            continue
        key, value = key_match.groups()
        fields[key] = value.strip().strip('"\'')
    return fields


def check_trailing_whitespace(path: Path, text: str, errors: list[str]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if line.endswith((" ", "\t")):
            fail(errors, f"{path}:{line_number}: trailing whitespace")


def check_relative_links(path: Path, text: str, errors: list[str]) -> None:
    for raw_target in LINK_RE.findall(text):
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        target_path = target.split("#", 1)[0]
        if not target_path:
            continue
        resolved = (path.parent / target_path).resolve()
        if not resolved.exists():
            fail(errors, f"{path}: broken relative link {target!r}")


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    manifest_path = repo_root / "skills-manifest.json"
    errors: list[str] = []

    manifest_text = read_utf8(manifest_path, errors)
    if manifest_text is None:
        return 1
    manifest = json.loads(manifest_text)
    entries = manifest.get("skills", [])
    expected_names = [entry["name"] for entry in entries]

    if len(expected_names) != len(set(expected_names)):
        fail(errors, "skills-manifest.json: duplicate skill names")

    skills_root = repo_root / "skills"
    discovered = sorted(
        path.name for path in skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    if discovered != sorted(expected_names):
        fail(
            errors,
            "Published skill set differs from manifest: "
            f"expected={sorted(expected_names)}, discovered={discovered}",
        )

    for entry in entries:
        name = entry["name"]
        skill_dir = repo_root / entry["path"]
        skill_md = skill_dir / "SKILL.md"
        ui_yaml = skill_dir / "agents" / "openai.yaml"

        if not NAME_RE.fullmatch(name):
            fail(errors, f"{name}: invalid skill name")
        if skill_dir.name != name:
            fail(errors, f"{name}: manifest path folder does not match name")
        if not skill_md.is_file():
            fail(errors, f"{name}: SKILL.md is missing")
            continue

        skill_text = read_utf8(skill_md, errors)
        if skill_text is None:
            continue
        fields = parse_frontmatter(skill_md, skill_text, errors)
        if set(fields) != {"name", "description"}:
            fail(errors, f"{skill_md}: frontmatter must contain only name and description")
        if fields.get("name") != name:
            fail(errors, f"{skill_md}: frontmatter name does not match folder")
        if not fields.get("description"):
            fail(errors, f"{skill_md}: description is empty")
        if len(skill_text.splitlines()) > 500:
            fail(errors, f"{skill_md}: exceeds the 500-line progressive-disclosure limit")
        check_trailing_whitespace(skill_md, skill_text, errors)
        check_relative_links(skill_md, skill_text, errors)

        if not ui_yaml.is_file():
            fail(errors, f"{name}: agents/openai.yaml is missing")
        else:
            ui_text = read_utf8(ui_yaml, errors)
            if ui_text is not None:
                check_trailing_whitespace(ui_yaml, ui_text, errors)
                for required in ("display_name:", "short_description:", "default_prompt:"):
                    if required not in ui_text:
                        fail(errors, f"{ui_yaml}: missing {required}")
                if f"${name}" not in ui_text:
                    fail(errors, f"{ui_yaml}: default prompt must mention ${name}")

        for file_path in skill_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in {
                ".md", ".yaml", ".yml", ".json", ".py", ".ps1"
            }:
                file_text = read_utf8(file_path, errors)
                if file_text is not None:
                    check_trailing_whitespace(file_path, file_text, errors)
                    if PRIVATE_WINDOWS_PATH_RE.search(file_text):
                        fail(errors, f"{file_path}: contains a private machine-specific path")

    repository_files = [
        repo_root / "README.md",
        repo_root / "LICENSE",
        repo_root / "skills-manifest.json",
        repo_root / ".github" / "workflows" / "validate-skills.yml",
        *sorted((repo_root / "scripts").glob("*")),
    ]
    for file_path in repository_files:
        if not file_path.is_file():
            fail(errors, f"{file_path}: required repository file is missing")
            continue
        file_text = read_utf8(file_path, errors)
        if file_text is None:
            continue
        check_trailing_whitespace(file_path, file_text, errors)
        if file_path.suffix.lower() == ".md":
            check_relative_links(file_path, file_text, errors)

    if errors:
        print("Skill validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validated {len(entries)} skills: {', '.join(expected_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
