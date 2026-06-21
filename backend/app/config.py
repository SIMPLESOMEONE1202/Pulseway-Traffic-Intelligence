from dataclasses import dataclass
from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    data_dir: Path = Path(os.getenv("TRAFFIC_DATA_DIR", BASE_DIR / "data"))
    database_path: Path = Path(os.getenv("TRAFFIC_DB", BASE_DIR / "data" / "traffic.db"))
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "500"))
    detector: str = os.getenv("TRAFFIC_DETECTOR", "auto")
    yolo_model: str = os.getenv("YOLO_MODEL", "yolov8n.pt")
    confidence: float = float(os.getenv("YOLO_CONFIDENCE", "0.30"))
    sample_every: int = max(1, int(os.getenv("SAMPLE_EVERY", "1")))
    cors_origins: tuple[str, ...] = tuple(
        value.strip()
        for value in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if value.strip()
    )


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
