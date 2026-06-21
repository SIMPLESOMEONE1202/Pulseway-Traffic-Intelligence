import csv
import logging
import time
from pathlib import Path
from typing import Callable

import cv2
import numpy as np

from .congestion import CongestionScorer
from .counting import LineCounter
from .detection import Detector
from .incidents import IncidentDetector
from .lanes import lane_stats
from .prediction import forecast
from .privacy import blur_people
from .signal_timing import recommend
from .tracking import SortTracker
from .visualization import Heatmap, draw_overlay, top_down_snapshot

log = logging.getLogger(__name__)
ProgressCallback = Callable[[float, dict | None], None]


def _writer(path: Path, fps: float, size: tuple[int, int]):
    for codec in ("avc1", "mp4v"):
        writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*codec), fps, size)
        if writer.isOpened():
            return writer
    raise RuntimeError("No MP4 video encoder is available in this OpenCV build")


def process_video(input_path: Path, output_dir: Path, callback: ProgressCallback, *, detector_mode="auto", model_name="yolov8n.pt", confidence=.3, sample_every=1) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        raise ValueError("The uploaded file is not a readable video")
    fps = capture.get(cv2.CAP_PROP_FPS)
    frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    if fps <= 0 or width <= 0 or height <= 0:
        capture.release()
        raise ValueError("The video has invalid metadata or an unsupported codec")

    detector = Detector(detector_mode, model_name, confidence)
    tracker = SortTracker()
    counter = LineCounter()
    scorer = CongestionScorer()
    incident_detector = IncidentDetector(min_history=max(12, int(fps * 2)))
    heatmap = Heatmap(height, width)
    writer = _writer(output_dir / "annotated.mp4", fps, (width, height))
    csv_file = (output_dir / "metrics.csv").open("w", newline="", encoding="utf-8")
    csv_writer = csv.DictWriter(csv_file, fieldnames=["timestamp_sec", "vehicle_count", "avg_speed_kmh", "score", "level"])
    csv_writer.writeheader()

    observed, incidents, inference_times = [], [], []
    last_tracks, last_lanes, last_frame = [], [], None
    index = 0
    try:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            started = time.perf_counter()
            detections = detector.detect(frame) if index % sample_every == 0 else []
            inference_times.append((time.perf_counter() - started) * 1000)
            blur_people(frame, detections)
            tracks = tracker.update(detections, fps / sample_every)
            counter.update(tracks, height)
            vehicles = [track for track in tracks if track.class_name != "person"]
            avg_speed = float(np.mean([track.speed_kmh for track in vehicles])) if vehicles else 0
            score, level = scorer.update(len(vehicles), avg_speed)
            lanes = lane_stats(tracks, width)
            timestamp = index / fps
            incidents.extend(incident_detector.update(tracks, timestamp, width))
            heatmap.update(tracks)
            draw_overlay(frame, tracks, score, level, counter.total, counter.y_fraction)
            writer.write(frame)
            metric = {"timestamp_sec": round(timestamp, 2), "vehicle_count": len(vehicles), "avg_speed_kmh": round(avg_speed, 1), "score": score, "level": level}
            if not observed or timestamp - observed[-1]["timestamp_sec"] >= max(1, min(30, frame_count / fps / 30)):
                observed.append(metric)
                csv_writer.writerow(metric)
                callback(min(99, (index + 1) / max(frame_count, 1) * 100), metric)
            last_tracks, last_lanes, last_frame = tracks, lanes, frame.copy()
            index += 1
    finally:
        capture.release(); writer.release(); csv_file.close()

    if index == 0 or last_frame is None:
        raise ValueError("The uploaded video contains no decodable frames")
    cv2.imwrite(str(output_dir / "heatmap.jpg"), heatmap.image(last_frame))
    cv2.imwrite(str(output_dir / "top-down.jpg"), top_down_snapshot(last_tracks, width, height))
    current = observed[-1]
    counts = {name: int(counter.by_class.get(name, 0)) for name in ("car", "truck", "bus", "motorcycle", "bicycle", "person")}
    return {
        "video_meta": {"fps": round(fps, 2), "frames_processed": index, "duration_sec": round(index / fps, 1), "resolution": f"{width}x{height}", "avg_inference_ms": round(float(np.mean(inference_times)), 1), "detector": detector.mode},
        "vehicle_counts": counts,
        "congestion": {"current_score": current["score"], "current_level": current["level"], "observed": observed, "predicted_trend": [point.__dict__ for point in forecast(observed)]},
        "lanes": [lane.__dict__ for lane in last_lanes],
        "incidents": [incident.__dict__ for incident in incidents],
        "speed": {"avg_kmh": current["avg_speed_kmh"], "calibration": "estimated_meters_per_pixel=0.05; calibrate per camera for measured speed"},
        "signal_recommendation": recommend(last_lanes),
    }
