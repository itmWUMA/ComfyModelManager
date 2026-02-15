import unittest
from pathlib import Path
import tempfile

from src.utils import file_utils


class TestFileUtils(unittest.TestCase):
    def test_is_model_file(self) -> None:
        self.assertTrue(file_utils.is_model_file(Path("model.safetensors")))
        self.assertTrue(file_utils.is_model_file(Path("model.CKPT")))
        self.assertFalse(file_utils.is_model_file(Path("model.txt")))

    def test_file_size_display(self) -> None:
        self.assertEqual(file_utils.file_size_display(0), "0 B")
        self.assertEqual(file_utils.file_size_display(1023), "1023 B")
        self.assertEqual(file_utils.file_size_display(1024), "1.0 KB")
        self.assertEqual(file_utils.file_size_display(1024 * 1024), "1.0 MB")

    def test_file_hash_and_text_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.txt"
            path.write_text("hello", encoding="utf-8")
            hash1 = file_utils.file_hash(path)
            hash2 = file_utils.file_hash(path)
            self.assertEqual(hash1, hash2)
            self.assertEqual(file_utils.text_hash("hello"), file_utils.text_hash("hello"))

    def test_safe_relative_path(self) -> None:
        root = Path("C:/root")
        path = Path("C:/root/sub/file.txt")
        self.assertEqual(file_utils.safe_relative_path(root, path), "sub/file.txt")
        other = Path("D:/other/file.txt")
        self.assertIn("other/file.txt", file_utils.safe_relative_path(root, other))

    def test_ensure_dir_and_list_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            target = base / "nested" / "dir"
            file_utils.ensure_dir(target)
            file_path = target / "file.txt"
            file_path.write_text("content", encoding="utf-8")
            files = list(file_utils.list_files(base))
            self.assertIn(file_path, files)

    def test_readable_path_parts(self) -> None:
        path = Path("C:/root/file.txt")
        name, full = file_utils.readable_path_parts(path)
        self.assertEqual(name, "file.txt")
        self.assertIn("/", full)


if __name__ == "__main__":
    unittest.main()
