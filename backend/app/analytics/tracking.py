from collections import deque
from dataclasses import dataclass, field
from math import hypot

from .detection import Detection


def iou(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> float:
    x1, y1, x2, y2 = max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])
    intersection = max(0, x2 - x1) * max(0, y2 - y1)
    area_a = max(0, a[2] - a[0]) * max(0, a[3] - a[1])
    area_b = max(0, b[2] - b[0]) * max(0, b[3] - b[1])
    return intersection / max(area_a + area_b - intersection, 1)


@dataclass
class Track:
    id: int
    bbox: tuple[int, int, int, int]
    class_name: str
    confidence: float
    hits: int = 1
    missed: int = 0
    speed_kmh: float = 0
    history: deque = field(default_factory=lambda: deque(maxlen=90))

    @property
    def center(self) -> tuple[float, float]:
        return ((self.bbox[0] + self.bbox[2]) / 2, (self.bbox[1] + self.bbox[3]) / 2)


class SortTracker:
    """Lightweight IOU tracker. Honest SORT-style naming; no appearance embeddings."""

    def __init__(self, max_missed: int = 12, iou_threshold: float = .18, meters_per_pixel: float = .05):
        self.tracks: list[Track] = []
        self.next_id = 1
        self.max_missed = max_missed
        self.iou_threshold = iou_threshold
        self.meters_per_pixel = meters_per_pixel

    def update(self, detections: list[Detection], fps: float) -> list[Track]:
        candidates = sorted(
            ((iou(track.bbox, det.bbox), ti, di) for ti, track in enumerate(self.tracks) for di, det in enumerate(detections)),
            reverse=True,
        )
        used_tracks, used_dets = set(), set()
        for overlap, ti, di in candidates:
            if overlap < self.iou_threshold or ti in used_tracks or di in used_dets:
                continue
            track, det = self.tracks[ti], detections[di]
            old = track.center
            track.bbox, track.class_name, track.confidence = det.bbox, det.class_name, det.confidence
            track.hits += 1
            track.missed = 0
            track.history.append(track.center)
            distance = hypot(track.center[0] - old[0], track.center[1] - old[1])
            instant_speed = distance * self.meters_per_pixel * fps * 3.6
            track.speed_kmh = .75 * track.speed_kmh + .25 * min(instant_speed, 160)
            used_tracks.add(ti); used_dets.add(di)
        for ti, track in enumerate(self.tracks):
            if ti not in used_tracks:
                track.missed += 1
        for di, det in enumerate(detections):
            if di not in used_dets:
                track = Track(self.next_id, det.bbox, det.class_name, det.confidence)
                track.history.append(track.center)
                self.next_id += 1
                self.tracks.append(track)
        self.tracks = [track for track in self.tracks if track.missed <= self.max_missed]
        return [track for track in self.tracks if track.hits >= 2 and track.missed <= 2]
