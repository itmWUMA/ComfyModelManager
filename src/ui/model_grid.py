from typing import Callable, List

import customtkinter as ctk

from src.models.model_scanner import ModelEntry
from src.ui.model_card import ModelCard


class ModelGrid(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        on_open: Callable[[ModelEntry], None],
    ) -> None:
        super().__init__(master, fg_color="#0f1013")
        self.on_open = on_open
        self.cards: List[ModelCard] = []
        self.column_count = 3

    def update_models(self, models: List[ModelEntry]) -> None:
        for card in self.cards:
            card.destroy()
        self.cards = []

        if not models:
            empty_label = ctk.CTkLabel(
                self,
                text="暂无模型",
                font=("Fira Sans", 16),
                text_color="#a6adbb",
            )
            empty_label.grid(row=0, column=0, padx=20, pady=20)
            return

        for index, model in enumerate(models):
            card = ModelCard(self, model, self.on_open)
            row = index // self.column_count
            col = index % self.column_count
            card.grid(row=row, column=col, padx=12, pady=12, sticky="nsew")
            self.cards.append(card)
        for col in range(self.column_count):
            self.grid_columnconfigure(col, weight=1)
