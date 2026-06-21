from dataclasses import dataclass
import logging
import cv2
import numpy as np

log = logging.getLogger(__name__)
TRACKED_CLASSES = {"car", "truck", "bus", "motorcycle", "bicycle", "person"}


@dataclass
class Detection:
    bbox: tuple[int, int, int, int]
    class_name: str
    confidence: float


class Detector:
    """YOLO detector with a zero-download OpenCV fallback."""

    def __init__(self, mode: str = "auto", model_name: str = "yolov8n.pt", confidence: float = 0.3):
        self.mode = mode
        self.confidence = confidence
        self.model = None
        self.motion = None
        if mode != "motion":
            try:
                from ultralytics import YOLO
                self.model = YOLO(model_name)
                self.mode = "yolo"
                log.info("Using YOLO detector: %s", model_name)
            except Exception as exc:
                if mode == "yolo":
                    raise RuntimeError(f"Could not initialize YOLO: {exc}") from exc
                log.warning("YOLO unavailable; using motion detector: %s", exc)
        if self.model is None:
            self.mode = "motion"
            self.motion = cv2.createBackgroundSubtractorMOG2(history=350, varThreshold=32, detectShadows=True)

    def detect(self, frame: np.ndarray) -> list[Detection]:
        if self.model is not None:
            result = self.model(frame, verbose=False, imgsz=640, conf=self.confidence)[0]
            detections = []
            if result.boxes is not None:
                for box in result.boxes:
                    name = result.names.get(int(box.cls[0]), "")
                    if name in TRACKED_CLASSES:
                        coords = tuple(int(v) for v in box.xyxy[0].tolist())
                        detections.append(Detection(coords, name, float(box.conf[0])))
            return detections

        mask = self.motion.apply(frame)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        mask = cv2.dilate(mask, np.ones((7, 7), np.uint8), iterations=2)
        detections = []
        min_area = max(500, frame.shape[0] * frame.shape[1] // 1500)
        for contour in cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]:
            if cv2.contourArea(contour) < min_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            if w > frame.shape[1] * .8 or h > frame.shape[0] * .8:
                continue
            detections.append(Detection((x, y, x + w, y + h), "car", 0.55))
        return detections
