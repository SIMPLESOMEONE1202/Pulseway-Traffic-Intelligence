from typing import Literal
from pydantic import BaseModel, Field


class JobCreated(BaseModel):
    job_id: str
    status: Literal["queued"] = "queued"


class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "done", "failed"]
    progress: float = Field(ge=0, le=100)
    error: str | None = None


class Health(BaseModel):
    status: str = "ok"
    service: str = "smart-traffic-api"
