from pathlib import Path
from typing import Callable

import customtkinter as ctk
from tkinter import filedialog

from src.config import default_app_data_dir


class SettingsDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        comfyui_dir: str,
        app_data_dir: str,
        hf_token: str,
        on_save: Callable[[str, str, str], None],
        on_close: Callable[[], None],
    ) -> None:
        super().__init__(master)
        self.on_save = on_save
        self.on_close = on_close

        self.title("设置")
        self.geometry("560x560")
        self.configure(fg_color="#15171c")
        self.protocol("WM_DELETE_WINDOW", self._close)

        self.comfy_entry = ctk.CTkEntry(
            self, placeholder_text="例如: D:\\ComfyUI\\models"
        )
        self.data_entry = ctk.CTkEntry(
            self, placeholder_text="例如: D:\\ComfyModelManager\\data"
        )
        self.token_entry = ctk.CTkEntry(self, show="*")
        self.comfy_entry.insert(0, comfyui_dir)
        self.data_entry.insert(0, app_data_dir)
        self.token_entry.insert(0, hf_token)
        self.comfyui_dir = comfyui_dir
        self.app_data_dir = app_data_dir

        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="设置", font=("Fira Sans", 16, "bold")).pack(
            pady=(16, 12)
        )

        ctk.CTkLabel(
            self,
            text="ComfyUI 模型目录",
            font=("Fira Sans", 12, "bold"),
            text_color="#e0e6f1",
        ).pack(anchor="w", padx=24, pady=(0, 4))
        path_row = ctk.CTkFrame(self, fg_color="#15171c")
        path_row.pack(fill="x", padx=24, pady=(0, 4))
        self.comfy_entry.pack(in_=path_row, side="left", fill="x", expand=True)
        ctk.CTkButton(path_row, text="浏览", width=80, command=self._pick_comfy).pack(
            side="left", padx=(8, 0)
        )
        ctk.CTkLabel(
            self,
            text="选择包含模型(checkpoints等)的文件夹",
            font=("Fira Sans", 11),
            text_color="#9aa3b2",
        ).pack(anchor="w", padx=24)
        self.comfy_error = ctk.CTkLabel(
            self, text="", font=("Fira Sans", 11), text_color="#d67067"
        )
        self.comfy_error.pack(anchor="w", padx=24, pady=(0, 6))

        self.comfy_current = ctk.CTkLabel(
            self,
            text=f"当前: {self.comfyui_dir if self.comfyui_dir else '未设置'}",
            font=("Fira Sans", 11),
            text_color="#7c8799",
        )
        self.comfy_current.pack(anchor="w", padx=24, pady=(0, 8))

        ctk.CTkLabel(
            self,
            text="应用数据目录",
            font=("Fira Sans", 12, "bold"),
            text_color="#e0e6f1",
        ).pack(anchor="w", padx=24, pady=(6, 4))
        data_row = ctk.CTkFrame(self, fg_color="#15171c")
        data_row.pack(fill="x", padx=24, pady=(0, 4))
        self.data_entry.pack(in_=data_row, side="left", fill="x", expand=True)
        ctk.CTkButton(data_row, text="浏览", width=80, command=self._pick_data).pack(
            side="left", padx=(8, 0)
        )
        ctk.CTkLabel(
            self,
            text="选择用于缓存与预览的文件夹",
            font=("Fira Sans", 11),
            text_color="#9aa3b2",
        ).pack(anchor="w", padx=24)
        self.data_error = ctk.CTkLabel(
            self, text="", font=("Fira Sans", 11), text_color="#d67067"
        )
        self.data_error.pack(anchor="w", padx=24, pady=(0, 6))

        self.data_current = ctk.CTkLabel(
            self,
            text=f"当前: {self.app_data_dir if self.app_data_dir else '未设置'}",
            font=("Fira Sans", 11),
            text_color="#7c8799",
        )
        self.data_current.pack(anchor="w", padx=24, pady=(0, 8))

        ctk.CTkLabel(
            self,
            text="Hugging Face Token",
            font=("Fira Sans", 12, "bold"),
            text_color="#e0e6f1",
        ).pack(anchor="w", padx=24, pady=(6, 4))
        self.token_entry.pack(fill="x", padx=24, pady=(0, 6))

        ctk.CTkButton(
            self,
            text="保存",
            fg_color="#3d5a80",
            hover_color="#5374a6",
            command=self._save,
        ).pack(pady=16)

    def _pick_comfy(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self._apply_directory(self.comfy_entry, self.comfy_error, folder)
        self._bring_to_front()

    def _pick_data(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self._apply_directory(self.data_entry, self.data_error, folder)
        self._bring_to_front()

    def _bring_to_front(self) -> None:
        self.lift()
        self.focus_force()

    def _apply_directory(
        self, entry: ctk.CTkEntry, error_label: ctk.CTkLabel, value: str
    ) -> None:
        entry.delete(0, "end")
        entry.insert(0, value)
        self._validate_directory(value, error_label)
        self._update_current(entry, value)

    def _update_current(self, entry: ctk.CTkEntry, value: str) -> None:
        display = value if value else "未设置"
        if entry is self.comfy_entry:
            self.comfy_current.configure(text=f"当前: {display}")
            self.comfyui_dir = value
        elif entry is self.data_entry:
            self.data_current.configure(text=f"当前: {display}")
            self.app_data_dir = value

    def _validate_directory(self, value: str, error_label: ctk.CTkLabel) -> bool:
        if not value:
            error_label.configure(text="")
            return True
        if not Path(value).is_dir():
            error_label.configure(text="需要选择文件夹路径。")
            return False
        error_label.configure(text="")
        return True

    def _save(self) -> None:
        comfy_dir = self.comfy_entry.get().strip()
        data_dir = self.data_entry.get().strip()
        token = self.token_entry.get().strip()
        if not comfy_dir:
            self.comfy_error.configure(text="请填写 ComfyUI 模型目录。")
            return
        comfy_valid = self._validate_directory(comfy_dir, self.comfy_error)
        data_valid = self._validate_directory(data_dir, self.data_error)
        if not comfy_valid or not data_valid:
            return
        if not data_dir:
            data_dir = str(default_app_data_dir())
        self.on_save(comfy_dir, data_dir, token)
        self._close()

    def _close(self) -> None:
        self.on_close()
        self.destroy()
