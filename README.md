# Pulseway Traffic Intelligence

An end-to-end traffic video analytics platform. Upload road footage, process it through a headless computer-vision pipeline, and review vehicle flow, congestion forecasts, lane pressure, stalled-vehicle alerts, signal recommendations, annotated video, heatmaps, and a top-down projection in a polished dashboard.

## What is implemented

- FastAPI upload → background analysis → results workflow with OpenAPI docs at `/docs`
- SQLite job state and time-series metadata, plus downloadable CSV per job
- YOLO detection when Ultralytics is available; automatic OpenCV motion-detection fallback
- Lightweight Kalman/IOU-style identity tracking (accurately labelled; no DeepSORT claim)
- Line-crossing counts, lane statistics, density + speed congestion scoring
- Explainable rolling linear forecast for the next 1, 3, and 5 minutes
- Stalled-vehicle detection, pedestrian head-region blur, adaptive green-time recommendation
- Annotated MP4, density heatmap, and explicitly labelled top-down projection
- Responsive React dashboard with upload, processing, and results states
- Unit/API tests and Docker Compose packaging

# 🏗️ SYSTEM ARCHITECTURE

```mermaid
flowchart LR

User[Traffic Analyst]

subgraph Frontend
Dashboard[React Dashboard]
end

subgraph Backend
FastAPI[FastAPI API]
Jobs[Background Job Manager]
SQLite[(SQLite Database)]
end

subgraph CVPipeline
Detector[YOLO / Motion Detector]
Tracker[Kalman + IOU Tracker]
Analytics[Traffic Analytics Engine]
Forecast[Congestion Forecast Engine]
end

subgraph Outputs
Video[Annotated Video]
Heatmap[Density Heatmap]
BEV[Top Down Projection]
CSV[Metrics CSV]
end

User --> Dashboard

Dashboard --> FastAPI

FastAPI --> Jobs

Jobs --> Detector

Detector --> Tracker

Tracker --> Analytics

Analytics --> Forecast

Forecast --> SQLite

Analytics --> Video
Analytics --> Heatmap
Analytics --> BEV
Analytics --> CSV

SQLite --> Dashboard
```

---

# 🔄 END-TO-END PROCESSING PIPELINE

```mermaid
flowchart TD

A[Upload Video]

A --> B[FastAPI Upload Endpoint]

B --> C[Store Job]

C --> D[Background Worker]

D --> E[Frame Extraction]

E --> F[Vehicle Detection]

F --> G[Object Tracking]

G --> H[Traffic Analytics]

H --> I[Forecasting]

I --> J[Generate Outputs]

J --> K[Store Results]

K --> L[Dashboard Visualization]
```

---

# ⚡ API WORKFLOW SEQUENCE

```mermaid
sequenceDiagram

participant User
participant Frontend
participant FastAPI
participant Worker
participant SQLite

User->>Frontend: Upload Video

Frontend->>FastAPI: POST /upload

FastAPI->>SQLite: Create Job

FastAPI-->>Frontend: job_id

Frontend->>FastAPI: Poll Status

FastAPI->>SQLite: Read Job State

SQLite-->>FastAPI: Processing

FastAPI-->>Frontend: Processing

Worker->>SQLite: Update Results

Frontend->>FastAPI: GET Results

FastAPI-->>Frontend: Analytics Payload
```

---

# 🚗 DETECTION & TRACKING PIPELINE

```mermaid
flowchart LR

Frame[Video Frame]

Frame --> Detector[YOLO Detection]

Detector --> Vehicles[Vehicle Bounding Boxes]

Vehicles --> Tracker[Kalman + IOU Tracker]

Tracker --> IDs[Persistent IDs]

IDs --> Analytics[Traffic Metrics]
```

---

# 📊 TRAFFIC ANALYTICS ENGINE

```mermaid
flowchart TD

Tracks[Tracked Vehicles]

Tracks --> Counts[Vehicle Counts]

Tracks --> Speed[Speed Estimation]

Tracks --> Density[Traffic Density]

Tracks --> Lanes[Lane Pressure]

Tracks --> Stall[Stalled Vehicle Detection]

Counts --> Congestion

Speed --> Congestion

Density --> Congestion

Lanes --> Congestion

Congestion[Congestion Score]
```

---

# 📈 CONGESTION FORECASTING PIPELINE

```mermaid
flowchart LR

Historical[Historical Scores]

Historical --> Rolling[Rolling Window]

Rolling --> Linear[Linear Regression]

Linear --> F1[1 Minute Forecast]

Linear --> F3[3 Minute Forecast]

Linear --> F5[5 Minute Forecast]

F1 --> Dashboard

F3 --> Dashboard

F5 --> Dashboard
```

