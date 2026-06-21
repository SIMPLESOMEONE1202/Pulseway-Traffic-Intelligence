def recommend(lanes) -> dict:
    if not lanes:
        return {"phase": "balanced_cycle", "green_time_sec": 25, "reason": "No dominant approach"}
    busiest = max(lanes, key=lambda lane: lane.count)
    total = sum(lane.count for lane in lanes)
    if total == 0:
        return {"phase": "balanced_cycle", "green_time_sec": 25, "reason": "No active demand"}
    green = min(55, max(20, round(20 + 35 * busiest.count / total)))
    return {"phase": f"approach_{busiest.lane}_green", "green_time_sec": green, "reason": f"Lane {busiest.lane} has the highest observed demand"}
