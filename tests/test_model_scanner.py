import unittest
from pathlib import Path
import tempfile

from src.config import AppConfig
from src.models.model_scanner import ModelScanner


class TestModelScanner(unittest.TestCase):
    def test_scan_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AppConfig(comfyui_models_dir=temp_dir)
            scanner = ModelScanner(config)
            results = scanner.scan()
            self.assertEqual(results, [])

    def test_scan_discovers_models_with_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            model_path = root / "checkpoints" / "SD 1.5" / "model.safetensors"
            model_path.parent.mkdir(parents=True, exist_ok=True)
            model_path.write_bytes(b"data")

            config = AppConfig(comfyui_models_dir=str(root))
            relative = "checkpoints/SD 1.5/model.safetensors"
            config.models_metadata[relative] = {
                "repo_id": "user/repo",
                "filename": "model.safetensors",
                "preview": "preview.png",
                "readme": "README.md",
                "notes": "用途提示",
            }
            scanner = ModelScanner(config)
            results = scanner.scan()
            self.assertEqual(len(results), 1)
            entry = results[0]
            self.assertEqual(entry.relative_path, relative)
            self.assertEqual(entry.repo_id, "user/repo")
            self.assertEqual(entry.preview, "preview.png")
            self.assertEqual(entry.readme, "README.md")
            self.assertEqual(entry.notes, "用途提示")


if __name__ == "__main__":
    unittest.main()
