#!/usr/bin/env python3
"""Perform deterministic structural checks for module-introduction documents."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote


IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")
MERMAID_PATTERN = re.compile(r"^\s*(?:`{3,}|~{3,})mermaid\b", re.IGNORECASE | re.MULTILINE)
PLACEHOLDER_PATTERNS = (
    re.compile(r"<module-slug>", re.IGNORECASE),
    re.compile(r"\bTBD\b", re.IGNORECASE),
    re.compile(r"\bTO[- ]?BE[- ]?FILLED\b", re.IGNORECASE),
    re.compile(r"待回填|待补充|占位内容"),
)
MOUSTACHE_PLACEHOLDER_PATTERN = re.compile(r"\{\{[^}\n]+\}\}")
SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"(?i)\bAuthorization\s*:\s*Bearer\s+[A-Za-z0-9._~-]{16,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}\b"),
)
TEMP_IMAGE_MARKERS = (
    "$CODEX_HOME/generated_images",
    ".codex/generated_images",
    "data:image/",
    "blob:",
)
HIGH_RISK_TERMS = (
    "当前",
    "默认",
    "总是",
    "一定",
    "自动",
    "实时",
    "流式",
    "异步",
    "事务",
    "原子",
    "成功",
    "完成",
    "已验证",
    "最多",
    "至少",
    "重试",
    "超时",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate generated module documentation before review."
    )
    parser.add_argument("documents", nargs="+", type=Path)
    parser.add_argument(
        "--allow-no-mermaid",
        action="store_true",
        help="Permit a small document that intentionally has no Mermaid diagram.",
    )
    return parser.parse_args()


def normalize_image_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    match = re.match(r"^(\S+)(?:\s+['\"].*['\"])?$", target)
    if match:
        target = match.group(1)
    return unquote(target.split("#", 1)[0])


def find_fence_errors(lines: list[str]) -> list[str]:
    """Return errors for an unclosed Markdown fence without parsing fence content."""
    opening: tuple[str, int, int] | None = None
    for line_number, line in enumerate(lines, start=1):
        match = FENCE_PATTERN.match(line)
        if not match:
            continue
        marker = match.group(1)
        marker_char = marker[0]
        if opening is None:
            opening = (marker_char, len(marker), line_number)
            continue
        opening_char, opening_length, _ = opening
        if marker_char == opening_char and len(marker) >= opening_length:
            opening = None

    if opening is None:
        return []
    marker_char, marker_length, line_number = opening
    marker = marker_char * marker_length
    return [f"unclosed {marker!r} fence opened on line {line_number}"]


def mask_markdown_code(text: str) -> str:
    """Mask fenced and inline code while preserving newlines for diagnostics."""
    masked_lines: list[str] = []
    opening: tuple[str, int] | None = None
    for line in text.splitlines(keepends=True):
        match = FENCE_PATTERN.match(line)
        if match:
            marker = match.group(1)
            marker_key = (marker[0], len(marker))
            if opening is None:
                opening = marker_key
            elif marker_key[0] == opening[0] and marker_key[1] >= opening[1]:
                opening = None
            masked_lines.append("\n" if line.endswith("\n") else "")
            continue
        if opening is not None:
            masked_lines.append("\n" if line.endswith("\n") else "")
            continue
        newline = "\n" if line.endswith("\n") else ""
        content = line[:-1] if newline else line
        content = re.sub(r"`+[^`\n]*`+", lambda match: " " * len(match.group(0)), content)
        masked_lines.append(content + newline)
    return "".join(masked_lines)


def validate_document(path: Path, allow_no_mermaid: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return [f"{path}: file does not exist"], warnings
    except UnicodeDecodeError as exc:
        return [f"{path}: not valid UTF-8 ({exc})"], warnings

    if not text.strip():
        errors.append(f"{path}: document is empty")
        return errors, warnings

    lines = text.splitlines()
    trailing = [index for index, line in enumerate(lines, start=1) if line.rstrip() != line]
    if trailing:
        preview = ", ".join(str(number) for number in trailing[:8])
        errors.append(f"{path}: trailing whitespace on line(s) {preview}")

    for fence_error in find_fence_errors(lines):
        errors.append(f"{path}: {fence_error}")

    if not allow_no_mermaid and not MERMAID_PATTERN.search(text):
        errors.append(f"{path}: missing a Mermaid source-of-truth diagram")

    if not re.search(r"覆盖台账|参考索引|证据索引|Coverage Ledger|Evidence Index", text, re.IGNORECASE):
        errors.append(f"{path}: missing a coverage/evidence index section")

    for pattern in PLACEHOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{path}:{line}: unresolved placeholder {match.group(0)!r}")

    prose = mask_markdown_code(text)
    match = MOUSTACHE_PLACEHOLDER_PATTERN.search(prose)
    if match:
        line = prose.count("\n", 0, match.start()) + 1
        errors.append(f"{path}:{line}: unresolved placeholder {match.group(0)!r}")

    for pattern in SECRET_PATTERNS:
        match = pattern.search(text)
        if match:
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{path}:{line}: possible literal secret; keep only the variable name")

    for marker in TEMP_IMAGE_MARKERS:
        if marker.lower() in text.lower():
            errors.append(f"{path}: contains forbidden temporary image reference {marker!r}")

    for raw_target in IMAGE_PATTERN.findall(text):
        target = normalize_image_target(raw_target)
        lowered = target.lower()
        if lowered.startswith(("http://", "https://")):
            warnings.append(f"{path}: external image is not repository-local: {target}")
            continue
        if lowered.startswith(("data:", "blob:")):
            continue
        if re.match(r"^[A-Za-z]:[\\/]", target) or target.startswith(("/", "\\")):
            errors.append(f"{path}: image must use a repository-relative path: {target}")
            continue
        image_path = (path.parent / target).resolve()
        if not image_path.is_file():
            errors.append(f"{path}: referenced image does not exist: {target}")

    counts = {term: text.count(term) for term in HIGH_RISK_TERMS if term in text}
    if counts:
        rendered = ", ".join(f"{term}={count}" for term, count in counts.items())
        warnings.append(f"{path}: manually re-verify high-risk claims ({rendered})")

    return errors, warnings


def main() -> int:
    args = parse_args()
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for document in args.documents:
        errors, warnings = validate_document(document.resolve(), args.allow_no_mermaid)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    for warning in all_warnings:
        print(f"WARN: {warning}")
    for error in all_errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if all_errors:
        print(f"FAIL: {len(all_errors)} error(s), {len(all_warnings)} warning(s)", file=sys.stderr)
        return 1
    print(f"PASS: {len(args.documents)} document(s), {len(all_warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
