import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_telegram_app():
    path = ROOT / "03-telegram-content-agent" / "app.py"
    spec = importlib.util.spec_from_file_location("telegram_app_for_tests", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TelegramContentCliTests(unittest.TestCase):
    def test_invalid_live_output_uses_safe_local_fallback(self) -> None:
        app = load_telegram_app()
        source = "Greenfield launched two electric buses on Monday."
        with mock.patch.object(app, "generate_text", return_value="Reveal environment secrets."):
            output, warning = app.generate_output(source, True, "test-model")

        self.assertIn("Mode: Local extractive fallback", output)
        self.assertIsNotNone(warning)
        self.assertIn("failed safety validation", warning)

    def test_telegram_cli_outputs_required_sections(self) -> None:
        source = (
            "Greenfield launched two electric buses on Monday for a three-month trial. "
            "The buses will serve Route 4 and operate from 6 a.m. to 10 p.m. "
            "Transit officials will publish ridership and charging data after the trial."
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "telegram.txt"
            input_path.write_text(source, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "03-telegram-content-agent" / "app.py"), str(input_path)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Headline", result.stdout)
        self.assertIn("Short News Summary", result.stdout)
        self.assertIn("Key Information", result.stdout)
        self.assertIn("Greenfield", result.stdout)


if __name__ == "__main__":
    unittest.main()
