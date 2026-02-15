import os
from pathlib import Path
from typing import List

import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.config import AppConfig, ConfigManager
from src.models.model_scanner import ModelEntry, ModelScanner
from src.ui.download_dialog import DownloadDialog, DownloadResult
from src.ui.model_detail import ModelDetailDialog
from src.ui.model_grid import ModelGrid
from src.ui.sidebar import Sidebar
from src.ui.settings_dialog import SettingsDialog
from src.ui.topbar import Topbar
from src.utils.file_utils import file_hash, safe_relative_path, text_hash


class ComfyModelManagerApp:
    def __init__(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.root = ctk.CTk()
        self.root.title("ComfyModelManager")
        self.root.geometry("1200x780")
        self.root.configure(fg_color="#0b0c10")

        self.config_manager = ConfigManager(Path("data") / "config.json")
        self.config = self.config_manager.load()

        self.selected_type = self.config.model_types[0]["id"]
        self.selected_base = self.config.base_models[0]

        self.sidebar = None
        self.topbar = None
        self.grid = None
        self._last_download_repo = ""

        self._build_layout()
        self._load_models()

        if not self.config.comfyui_models_dir:
            self._open_settings()

    def run(self) -> None:
        self.root.mainloop()

    def _build_layout(self) -> None:
        header = ctk.CTkFrame(self.root, fg_color="#0b0c10")
        header.pack(fill="x")

        title = ctk.CTkLabel(
            header, text="ComfyModelManager", font=("Fira Sans", 20, "bold")
        )
        title.pack(side="left", padx=20, pady=16)

        ctk.CTkButton(
            header,
            text="设置",
            fg_color="#3d5a80",
            hover_color="#5374a6",
            command=self._open_settings,
        ).pack(side="right", padx=20, pady=12)

        body = ctk.CTkFrame(self.root, fg_color="#0b0c10")
        body.pack(fill="both", expand=True)

        type_pairs = [(item["id"], item["label"]) for item in self.config.model_types]
        self.sidebar = Sidebar(body, type_pairs, self._on_type_select, self._open_download)
        self.sidebar.pack(side="left", fill="y")

        content = ctk.CTkFrame(body, fg_color="#0b0c10")
        content.pack(side="left", fill="both", expand=True)

        self.topbar = Topbar(content, self.config.base_models, self._on_base_select)
        self.topbar.pack(fill="x")

        self.grid = ModelGrid(content, self._open_detail)
        self.grid.pack(fill="both", expand=True, padx=12, pady=12)

        if self.sidebar:
            self.sidebar._select(self.selected_type)
        if self.topbar:
            self.topbar._select(self.selected_base)

    def _open_settings(self) -> None:
        SettingsDialog(
            self.root,
            self.config.comfyui_models_dir,
            self.config.app_data_dir,
            self.config.hf_token,
            self._save_settings,
        )

    def _save_settings(self, comfy_dir: str, app_data_dir: str, token: str) -> None:
        self.config.comfyui_models_dir = comfy_dir
        self.config.app_data_dir = app_data_dir
        self.config.hf_token = token
        self.config.ensure_app_dirs()
        self.config_manager.save()
        self._load_models()

    def _load_models(self) -> None:
        scanner = ModelScanner(self.config)
        models = scanner.scan()
        filtered = self._filter_models(models)
        if self.grid:
            self.grid.update_models(filtered)

    def _filter_models(self, models: List[ModelEntry]) -> List[ModelEntry]:
        return [
            model
            for model in models
            if model.model_type == self.selected_type
            and model.base_model == self.selected_base
        ]

    def _on_type_select(self, model_type: str) -> None:
        self.selected_type = model_type
        self._load_models()

    def _on_base_select(self, base_model: str) -> None:
        self.selected_base = base_model
        self._load_models()

    def _open_download(self) -> None:
        if not self.config.comfyui_models_dir:
            messagebox.showerror("配置缺失", "请先在设置中配置 ComfyUI 模型目录")
            return
        if not self.config.app_data_dir:
            messagebox.showerror("配置缺失", "请先在设置中配置应用数据目录")
            return
        dialog = DownloadDialog(
            self.root,
            [item["id"] for item in self.config.model_types],
            self.config.base_models,
            self.config.hf_token,
            Path(self.config.comfyui_models_dir),
            Path(self.config.app_data_dir),
            self._set_last_download_repo,
            self._download_complete,
        )
        dialog.grab_set()

    def _download_complete(self, result: DownloadResult) -> None:
        if not result.success:
            messagebox.showerror("下载失败", result.message)
            return
        if result.model_path:
            relative = safe_relative_path(
                Path(self.config.comfyui_models_dir), Path(result.model_path)
            )
            readme_path = result.readme_path
            if readme_path:
                readme_path = str(Path(readme_path))
            self.config.add_metadata(
                relative_path=relative,
                repo_id=self._last_download_repo,
                filename=Path(result.model_path).name,
                readme_path=readme_path or "",
            )
            self.config_manager.save()
        messagebox.showinfo("下载完成", "模型下载完成")
        self._load_models()

    def _set_last_download_repo(self, repo_id: str) -> None:
        self._last_download_repo = repo_id

    def _open_detail(self, model: ModelEntry) -> None:
        dialog = ModelDetailDialog(
            self.root,
            model,
            self._update_preview,
            self._delete_model,
        )
        dialog.grab_set()

    def _update_preview(self, model: ModelEntry) -> None:
        path = filedialog.askopenfilename(
            title="选择预览图",
            filetypes=[("Image", "*.png;*.jpg;*.jpeg")],
        )
        if not path:
            return
        preview_dir = Path(self.config.app_data_dir) / "previews"
        preview_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"{file_hash(Path(path))}.png"
        target = preview_dir / file_name
        if not target.exists():
            with open(path, "rb") as source:
                target.write_bytes(source.read())
        relative = safe_relative_path(Path(self.config.app_data_dir), target)
        self.config.set_preview(model.relative_path, str(Path(self.config.app_data_dir) / relative))
        self.config_manager.save()
        self._load_models()

    def _delete_model(self, model: ModelEntry) -> None:
        if not messagebox.askyesno("确认", "确定删除该模型文件吗？"):
            return
        try:
            os.remove(model.absolute_path)
        except OSError:
            messagebox.showerror("失败", "无法删除模型文件")
            return
        if model.relative_path in self.config.models_metadata:
            self.config.models_metadata.pop(model.relative_path)
            self.config_manager.save()
        self._load_models()
