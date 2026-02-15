import json
import unittest
from pathlib import Path
import tempfile

from src.config import AppConfig, ConfigManager, DEFAULT_BASE_MODELS, DEFAULT_MODEL_TYPES


class TestAppConfig(unittest.TestCase):
    def test_to_from_dict_roundtrip(self) -> None:
        config = AppConfig(
            comfyui_models_dir="C:/models",
            app_data_dir="C:/data",
            hf_token="token",
            model_types=list(DEFAULT_MODEL_TYPES),
            base_models=list(DEFAULT_BASE_MODELS),
            models_metadata={"a": {"repo_id": "repo", "filename": "file"}},
        )
        payload = config.to_dict()
        restored = AppConfig.from_dict(payload)
        self.assertEqual(restored.comfyui_models_dir, "C:/models")
        self.assertEqual(restored.app_data_dir, "C:/data")
        self.assertEqual(restored.hf_token, "token")
        self.assertEqual(restored.model_types, list(DEFAULT_MODEL_TYPES))
        self.assertEqual(restored.base_models, list(DEFAULT_BASE_MODELS))
        self.assertEqual(restored.models_metadata, {"a": {"repo_id": "repo", "filename": "file"}})

    def test_ensure_app_dirs_and_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config = AppConfig(app_data_dir=temp_dir)
            config.ensure_app_dirs()
            base = Path(temp_dir)
            self.assertTrue((base / "readmes").exists())
            self.assertTrue((base / "previews").exists())

            config.add_metadata("rel", "repo", "file.safetensors", "readme.md")
            self.assertIn("rel", config.models_metadata)
            config.set_preview("rel", "preview.png")
            self.assertEqual(config.models_metadata["rel"]["preview"], "preview.png")


class TestConfigManager(unittest.TestCase):
    def test_load_save_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            manager = ConfigManager(config_path)
            config = manager.load()
            self.assertTrue(config_path.exists())
            config.comfyui_models_dir = "C:/models"
            manager.save()
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["comfyui_models_dir"], "C:/models")

    def test_update_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            manager = ConfigManager(config_path)
            manager.load()
            manager.update_paths("C:/models", "C:/data")
            self.assertEqual(manager.config.comfyui_models_dir, "C:/models")
            self.assertEqual(manager.config.app_data_dir, "C:/data")


if __name__ == "__main__":
    unittest.main()
