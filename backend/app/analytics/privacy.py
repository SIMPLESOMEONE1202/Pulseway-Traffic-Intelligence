import cv2


def blur_people(frame, detections) -> None:
    for det in detections:
        if det.class_name != "person":
            continue
        x1, y1, x2, y2 = det.bbox
        head_bottom = y1 + max(1, (y2 - y1) // 3)
        region = frame[max(0, y1):max(0, head_bottom), max(0, x1):max(0, x2)]
        if region.size:
            frame[max(0, y1):max(0, head_bottom), max(0, x1):max(0, x2)] = cv2.GaussianBlur(region, (31, 31), 0)
