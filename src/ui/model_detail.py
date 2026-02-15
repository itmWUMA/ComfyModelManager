import os
import subprocess
from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image

from src.models.model_scanner import ModelEntry
from src.utils.file_utils import file_size_display, list_files, text_hash


class ModelDetailDialog(ctk.CTkToplevel):
    def __init__(
        self,
        master,
        model: ModelEntry,
        app_data_dir: str,
        on_preview: Callable[[ModelEntry], None],
        on_delete: Callable[[ModelEntry], None],
        on_save_notes: Callable[[ModelEntry, str], None],
    ) -> None:
        super().__init__(master)
        self.model = model
        self.app_data_dir = Path(app_data_dir)
        self.on_preview = on_preview
        self.on_delete = on_delete
        self.on_save_notes = on_save_notes
        self.preview_image = None
        self.notes_box = None

        self.title("模型详情")
        self.geometry("820x620")
        self.configure(fg_color="#121419")

        self._build()

    def _build(self) -> None:
        header = ctk.CTkLabel(
            self,
            text=self.model.name,
            font=("Fira Sans", 18, "bold"),
        )
        header.pack(pady=(16, 8))

        content = ctk.CTkFrame(self, fg_color="#1a1d23", corner_radius=16)
        content.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        left = ctk.CTkFrame(content, fg_color="#111318", corner_radius=14)
        left.pack(side="left", fill="y", padx=16, pady=16)

        preview_label = ctk.CTkLabel(left, text="预览图")
        preview_label.pack(padx=12, pady=12)

        if self.model.preview:
            path = Path(self.model.preview)
            if path.exists():
                image = Image.open(path)
                image.thumbnail((280, 280))
                self.preview_image = ctk.CTkImage(image, size=image.size)
                preview_label.configure(image=self.preview_image, text="")

        info_frame = ctk.CTkFrame(content, fg_color="#1a1d23")
        info_frame.pack(side="left", fill="both", expand=True, padx=(0, 16), pady=16)

        info_text = (
            f"文件名: {self.model.name}\n"
            f"大小: {file_size_display(self.model.size_bytes)}\n"
            f"类型: {self.model.model_type}\n"
            f"基底模型: {self.model.base_model}\n"
            f"路径: {self.model.absolute_path}"
        )
        ctk.CTkLabel(info_frame, text=info_text, justify="left").pack(
            anchor="w", padx=12, pady=(12, 8)
        )

        readme_text = self._read_readme()
        readme_box = ctk.CTkTextbox(info_frame, wrap="word", height=220)
        readme_box.insert("1.0", readme_text)
        readme_box.configure(state="disabled")
        readme_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        notes_label = ctk.CTkLabel(info_frame, text="用途提示")
        notes_label.pack(anchor="w", padx=12, pady=(0, 6))

        self.notes_box = ctk.CTkTextbox(info_frame, wrap="word", height=90)
        self.notes_box.insert("1.0", self.model.notes)
        self.notes_box.pack(fill="x", padx=12, pady=(0, 12))

        actions = ctk.CTkFrame(self, fg_color="#121419")
        actions.pack(fill="x", padx=16, pady=(0, 16))

        ctk.CTkButton(
            actions,
            text="保存用途提示",
            fg_color="#345995",
            hover_color="#4369ad",
            command=self._save_notes,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="更换预览图",
            fg_color="#3d5a80",
            hover_color="#5374a6",
            command=lambda: self.on_preview(self.model),
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="打开目录",
            fg_color="#2f3e46",
            hover_color="#3d4f59",
            command=self._open_folder,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="删除模型",
            fg_color="#9e2a2b",
            hover_color="#bc4749",
            command=lambda: self.on_delete(self.model),
        ).pack(side="right", padx=6)

    def _save_notes(self) -> None:
        if not self.notes_box:
            return
        self.model.notes = self.notes_box.get("1.0", "end").strip()
        self.on_save_notes(self.model, self.model.notes)

    def _open_folder(self) -> None:
        path = Path(self.model.absolute_path).parent
        if os.name == "nt":
            subprocess.Popen(["explorer", str(path)])
        elif os.name == "posix":
            subprocess.Popen(["xdg-open", str(path)])

    def _read_readme(self) -> str:
        readme_path, state, diagnostic_path = self._resolve_readme_path()
        if not readme_path:
            return self._format_readme_state(state, diagnostic_path)
        content = readme_path.read_text(encoding="utf-8", errors="ignore")
        return self._format_readme_state(content, diagnostic_path)

    def _resolve_readme_path(self) -> tuple[Path | None, str, str]:
        roots: list[Path] = []
        if self.model.repo_id:
            roots.append(self.app_data_dir / "readmes" / text_hash(self.model.repo_id))
        if self.model.readme:
            roots.append(Path(self.model.readme))

        if not roots:
            return None, "README 未下载", ""

        last_checked = ""
        saw_existing_root = False
        for root in roots:
            root = Path(str(root))
            if not root.is_absolute() and (self.app_data_dir / root).exists():
                root = self.app_data_dir / root

            if not root.exists():
                last_checked = str(root)
                continue
            saw_existing_root = True
            if root.is_file():
                if root.name.lower() == "readme.md":
                    return root, "", str(root)
                last_checked = str(root)
                continue
            readme_path = self._find_readme_file(root)
            if readme_path:
                return readme_path, "", str(readme_path)
            last_checked = str(root)

        if saw_existing_root:
            return None, "已下载但未找到 README", last_checked
        return None, "README 未下载", last_checked

    def _find_readme_file(self, root: Path) -> Path | None:
        if not root.is_dir():
            return None
        candidates = [path for path in list_files(root) if path.name.lower() == "readme.md"]
        if not candidates:
            return None
        return sorted(candidates, key=lambda item: str(item))[0]

    def _format_readme_state(self, content: str, diagnostic_path: str) -> str:
        if diagnostic_path:
            return f"{content}\n\n诊断: 已检查 {diagnostic_path}"
        return content
