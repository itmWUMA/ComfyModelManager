from pathlib import Path
from typing import Callable, Optional

import customtkinter as ctk
from PIL import Image

from src.models.model_scanner import ModelEntry
from src.utils.file_utils import file_size_display


class ModelCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        model: ModelEntry,
        on_open: Callable[[ModelEntry], None],
    ) -> None:
        super().__init__(master, fg_color="#21242b", corner_radius=14)
        self.model = model
        self.on_open = on_open
        self.image_label: Optional[ctk.CTkLabel] = None
        self.preview_image = None

        self._build()

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        image_frame = ctk.CTkFrame(self, fg_color="#1a1c21", corner_radius=10)
        image_frame.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="nsew")
        image_label = ctk.CTkLabel(image_frame, text="预览图")
        image_label.pack(expand=True, fill="both", padx=12, pady=24)
        self.image_label = image_label

        if self.model.preview:
            self._load_preview(Path(self.model.preview))

        name_label = ctk.CTkLabel(
            self,
            text=self.model.name,
            wraplength=180,
            justify="left",
            font=("Fira Sans", 13, "bold"),
        )
        name_label.grid(row=1, column=0, padx=12, sticky="w")

        size_label = ctk.CTkLabel(
            self,
            text=file_size_display(self.model.size_bytes),
            text_color="#a6adbb",
            font=("Fira Sans", 11),
        )
        size_label.grid(row=2, column=0, padx=12, pady=(0, 12), sticky="w")

        self.bind("<Button-1>", self._click)
        for child in self.winfo_children():
            child.bind("<Button-1>", self._click)
        if self.image_label:
            self.image_label.bind("<Button-1>", self._click)

    def _click(self, _event) -> None:
        self.on_open(self.model)

    def _load_preview(self, path: Path) -> None:
        if not path.exists():
            return
        image = Image.open(path)
        image.thumbnail((200, 200))
        self.preview_image = ctk.CTkImage(image, size=image.size)
        if self.image_label:
            self.image_label.configure(image=self.preview_image, text="")
