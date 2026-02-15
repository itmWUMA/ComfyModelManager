import unittest

from src.app import ComfyModelManagerApp
from src.models.model_scanner import ModelEntry


class TestComfyModelManagerApp(unittest.TestCase):
    def test_filter_models(self) -> None:
        app = ComfyModelManagerApp.__new__(ComfyModelManagerApp)
        app.selected_type = "checkpoints"
        app.selected_base = "SD 1.5"

        models = [
            ModelEntry(
                name="a",
                relative_path="a",
                absolute_path="a",
                size_bytes=1,
                model_type="checkpoints",
                base_model="SD 1.5",
            ),
            ModelEntry(
                name="b",
                relative_path="b",
                absolute_path="b",
                size_bytes=1,
                model_type="loras",
                base_model="SD 1.5",
            ),
            ModelEntry(
                name="c",
                relative_path="c",
                absolute_path="c",
                size_bytes=1,
                model_type="checkpoints",
                base_model="SDXL",
            ),
        ]

        filtered = app._filter_models(models)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].name, "a")


if __name__ == "__main__":
    unittest.main()
