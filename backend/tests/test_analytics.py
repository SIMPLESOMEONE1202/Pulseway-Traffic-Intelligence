from app.analytics.congestion import CongestionScorer, level_for
from app.analytics.counting import LineCounter
from app.analytics.detection import Detection
from app.analytics.prediction import forecast
from app.analytics.signal_timing import recommend
from app.analytics.tracking import SortTracker, Track, iou
from app.analytics.lanes import LaneStat


def test_iou_identity_and_separation():
    assert iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1
    assert iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0


def test_tracker_preserves_id_for_overlapping_detection():
    tracker = SortTracker(iou_threshold=.1)
    tracker.update([Detection((10, 10, 30, 30), "car", .9)], 30)
    tracks = tracker.update([Detection((12, 12, 32, 32), "car", .9)], 30)
    assert len(tracks) == 1
    assert tracks[0].id == 1


def test_line_counter_requires_crossing():
    counter = LineCounter(.5)
    track = Track(1, (0, 35, 10, 45), "car", .9, hits=2)
    counter.update([track], 100)
    track.bbox = (0, 55, 10, 65)
    counter.update([track], 100)
    assert counter.total == 1
    assert counter.by_class["car"] == 1


def test_congestion_uses_density_and_speed():
    scorer = CongestionScorer(1)
    fast_score, _ = scorer.update(14, 50)
    slow_score, _ = scorer.update(14, 5)
    assert slow_score > fast_score
    assert level_for(80) == "HEAVY"


def test_forecast_projects_increasing_series():
    series = [{"timestamp_sec": i * 60, "score": 20 + i * 4} for i in range(5)]
    points = forecast(series)
    assert [point.t_minutes for point in points] == [1, 3, 5]
    assert points[-1].score > points[0].score > series[-1]["score"]


def test_signal_prefers_busiest_lane():
    result = recommend([LaneStat(1, 2, 30), LaneStat(2, 8, 15)])
    assert result["phase"] == "approach_2_green"
    assert 20 <= result["green_time_sec"] <= 55
