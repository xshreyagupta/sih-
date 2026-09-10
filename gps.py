ROUTE = [
    {"t": 0,    "lat": 28.545725, "lng": 77.010340},  # L001
    {"t": 1991, "lat": 28.692921, "lng": 76.978975},  # L002
    {"t": 3982, "lat": 28.641147, "lng": 77.096276},  # L003
    {"t": 5973, "lat": 28.426100, "lng": 77.152974},  # L004
    {"t": 7964, "lat": 28.416873, "lng": 77.123458},  # L005
    {"t": 9955, "lat": 28.431435, "lng": 76.986285},  # L006
]

def get_gps_at(timestamp: float) -> dict:
    for i in range(len(ROUTE) - 1):
        p1, p2 = ROUTE[i], ROUTE[i + 1]
        if p1["t"] <= timestamp <= p2["t"]:
            frac = (timestamp - p1["t"]) / (p2["t"] - p1["t"])
            return {
                "lat": p1["lat"] + frac * (p2["lat"] - p1["lat"]),
                "lng": p1["lng"] + frac * (p2["lng"] - p1["lng"]),
            }
    if timestamp < ROUTE[0]["t"]:
        return {"lat": ROUTE[0]["lat"], "lng": ROUTE[0]["lng"]}
    return {"lat": ROUTE[-1]["lat"], "lng": ROUTE[-1]["lng"]}

def ms_to_seconds(timestamp_ms):
    return timestamp_ms / 1000.0