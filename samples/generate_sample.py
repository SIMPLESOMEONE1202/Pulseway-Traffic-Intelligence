"""Generate a tiny deterministic road-like clip for smoke testing."""
from pathlib import Path
import cv2
import numpy as np

path = Path(__file__).with_name("sample-traffic.mp4")
width, height, fps, frames = 640, 360, 20, 160
writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
if not writer.isOpened():
    raise RuntimeError("This OpenCV build cannot write MP4 video")
for index in range(frames):
    frame = np.full((height, width, 3), (28, 31, 29), np.uint8)
    cv2.rectangle(frame, (125, 0), (515, height), (48, 51, 49), -1)
    for x in (222, 320, 418):
        for y in range(-40, height, 70):
            cv2.line(frame, (x, y + index * 3 % 70), (x, y + 33 + index * 3 % 70), (155, 155, 145), 2)
    cars = [
        (165, (index * 3 + 20) % 440 - 70, (30, 175, 230)),
        (265, (index * 2 + 130) % 440 - 70, (220, 130, 45)),
        (365, (index * 4 + 60) % 440 - 70, (70, 210, 90)),
        (465, (index * 2 + 250) % 440 - 70, (175, 70, 190)),
    ]
    for x, y, color in cars:
        cv2.rectangle(frame, (x, y), (x + 38, y + 60), color, -1)
        cv2.rectangle(frame, (x + 5, y + 8), (x + 33, y + 20), (35, 45, 48), -1)
    cv2.putText(frame, "PULSEWAY SAMPLE / SYNTHETIC FOOTAGE", (12, 344), cv2.FONT_HERSHEY_SIMPLEX, .38, (170, 180, 176), 1, cv2.LINE_AA)
    writer.write(frame)
writer.release()
print(path)
