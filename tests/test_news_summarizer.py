import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_news_app():
    path = ROOT / "01-news-summarizer-agent" / "app.py"
    spec = importlib.util.spec_from_file_location("news_app_for_tests", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NewsSummarizerCliTests(unittest.TestCase):
    def test_invalid_live_output_uses_safe_local_fallback(self) -> None:
        app = load_news_app()
        source = "Riverdale opened a community library with 5,000 books."
        injected_output = (
            "Headline\nMars colony discovers aliens\n\n"
            "Concise Summary\nColonists found life on Mars.\n\n"
            "Key Points\n- Scientists confirmed extraterrestrial life.\n\n"
            "Important Entities\n- Mars"
        )
        with mock.patch.object(app, "generate_text", return_value=injected_output):
            output, warning = app.generate_output(source, True, "test-model")

        self.assertIn("Mode: Local extractive fallback", output)
        self.assertIsNotNone(warning)
        self.assertIn("failed safety validation", warning)

    def test_news_cli_outputs_required_sections(self) -> None:
        source = (
            "Riverdale opened a solar-powered community library on Tuesday. "
            "The library includes 5,000 books and free digital-skills classes. "
            "Mayor Lina Ahmed said local volunteers helped design the program."
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "news.txt"
            input_path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "01-news-summarizer-agent" / "app.py"), str(input_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Headline", result.stdout)
        self.assertIn("Concise Summary", result.stdout)
        self.assertIn("Key Points", result.stdout)
        self.assertIn("Important Entities", result.stdout)
        self.assertIn("Riverdale", result.stdout)


if __name__ == "__main__":
    unittest.main()
