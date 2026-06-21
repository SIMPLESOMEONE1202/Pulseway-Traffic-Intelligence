from dataclasses import dataclass


@dataclass
class LaneStat:
    lane: int
    count: int
    avg_speed_kmh: float


def lane_stats(tracks, width: int, lane_count: int = 4) -> list[LaneStat]:
    buckets = [[] for _ in range(lane_count)]
    for track in tracks:
        index = min(lane_count - 1, max(0, int(track.center[0] / max(width, 1) * lane_count)))
        if track.class_name != "person":
            buckets[index].append(track.speed_kmh)
    return [
        LaneStat(index + 1, len(speeds), round(sum(speeds) / len(speeds), 1) if speeds else 0)
        for index, speeds in enumerate(buckets)
    ]
