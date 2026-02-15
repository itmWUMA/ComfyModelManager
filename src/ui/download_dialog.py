import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List

import customtkinter as ctk

from src.services.hf_downloader import DownloadRequest, HFDownloader
from src.utils.file_utils import file_size_display, text_hash


@dataclass
class DownloadResult:
    success: bool
    message: str
    readme_path: str = ""
    model_path: str = ""


class DownloadDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        model_types: List[str],
        base_models: List[str],
        selected_type: str,
        selected_base: str,
        token: str,
        models_root: Path,
        app_data_dir: Path,
        on_request: Callable[[str], None],
        on_complete: Callable[[DownloadResult], None],
    ) -> None:
        super().__init__(master)
        self.downloader = HFDownloader()
        self.on_complete = on_complete
        self.token = token
        self.models_root = models_root
        self.app_data_dir = app_data_dir
        self.on_request = on_request

        self.title("下载模型")
        self.geometry("520x480")
        self.configure(fg_color="#14161b")

        self.progress_var = ctk.DoubleVar(value=0.0)
        self.progress_label_var = ctk.StringVar(value="0%")
        self.speed_label_var = ctk.StringVar(value="0 MB/s")
        self.size_label_var = ctk.StringVar(value="0 / 0")

        self.repo_entry = ctk.CTkEntry(self, placeholder_text="repo_id")
        self.filename_entry = ctk.CTkEntry(self, placeholder_text="文件名")
        self.type_option = ctk.CTkOptionMenu(self, values=model_types)
        self.base_option = ctk.CTkOptionMenu(self, values=base_models)
        if selected_type in model_types:
            self.type_option.set(selected_type)
        if selected_base in base_models:
            self.base_option.set(selected_base)

        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="Hugging Face 下载", font=("Fira Sans", 16, "bold")).pack(
            pady=(16, 12)
        )

        self.repo_entry.pack(fill="x", padx=24, pady=6)
        self.filename_entry.pack(fill="x", padx=24, pady=6)

        row = ctk.CTkFrame(self, fg_color="#14161b")
        row.pack(fill="x", padx=24, pady=6)
        self.type_option.pack(in_=row, side="left", expand=True, fill="x", padx=(0, 8))
        self.base_option.pack(in_=row, side="left", expand=True, fill="x")

        progress = ctk.CTkProgressBar(self, variable=self.progress_var)
        progress.pack(fill="x", padx=24, pady=(20, 4))

        info_row = ctk.CTkFrame(self, fg_color="#14161b")
        info_row.pack(fill="x", padx=24)
        ctk.CTkLabel(info_row, textvariable=self.progress_label_var).pack(side="left")
        ctk.CTkLabel(info_row, textvariable=self.speed_label_var).pack(side="right")
        ctk.CTkLabel(info_row, textvariable=self.size_label_var).pack(side="right", padx=12)

        actions = ctk.CTkFrame(self, fg_color="#14161b")
        actions.pack(fill="x", padx=24, pady=(16, 16))
        ctk.CTkButton(actions, text="开始下载", command=self._start).pack(
            side="left", padx=6
        )
        ctk.CTkButton(actions, text="取消", fg_color="#2a2c33", command=self._cancel).pack(
            side="left", padx=6
        )

    def _start(self) -> None:
        repo_id = self.repo_entry.get().strip()
        filename = self.filename_entry.get().strip()
        if not repo_id or not filename:
            self._complete(False, "repo_id 或文件名不能为空", None, None)
            return

        model_type = self.type_option.get()
        base_model = self.base_option.get()
        target_dir = self.models_root / model_type / base_model
        readme_root = self.app_data_dir / "readmes" / text_hash(repo_id)
        request = DownloadRequest(
            repo_id=repo_id,
            filename=filename,
            model_type=model_type,
            base_model=base_model,
            target_dir=target_dir,
            readme_dir=readme_root,
            token=self.token,
        )
        self.on_request(repo_id)
        self.downloader.download_async(
            request,
            progress_cb=self._progress,
            completion_cb=lambda success, message, readme, model: self._complete(
                success, message, readme, model
            ),
        )

    def _progress(self, downloaded: int, total: int, speed: float) -> None:
        total = max(total, 1)
        percent = downloaded / total
        self.progress_var.set(percent)
        self.progress_label_var.set(f"{percent * 100:.1f}%")
        self.speed_label_var.set(f"{file_size_display(int(speed))}/s")
        self.size_label_var.set(
            f"{file_size_display(downloaded)} / {file_size_display(total)}"
        )

    def _cancel(self) -> None:
        self.downloader.cancel()
        self._complete(False, "download_cancelled", None, None)

    def _complete(
        self,
        success: bool,
        message: str,
        readme_path: str | None,
        model_path: str | None,
    ) -> None:
        self.after(
            0,
            lambda: self.on_complete(
                DownloadResult(
                    success,
                    message,
                    readme_path or "",
                    model_path or "",
                )
            ),
        )
        if success:
            self.destroy()
