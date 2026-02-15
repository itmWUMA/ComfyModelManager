import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile

from src.services.hf_downloader import DownloadRequest, HFDownloader


class TestHFDownloader(unittest.TestCase):
    def test_progress_callback_and_download(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target_dir = Path(temp_dir)
            request = DownloadRequest(
                repo_id="user/repo",
                filename="model.bin",
                model_type="checkpoints",
                base_model="SD 1.5",
                target_dir=target_dir,
            )

            response = Mock()
            response.headers = {"Content-Length": "3"}
            response.iter_content.return_value = [b"a", b"b", b"c"]
            response.raise_for_status = Mock()

            progress_calls = []

            def progress_cb(downloaded: int, total: int, speed: float) -> None:
                progress_calls.append((downloaded, total))

            downloader = HFDownloader()

            with patch("src.services.hf_downloader.requests.get", return_value=response):
                with patch("src.services.hf_downloader.hf_hub_url", return_value="http://example"):
                    path = downloader._download_with_progress(request, progress_cb)

            self.assertTrue(Path(path).exists())
            self.assertEqual(Path(path).read_bytes(), b"abc")
            self.assertEqual(progress_calls[-1][0], 3)

    def test_download_readme_handles_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            request = DownloadRequest(
                repo_id="user/repo",
                filename="model.bin",
                model_type="checkpoints",
                base_model="SD 1.5",
                target_dir=Path(temp_dir),
            )

            api = Mock()
            api.repo_info.side_effect = Exception("fail")

            with patch("src.services.hf_downloader.HfApi", return_value=api):
                with patch("src.services.hf_downloader.hf_hub_download", side_effect=Exception("fail")):
                    downloader = HFDownloader()
                    result = downloader._download_readme(request)

            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
