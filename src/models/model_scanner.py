from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from src.config import AppConfig
from src.utils.file_utils import is_model_file, safe_relative_path


@dataclass
class ModelEntry:
    name: str
    relative_path: str
    absolute_path: str
    size_bytes: int
    model_type: str
    base_model: str
    repo_id: str = ""
    filename: str = ""
    preview: str = ""
    readme: str = ""


class ModelScanner:
    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def scan(self) -> List[ModelEntry]:
        models_root = Path(self.config.comfyui_models_dir)
        results: List[ModelEntry] = []
        if not models_root.exists():
            return results

        type_map = {item["id"]: item["label"] for item in self.config.model_types}
        for model_type_id in type_map.keys():
            type_dir = models_root / model_type_id
            if not type_dir.exists():
                continue
            for base_dir in type_dir.iterdir():
                if not base_dir.is_dir():
                    continue
                base_model = base_dir.name
                for file_path in base_dir.iterdir():
                    if file_path.is_file() and is_model_file(file_path):
                        relative = safe_relative_path(models_root, file_path)
                        entry = ModelEntry(
                            name=file_path.name,
                            relative_path=relative,
                            absolute_path=str(file_path),
                            size_bytes=file_path.stat().st_size,
                            model_type=model_type_id,
                            base_model=base_model,
                        )
                        self._apply_metadata(entry)
                        results.append(entry)
        return results

    def _apply_metadata(self, entry: ModelEntry) -> None:
        metadata = self.config.models_metadata.get(entry.relative_path)
        if not metadata:
            return
        entry.repo_id = metadata.get("repo_id", "")
        entry.filename = metadata.get("filename", "")
        entry.preview = metadata.get("preview", "")
        entry.readme = metadata.get("readme", "")
