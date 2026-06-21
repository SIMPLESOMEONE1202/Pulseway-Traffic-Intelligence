from dataclasses import dataclass
from math import hypot


@dataclass
class Incident:
    track_id: int
    type: str
    timestamp_sec: float
    lane: int


class IncidentDetector:
    def __init__(self, min_history: int = 24, displacement_px: float = 10):
        self.min_history = min_history
        self.displacement_px = displacement_px
        self.reported: set[int] = set()

    def update(self, tracks, timestamp: float, width: int) -> list[Incident]:
        found = []
        for track in tracks:
            if track.id in self.reported or track.class_name == "person" or len(track.history) < self.min_history:
                continue
            start, end = track.history[0], track.history[-1]
            if hypot(end[0] - start[0], end[1] - start[1]) <= self.displacement_px:
                lane = min(4, max(1, int(track.center[0] / max(width, 1) * 4) + 1))
                found.append(Incident(track.id, "stalled_vehicle", round(timestamp, 1), lane))
                self.reported.add(track.id)
        return found