---

# 🚨 INCIDENT DETECTION WORKFLOW

```mermaid
flowchart TD

Vehicle[Tracked Vehicle]

Vehicle --> Moving{Moving?}

Moving -->|Yes| Continue[Normal Tracking]

Moving -->|No| Timer[Stall Timer]

Timer --> Threshold{Threshold Exceeded?}

Threshold -->|No| Continue

Threshold -->|Yes| Alert[Generate Alert]

Alert --> Dashboard[Dashboard Warning]
```

---

# 📂 OUTPUT GENERATION PIPELINE

```mermaid
flowchart LR

Analytics[Analytics Engine]

Analytics --> Annotated[Annotated MP4]

Analytics --> Heatmap[Density Heatmap]

Analytics --> BEV[Top Down Projection]

Analytics --> CSV[Metrics CSV]

Annotated --> Results

Heatmap --> Results

BEV --> Results

CSV --> Results
```

---

# 🗄️ DATABASE & JOB STATE FLOW

```mermaid
flowchart TD

Upload[New Upload]

Upload --> Queued[Queued]

Queued --> Processing[Processing]

Processing --> Complete[Completed]

Processing --> Failed[Failed]

Complete --> Results[Results Available]

Results --> SQLite[(SQLite Storage)]
```

---

# 📂 PROJECT STRUCTURE ARCHITECTURE

```mermaid
flowchart TB

Root[Pulseway Traffic Intelligence]

Root --> Frontend[React Frontend]

Frontend --> Upload[Upload UI]
Frontend --> Dashboard[Analytics Dashboard]

Root --> Backend[FastAPI Backend]

Backend --> API[API Routes]
Backend --> Jobs[Background Workers]
Backend --> DB[SQLite]

Root --> CV[Computer Vision Engine]

CV --> Detector[YOLO Detector]
CV --> Tracker[Tracker]
CV --> Analytics[Analytics]

Root --> Forecast[Forecasting Engine]

Root --> Outputs[Output Generator]

Outputs --> Video[Annotated Video]
Outputs --> Heatmap[Heatmap]
Outputs --> BEV[Top Down View]
Outputs --> CSV[Metrics]
```

---

# 🚀 PRODUCTION-SCALE ARCHITECTURE

```mermaid
flowchart LR

Users[Users]

Users --> LoadBalancer

LoadBalancer --> React[React Frontend]

React --> FastAPI[FastAPI Cluster]

FastAPI --> Redis[Redis Queue]

Redis --> Workers[Celery Workers]

Workers --> ObjectStorage[S3 Storage]

Workers --> PostgreSQL

Workers --> CVEngine[CV Processing Cluster]

CVEngine --> Results[Analytics Results]

Results --> Dashboard
```


## Local development

Requirements: Python 3.10+, Node.js 20+, and an OpenCV-supported video codec.

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite server proxies `/api` to `http://localhost:8000`. API documentation is at `http://localhost:8000/docs`.

To run without downloading/loading YOLO weights, set `$env:TRAFFIC_DETECTOR='motion'` before starting the API. `auto` is the default and falls back to motion detection if YOLO cannot initialize.

## CLI

The processing engine is display-free and can be used without the web app:

```powershell
cd backend
python cli.py ..\samples\sample-traffic.mp4 --output output --detector motion
```

## Tests and builds

```powershell
cd backend
pytest -q

cd ..\frontend
npm run build
```

## Docker

```powershell
docker compose up --build
```

Open `http://localhost:8080` (dashboard) or `http://localhost:8000/docs` (API).

## API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/upload` | Validate and store a video; returns `job_id` |
| `GET` | `/jobs/{id}/status` | Poll queued/processing/done/failed state |
| `GET` | `/jobs/{id}/results` | Full analytics payload |
| `GET` | `/jobs/{id}/video` | Annotated MP4 |
| `GET` | `/jobs/{id}/heatmap` | Density image |
| `GET` | `/jobs/{id}/bev` | Top-down projection image |
| `GET` | `/jobs/{id}/metrics` | Per-interval CSV |

## Measurement caveats

Speed is an estimate based on a configurable meters-per-pixel assumption. Calibrate each camera with known road geometry before treating it as a measured physical speed. The top-down image is a scaled spatial projection, not a perspective-corrected homography. Congestion prediction is a short-horizon extrapolation of observed score trends; it is deliberately explainable and does not claim long-term forecasting accuracy.

For production concurrency, replace in-process background tasks with a durable queue such as Celery/Redis and store media in object storage. The current architecture is intentionally suited to a solo/academic demo deployment.

See [`samples/sample-results.json`](samples/sample-results.json) for an example API response.
