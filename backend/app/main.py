import logging
import shutil
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .analytics.engine import process_video
from .config import settings
from .database import add_metric, create_job, get_job, init_db, update_job
from .schemas import Health, JobCreated, JobStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger(__name__)
ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Pulseway Traffic Intelligence API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


def job_or_404(job_id: str) -> dict:
    job = get_job(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


def run_job(job_id: str, source: Path, folder: Path) -> None:
    try:
        update_job(job_id, status="processing", progress=1, error=None)
        def progress(value: float, metric: dict | None):
            update_job(job_id, progress=round(value, 1))
            if metric:
                add_metric(job_id, metric)
        result = process_video(source, folder, progress, detector_mode=settings.detector, model_name=settings.yolo_model, confidence=settings.confidence, sample_every=settings.sample_every)
        result["job_id"] = job_id
        result["media"] = {"video_url": f"/jobs/{job_id}/video", "heatmap_url": f"/jobs/{job_id}/heatmap", "bev_url": f"/jobs/{job_id}/bev", "metrics_url": f"/jobs/{job_id}/metrics"}
        update_job(job_id, status="done", progress=100, result_json=result)
    except Exception as exc:
        log.exception("Job %s failed", job_id)
        update_job(job_id, status="failed", error=str(exc), progress=0)


@app.get("/health", response_model=Health)
def health(): return Health()


@app.post("/upload", response_model=JobCreated, status_code=202)
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, f"Unsupported video type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")
    job_id = uuid.uuid4().hex[:12]
    folder = settings.data_dir / "jobs" / job_id
    folder.mkdir(parents=True, exist_ok=False)
    source = folder / f"input{suffix}"
    size = 0
    try:
        with source.open("wb") as output:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > settings.max_upload_mb * 1024 * 1024:
                    raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit")
                output.write(chunk)
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
    if size == 0:
        shutil.rmtree(folder, ignore_errors=True)
        raise HTTPException(400, "Uploaded file is empty")
    create_job(job_id, file.filename or source.name)
    background_tasks.add_task(run_job, job_id, source, folder)
    return JobCreated(job_id=job_id)


@app.get("/jobs/{job_id}/status", response_model=JobStatus)
def status(job_id: str):
    job = job_or_404(job_id)
    return JobStatus(job_id=job_id, status=job["status"], progress=job["progress"], error=job["error"])


@app.get("/jobs/{job_id}/results")
def results(job_id: str):
    job = job_or_404(job_id)
    if job["status"] != "done":
        raise HTTPException(409, f"Job is {job['status']}; results are not ready")
    return job["result"]


def media(job_id: str, name: str, media_type: str):
    job_or_404(job_id)
    path = settings.data_dir / "jobs" / job_id / name
    if not path.exists(): raise HTTPException(404, "Media is not ready")
    return FileResponse(path, media_type=media_type, filename=name if name == "metrics.csv" else None)


@app.get("/jobs/{job_id}/video")
def video(job_id: str): return media(job_id, "annotated.mp4", "video/mp4")


@app.get("/jobs/{job_id}/heatmap")
def heatmap(job_id: str): return media(job_id, "heatmap.jpg", "image/jpeg")


@app.get("/jobs/{job_id}/bev")
def bev(job_id: str): return media(job_id, "top-down.jpg", "image/jpeg")


@app.get("/jobs/{job_id}/metrics")
def metrics(job_id: str): return media(job_id, "metrics.csv", "text/csv")
