from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_module_doc import find_fence_errors, validate_document


VALID_DOCUMENT = """# 限流模块

## 架构

~~~mermaid
flowchart LR
    A --> B
~~~

![架构图](assets/rate-limit.png)

## 覆盖台账

| 类别 | 证据 |
|---|---|
| 入口 | `EntryRateLimiter` |
"""


class FenceValidationTest(unittest.TestCase):
    def test_accepts_matching_backtick_and_tilde_fences(self) -> None:
        self.assertEqual([], find_fence_errors(["```java", "x", "```"]))
        self.assertEqual([], find_fence_errors(["~~~~mermaid", "A --> B", "~~~~"]))

    def test_rejects_mismatched_fence_types(self) -> None:
        errors = find_fence_errors(["```java", "x", "~~~"])

        self.assertEqual(["unclosed '```' fence opened on line 1"], errors)


class DocumentValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_directory.name)

    def tearDown(self) -> None:
        self.temp_directory.cleanup()

    def write_document(self, content: str) -> Path:
        document = self.root / "module.md"
        document.write_text(content, encoding="utf-8")
        return document

    def test_accepts_valid_document_and_existing_relative_image(self) -> None:
        assets = self.root / "assets"
        assets.mkdir()
        (assets / "rate-limit.png").write_bytes(b"png-test-double")
        document = self.write_document(VALID_DOCUMENT)

        errors, warnings = validate_document(document, allow_no_mermaid=False)

        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_rejects_missing_mermaid_placeholder_and_missing_image(self) -> None:
        document = self.write_document(
            "# 模块\n\n![图](assets/missing.png)\n\n## 覆盖台账\n\n待回填\n"
        )

        errors, _ = validate_document(document, allow_no_mermaid=False)

        rendered = "\n".join(errors)
        self.assertIn("missing a Mermaid", rendered)
        self.assertIn("unresolved placeholder", rendered)
        self.assertIn("referenced image does not exist", rendered)

    def test_rejects_literal_secret_temporary_image_and_trailing_space(self) -> None:
        document = self.write_document(
            "# 模块  \n\n```mermaid\nA --> B\n```\n\n"
            "![图](data:image/png;base64,abc)\n\n## 证据索引\n\n"
            "Authorization: Bearer abcdefghijklmnopqrstuvwxyz\n"
        )

        errors, _ = validate_document(document, allow_no_mermaid=False)

        rendered = "\n".join(errors)
        self.assertIn("trailing whitespace", rendered)
        self.assertIn("possible literal secret", rendered)
        self.assertIn("forbidden temporary image reference", rendered)


if __name__ == "__main__":
    unittest.main()
