import os
from pathlib import Path

os.environ["TRAFFIC_DATA_DIR"] = str(Path(__file__).parent / ".test-data")
os.environ["TRAFFIC_DB"] = str(Path(__file__).parent / ".test-data" / "test.db")

from fastapi.testclient import TestClient
from app.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_rejects_wrong_type():
    with TestClient(app) as client:
        response = client.post("/upload", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert response.status_code == 415


def test_sample_video_completes_end_to_end():
    sample = Path(__file__).parents[2] / "samples" / "sample-traffic.mp4"
    with TestClient(app) as client, sample.open("rb") as video:
        created = client.post("/upload", files={"file": (sample.name, video, "video/mp4")})
        assert created.status_code == 202
        job_id = created.json()["job_id"]
        status = client.get(f"/jobs/{job_id}/status").json()
        assert status["status"] == "done"
        result = client.get(f"/jobs/{job_id}/results")
        assert result.status_code == 200
        assert result.json()["video_meta"]["frames_processed"] == 160
        assert client.get(f"/jobs/{job_id}/heatmap").status_code == 200
