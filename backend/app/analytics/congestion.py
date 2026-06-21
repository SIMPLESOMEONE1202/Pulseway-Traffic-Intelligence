from collections import deque


def level_for(score: float) -> str:
    if score < 25: return "FREE FLOW"
    if score < 50: return "LIGHT"
    if score < 75: return "MODERATE"
    return "HEAVY"


class CongestionScorer:
    def __init__(self, rolling_frames: int = 30):
        self.scores = deque(maxlen=rolling_frames)

    def update(self, vehicle_count: int, avg_speed: float) -> tuple[float, str]:
        density = min(100, vehicle_count / 18 * 100)
        speed_penalty = 100 - min(100, avg_speed / 50 * 100) if vehicle_count else 0
        raw = .65 * density + .35 * speed_penalty
        self.scores.append(raw)
        score = round(sum(self.scores) / len(self.scores), 1)
        return score, level_for(score)
