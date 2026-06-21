from collections import Counter


class LineCounter:
    def __init__(self, y_fraction: float = .55):
        self.y_fraction = y_fraction
        self.counted: set[int] = set()
        self.previous_y: dict[int, float] = {}
        self.by_class: Counter = Counter()

    def update(self, tracks, frame_height: int) -> None:
        line_y = frame_height * self.y_fraction
        for track in tracks:
            y = track.center[1]
            previous = self.previous_y.get(track.id)
            if previous is not None and track.id not in self.counted and (previous - line_y) * (y - line_y) <= 0:
                self.counted.add(track.id)
                self.by_class[track.class_name] += 1
            self.previous_y[track.id] = y

    @property
    def total(self) -> int:
        return sum(self.by_class.values())
