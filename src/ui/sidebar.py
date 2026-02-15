from typing import Callable, List, Tuple

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        model_types: List[Tuple[str, str]],
        on_select: Callable[[str], None],
        on_download: Callable[[], None],
    ) -> None:
        super().__init__(master, fg_color="#1e1f24")
        self.on_select = on_select
        self.buttons = {}

        title = ctk.CTkLabel(self, text="模型类型", font=("Fira Sans", 16, "bold"))
        title.pack(pady=(16, 8))

        for type_id, label in model_types:
            btn = ctk.CTkButton(
                self,
                text=label,
                width=140,
                fg_color="#2a2c33",
                hover_color="#3a3d46",
                command=lambda value=type_id: self._select(value),
            )
            btn.pack(pady=4, padx=12)
            self.buttons[type_id] = btn

        ctk.CTkLabel(self, text="", height=8).pack()

        download_btn = ctk.CTkButton(
            self,
            text="下载模型",
            fg_color="#5c824f",
            hover_color="#7aa76b",
            command=on_download,
        )
        download_btn.pack(side="bottom", pady=16, padx=12)

    def _select(self, value: str) -> None:
        for key, btn in self.buttons.items():
            if key == value:
                btn.configure(fg_color="#3d5a80")
            else:
                btn.configure(fg_color="#2a2c33")
        self.on_select(value)
