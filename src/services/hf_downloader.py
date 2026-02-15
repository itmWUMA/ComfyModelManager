import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import requests
from huggingface_hub import HfApi, hf_hub_download, hf_hub_url


ProgressCallback = Callable[[int, int, float], None]
CompletionCallback = Callable[[bool, str, Optional[str], Optional[str]], None]


@dataclass
class DownloadRequest:
    repo_id: str
    filename: str
    model_type: str
    base_model: str
    target_dir: Path
    readme_dir: Optional[Path] = None
    token: str = ""


class HFDownloader:
    def __init__(self) -> None:
        self._cancelled = False

    def download_async(
        self,
        request: DownloadRequest,
        progress_cb: Optional[ProgressCallback] = None,
        completion_cb: Optional[CompletionCallback] = None,
    ) -> threading.Thread:
        thread = threading.Thread(
            target=self._download,
            args=(request, progress_cb, completion_cb),
            daemon=True,
        )
        thread.start()
        return thread

    def cancel(self) -> None:
        self._cancelled = True

    def _download(
        self,
        request: DownloadRequest,
        progress_cb: Optional[ProgressCallback],
        completion_cb: Optional[CompletionCallback],
    ) -> None:
        self._cancelled = False
        try:
            request.target_dir.mkdir(parents=True, exist_ok=True)
            model_path = self._download_with_progress(request, progress_cb)
            if self._cancelled:
                if completion_cb:
                    completion_cb(False, "download_cancelled", None, None)
                return

            readme_path = self._download_readme(request)
            if completion_cb:
                completion_cb(True, "", readme_path, model_path)
        except Exception as exc:
            if completion_cb:
                completion_cb(False, str(exc), None, None)

    def _progress(
        self,
        total: int,
        downloaded: int,
        speed: float,
        callback: Optional[ProgressCallback],
    ) -> None:
        if self._cancelled:
            raise RuntimeError("download_cancelled")
        if callback:
            callback(downloaded, total, speed)

    def _download_with_progress(
        self, request: DownloadRequest, progress_cb: Optional[ProgressCallback]
    ) -> str:
        target_path = request.target_dir / request.filename
        headers = {}
        if request.token:
            headers["Authorization"] = f"Bearer {request.token}"

        url = hf_hub_url(repo_id=request.repo_id, filename=request.filename)
        response = requests.get(url, headers=headers, stream=True, timeout=30)
        response.raise_for_status()

        total = int(response.headers.get("Content-Length", "0"))
        downloaded = 0
        start = time.time()
        with target_path.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 512):
                if self._cancelled:
                    target_path.unlink(missing_ok=True)
                    raise RuntimeError("download_cancelled")
                if not chunk:
                    continue
                handle.write(chunk)
                downloaded += len(chunk)
                if progress_cb:
                    elapsed = max(0.1, time.time() - start)
                    speed = downloaded / elapsed
                    self._progress(total, downloaded, speed, progress_cb)
        return str(target_path)

    def _download_readme(self, request: DownloadRequest) -> Optional[str]:
        api = HfApi(token=request.token or None)
        readme_name = None
        try:
            repo_info = api.repo_info(repo_id=request.repo_id)
            for sibling in repo_info.siblings or []:
                if sibling.rfilename.lower() == "readme.md":
                    readme_name = sibling.rfilename
                    break
        except Exception:
            readme_name = "README.md"

        if not readme_name:
            return None

        readme_dir = request.readme_dir or (request.target_dir / "readmes")
        readme_dir.mkdir(parents=True, exist_ok=True)
        try:
            path = hf_hub_download(
                repo_id=request.repo_id,
                filename=readme_name,
                cache_dir=str(readme_dir),
                token=request.token or None,
            )
        except Exception:
            return None
        return path
