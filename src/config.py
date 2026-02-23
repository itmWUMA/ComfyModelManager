import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


MODEL_DIR_CHECKPOINTS = "checkpoints"
MODEL_DIR_LORAS = "loras"
MODEL_DIR_VAE = "vae"
MODEL_DIR_CONTROLNET = "controlnet"
MODEL_DIR_CLIP = "clip"
MODEL_DIR_UPSCALE = "upscale_models"
MODEL_DIR_EMBEDDINGS = "embeddings"

DEFAULT_MODEL_TYPES = [
    {"id": MODEL_DIR_CHECKPOINTS, "label": "Checkpoint"},
    {"id": MODEL_DIR_LORAS, "label": "LoRA"},
    {"id": MODEL_DIR_VAE, "label": "VAE"},
    {"id": MODEL_DIR_CONTROLNET, "label": "ControlNet"},
    {"id": MODEL_DIR_CLIP, "label": "CLIP"},
    {"id": MODEL_DIR_UPSCALE, "label": "Upscaler"},
    {"id": MODEL_DIR_EMBEDDINGS, "label": "Embedding"},
]

DEFAULT_BASE_MODELS = ["SD 1.5", "SDXL", "FLUX", "SD 3.x", "Kolors", "HunyuanDiT"]


def default_app_data_dir() -> Path:
    return Path.home() / ".comfy-model-manager" / "data"


def default_config_path() -> Path:
    return default_app_data_dir() / "config.json"


@dataclass
class AppConfig:
    comfyui_models_dir: str = ""
    app_data_dir: str = str(default_app_data_dir())
    hf_token: str = ""
    model_types: List[Dict[str, str]] = field(default_factory=lambda: list(DEFAULT_MODEL_TYPES))
    base_models: List[str] = field(default_factory=lambda: list(DEFAULT_BASE_MODELS))
    models_metadata: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "comfyui_models_dir": self.comfyui_models_dir,
            "app_data_dir": self.app_data_dir,
            "hf_token": self.hf_token,
            "model_types": self.model_types,
            "base_models": self.base_models,
            "models_metadata": self.models_metadata,
        }

    @classmethod
    def from_dict(cls, payload: Dict) -> "AppConfig":
        config = cls()
        config.comfyui_models_dir = payload.get("comfyui_models_dir", "")
        config.app_data_dir = payload.get("app_data_dir", str(default_app_data_dir()))
        config.hf_token = payload.get("hf_token", "")
        config.model_types = payload.get("model_types", list(DEFAULT_MODEL_TYPES))
        config.base_models = payload.get("base_models", list(DEFAULT_BASE_MODELS))
        config.models_metadata = payload.get("models_metadata", {})
        return config

    def ensure_app_dirs(self) -> None:
        base = Path(self.app_data_dir)
        (base / "readmes").mkdir(parents=True, exist_ok=True)
        (base / "previews").mkdir(parents=True, exist_ok=True)

    def add_metadata(
        self, relative_path: str, repo_id: str, filename: str, readme_path: str
    ) -> None:
        self.models_metadata[relative_path] = {
            "repo_id": repo_id,
            "filename": filename,
            "readme": readme_path,
            "added_at": datetime.utcnow().isoformat(timespec="seconds"),
        }

    def set_preview(self, relative_path: str, preview_path: str) -> None:
        entry = self.models_metadata.get(relative_path)
        if not entry:
            entry = {}
            self.models_metadata[relative_path] = entry
        entry["preview"] = preview_path

    def set_notes(self, relative_path: str, notes: str) -> None:
        entry = self.models_metadata.get(relative_path)
        if not entry:
            entry = {}
            self.models_metadata[relative_path] = entry
        entry["notes"] = notes


class ConfigManager:
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.config = AppConfig()

    def load(self) -> AppConfig:
        if self.config_path.exists():
            payload = json.loads(self.config_path.read_text(encoding="utf-8"))
            self.config = AppConfig.from_dict(payload)
        else:
            self.config = AppConfig()
            self.save()
        self.config.ensure_app_dirs()
        return self.config

    def save(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(
            json.dumps(self.config.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def update_paths(self, comfyui_models_dir: str, app_data_dir: Optional[str] = None) -> None:
        self.config.comfyui_models_dir = comfyui_models_dir
        if app_data_dir is not None:
            self.config.app_data_dir = app_data_dir
        self.config.ensure_app_dirs()
        self.save()
