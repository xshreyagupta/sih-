import json
from gps import get_gps_at, ms_to_seconds


INPUT_FILE = "m2_output_m3.json"
OUTPUT_FILE = "traffic_congestion.json"


def generate_traffic_output():

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    for frame in data.get("frames", []):

        timestamp_ms = frame.get("timestamp_ms", 0)
        timestamp_seconds = ms_to_seconds(timestamp_ms)

        gps = get_gps_at(timestamp_seconds)

        results.append({
            "frame_id": frame.get("frame_id"),
            "timestamp_ms": timestamp_ms,
            "latitude": round(gps["lat"], 6),
            "longitude": round(gps["lng"], 6),
            "vehicle_count": frame.get(
                "current_vehicle_count",
                frame.get("vehicle_count", 0)
            ),
            "avg_speed": frame.get("avg_speed"),
            "congestion_level": frame.get("congestion_level")
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Traffic output written to: {OUTPUT_FILE}")
    print(f"Frames processed: {len(results)}")


if __name__ == "__main__":
    generate_traffic_output()