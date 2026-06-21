import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import settings


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    db = sqlite3.connect(settings.database_path, timeout=30)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def init_db() -> None:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY,
              original_name TEXT NOT NULL,
              status TEXT NOT NULL,
              progress REAL NOT NULL DEFAULT 0,
              error TEXT,
              result_json TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS metrics (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              job_id TEXT NOT NULL,
              timestamp_sec REAL NOT NULL,
              vehicle_count INTEGER NOT NULL,
              avg_speed_kmh REAL NOT NULL,
              congestion_score REAL NOT NULL,
              congestion_level TEXT NOT NULL,
              FOREIGN KEY(job_id) REFERENCES jobs(id)
            );
            CREATE INDEX IF NOT EXISTS idx_metrics_job ON metrics(job_id);
            """
        )


def create_job(job_id: str, original_name: str) -> None:
    now = utc_now()
    with connection() as db:
        db.execute(
            "INSERT INTO jobs(id, original_name, status, progress, created_at, updated_at) VALUES(?, ?, 'queued', 0, ?, ?)",
            (job_id, original_name, now, now),
        )


def update_job(job_id: str, **fields: Any) -> None:
    allowed = {"status", "progress", "error", "result_json"}
    values = {key: value for key, value in fields.items() if key in allowed}
    if "result_json" in values and not isinstance(values["result_json"], str):
        values["result_json"] = json.dumps(values["result_json"])
    values["updated_at"] = utc_now()
    assignments = ", ".join(f"{key} = ?" for key in values)
    with connection() as db:
        db.execute(f"UPDATE jobs SET {assignments} WHERE id = ?", (*values.values(), job_id))


def get_job(job_id: str) -> dict[str, Any] | None:
    with connection() as db:
        row = db.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
    if not row:
        return None
    result = dict(row)
    if result.get("result_json"):
        result["result"] = json.loads(result["result_json"])
    return result


def add_metric(job_id: str, metric: dict[str, Any]) -> None:
    with connection() as db:
        db.execute(
            """INSERT INTO metrics(job_id, timestamp_sec, vehicle_count, avg_speed_kmh,
               congestion_score, congestion_level) VALUES(?, ?, ?, ?, ?, ?)""",
            (job_id, metric["timestamp_sec"], metric["vehicle_count"], metric["avg_speed_kmh"], metric["score"], metric["level"]),
        )
