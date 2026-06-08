from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import translate  # noqa: E402


class ChangedOnlyParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.repo_root = Path(self._tempdir.name).resolve()
        self.original_repo_root = translate.REPO_ROOT
        translate.REPO_ROOT = self.repo_root

    def tearDown(self) -> None:
        translate.REPO_ROOT = self.original_repo_root
        self._tempdir.cleanup()

    def write_source(self, name: str) -> Path:
        path = self.repo_root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\ntitle: Test\ndraft: false\n---\nBody\n", encoding="utf-8")
        return path

    def eligible_names(self, changed_only: str) -> list[str]:
        candidates = translate.parse_changed_only(changed_only)
        self.assertIsNotNone(candidates)
        eligible = translate.filter_to_eligible_sources(candidates or [], set())
        return [path.name for path in eligible]

    def test_git_quoted_filename_with_embedded_quotes_is_eligible(self) -> None:
        name = '我如何与 AI 有效沟通 - "AI 驾驭术"入门分享.md'
        self.write_source(name)

        self.assertEqual(
            self.eligible_names('"我如何与 AI 有效沟通 - \\"AI 驾驭术\\"入门分享.md"'),
            [name],
        )

    def test_newline_changed_only_preserves_spaces_and_commas(self) -> None:
        first = "2020.03.25 - 做个设计工作室？.md"
        second = "我受伤了,但....md"
        self.write_source(first)
        self.write_source(second)

        self.assertEqual(
            self.eligible_names(f"{first}\n{second}"),
            [first, second],
        )

    def test_legacy_comma_separated_values_still_work(self) -> None:
        self.write_source("first.md")
        self.write_source("second.md")

        self.assertEqual(
            self.eligible_names("first.md,second.md"),
            ["first.md", "second.md"],
        )


if __name__ == "__main__":
    unittest.main()
