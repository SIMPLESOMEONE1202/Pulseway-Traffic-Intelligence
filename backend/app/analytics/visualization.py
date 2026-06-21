import cv2
import numpy as np


COLORS = {
    "car": (20, 190, 255), "truck": (10, 150, 230), "bus": (30, 160, 220),
    "motorcycle": (50, 220, 255), "bicycle": (100, 220, 255), "person": (200, 80, 220),
}


def draw_overlay(frame, tracks, score: float, level: str, total: int, line_fraction: float = .55):
    height, width = frame.shape[:2]
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, 64), (12, 12, 12), -1)
    cv2.rectangle(overlay, (0, height - 46), (width, height), (12, 12, 12), -1)
    cv2.addWeighted(overlay, .82, frame, .18, 0, frame)
    line_y = int(height * line_fraction)
    cv2.line(frame, (0, line_y), (width, line_y), (0, 255, 180), 2)
    for track in tracks:
        x1, y1, x2, y2 = track.bbox
        color = COLORS.get(track.class_name, (140, 140, 140))
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, f"{track.class_name.upper()} #{track.id}  {track.speed_kmh:.0f} km/h", (x1, max(18, y1 - 7)), cv2.FONT_HERSHEY_SIMPLEX, .43, color, 1, cv2.LINE_AA)
    cv2.putText(frame, "PULSEWAY  /  TRAFFIC INTELLIGENCE", (18, 27), cv2.FONT_HERSHEY_SIMPLEX, .57, (220, 210, 30), 1, cv2.LINE_AA)
    cv2.putText(frame, f"CONGESTION {score:.0f}  {level}", (18, 52), cv2.FONT_HERSHEY_SIMPLEX, .48, (0, 255, 180), 1, cv2.LINE_AA)
    cv2.putText(frame, f"COUNTED {total:04d}", (width - 165, 35), cv2.FONT_HERSHEY_SIMPLEX, .5, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.putText(frame, "KALMAN-IOU TRACKER (SORT-STYLE)  /  PRIVACY FILTER ACTIVE", (18, height - 17), cv2.FONT_HERSHEY_SIMPLEX, .4, (140, 140, 140), 1, cv2.LINE_AA)


class Heatmap:
    def __init__(self, height: int, width: int):
        self.values = np.zeros((height, width), np.float32)

    def update(self, tracks):
        self.values *= .985
        h, w = self.values.shape
        for track in tracks:
            x, y = map(int, track.center)
            if 0 <= x < w and 0 <= y < h:
                cv2.circle(self.values, (x, y), max(18, h // 25), 1, -1)
        self.values = cv2.GaussianBlur(self.values, (0, 0), sigmaX=15)

    def image(self, base):
        norm = cv2.normalize(self.values, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        color = cv2.applyColorMap(norm, cv2.COLORMAP_TURBO)
        return cv2.addWeighted(base, .52, color, .48, 0)


def top_down_snapshot(tracks, width: int, height: int, canvas_size=(420, 580)):
    cw, ch = canvas_size
    canvas = np.full((ch, cw, 3), (12, 12, 12), np.uint8)
    for lane in range(1, 4):
        x = int(cw * lane / 4)
        cv2.line(canvas, (x, 0), (x, ch), (70, 70, 70), 1)
    for track in tracks:
        x = int(track.center[0] / max(width, 1) * cw)
        y = int(track.center[1] / max(height, 1) * ch)
        color = COLORS.get(track.class_name, (140, 140, 140))
        cv2.circle(canvas, (x, y), 7 if track.class_name != "person" else 4, color, -1)
    cv2.putText(canvas, "TOP-DOWN PROJECTION", (16, 28), cv2.FONT_HERSHEY_SIMPLEX, .5, (220, 210, 30), 1, cv2.LINE_AA)
    return canvas
