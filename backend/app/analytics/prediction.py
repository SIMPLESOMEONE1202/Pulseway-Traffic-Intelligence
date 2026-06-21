from dataclasses import dataclass
import numpy as np


@dataclass
class ForecastPoint:
    t_minutes: int
    score: float


def forecast(series: list[dict], horizons: tuple[int, ...] = (1, 3, 5)) -> list[ForecastPoint]:
    """Explainable linear trend forecast with damping and safe score bounds."""
    if not series:
        return [ForecastPoint(h, 0) for h in horizons]
    values = np.array([point["score"] for point in series[-20:]], dtype=float)
    current = float(values[-1])
    if len(values) < 3:
        slope = 0.0
    else:
        x = np.array([point["timestamp_sec"] for point in series[-20:]], dtype=float) / 60
        x -= x[0]
        slope = float(np.polyfit(x, values, 1)[0]) if np.ptp(x) > 0 else 0.0
        slope = max(-8.0, min(8.0, slope))
    return [ForecastPoint(h, round(max(0, min(100, current + slope * h * .75)), 1)) for h in horizons]
