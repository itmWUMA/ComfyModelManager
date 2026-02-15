from typing import Callable, List

import customtkinter as ctk


class Topbar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        base_models: List[str],
        on_select: Callable[[str], None],
    ) -> None:
        super().__init__(master, fg_color="#15161a")
        self.on_select = on_select
        self.buttons = {}

        for base in base_models:
            btn = ctk.CTkButton(
                self,
                text=base,
                height=32,
                fg_color="#23242b",
                hover_color="#343641",
                command=lambda value=base: self._select(value),
            )
            btn.pack(side="left", padx=6, pady=12)
            self.buttons[base] = btn

    def _select(self, value: str) -> None:
        for key, btn in self.buttons.items():
            if key == value:
                btn.configure(fg_color="#4f5d2f")
            else:
                btn.configure(fg_color="#23242b")
        self.on_select(value)
