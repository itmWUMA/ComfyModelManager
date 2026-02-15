from pathlib import Path
from typing import Callable

import customtkinter as ctk
from tkinter import filedialog


class SettingsDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        comfyui_dir: str,
        app_data_dir: str,
        hf_token: str,
        on_save: Callable[[str, str, str], None],
    ) -> None:
        super().__init__(master)
        self.on_save = on_save

        self.title("设置")
        self.geometry("520x360")
        self.configure(fg_color="#15171c")

        self.comfy_entry = ctk.CTkEntry(self)
        self.data_entry = ctk.CTkEntry(self)
        self.token_entry = ctk.CTkEntry(self, show="*")
        self.comfy_entry.insert(0, comfyui_dir)
        self.data_entry.insert(0, app_data_dir)
        self.token_entry.insert(0, hf_token)

        self._build()

    def _build(self) -> None:
        ctk.CTkLabel(self, text="设置", font=("Fira Sans", 16, "bold")).pack(
            pady=(16, 12)
        )

        path_row = ctk.CTkFrame(self, fg_color="#15171c")
        path_row.pack(fill="x", padx=24, pady=6)
        self.comfy_entry.pack(in_=path_row, side="left", fill="x", expand=True)
        ctk.CTkButton(path_row, text="浏览", width=80, command=self._pick_comfy).pack(
            side="left", padx=(8, 0)
        )

        data_row = ctk.CTkFrame(self, fg_color="#15171c")
        data_row.pack(fill="x", padx=24, pady=6)
        self.data_entry.pack(in_=data_row, side="left", fill="x", expand=True)
        ctk.CTkButton(data_row, text="浏览", width=80, command=self._pick_data).pack(
            side="left", padx=(8, 0)
        )

        self.token_entry.pack(fill="x", padx=24, pady=6)

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
            self.comfy_entry.delete(0, "end")
            self.comfy_entry.insert(0, folder)

    def _pick_data(self) -> None:
        folder = filedialog.askdirectory()
        if folder:
            self.data_entry.delete(0, "end")
            self.data_entry.insert(0, folder)

    def _save(self) -> None:
        comfy_dir = self.comfy_entry.get().strip()
        data_dir = self.data_entry.get().strip()
        token = self.token_entry.get().strip()
        if not comfy_dir:
            return
        if not data_dir:
            data_dir = str(Path("data"))
        self.on_save(comfy_dir, data_dir, token)
        self.destroy()
