import csv
import json
import math

EXPECTED_FILE = "expected m1.txt"
DETECTIONS_FILE = "video1m1.json"
OUTPUT_FILE = "infrastructure.json"




MATCH_RADIUS_METERS = 10

INFRASTRUCTURE_TYPES = {
    "no_parking_sign",
    "pedestrian_crossing_sign",
    "road_work_ahead_sign",
    "school_ahead_sign",
    "speed_limit_sign",
    "traffic_light",
    "zebra_crossing",
    "road_divider",
    "streetlight",
    "stop_sign",
}


def normalize_type(value):
    if value is None:
        return None

    value = value.strip().lower()

    aliases = {
        "no_parking": "no_parking_sign",
        "pedestrian_crossing": "pedestrian_crossing_sign",
        "road_work_ahead": "road_work_ahead_sign",
        "school_ahead": "school_ahead_sign",
        "speed_limit": "speed_limit_sign",
    }

    return aliases.get(value, value)


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    dlat = lat2 - lat1
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * R * math.asin(math.sqrt(a))


def load_expected_locations():
    locations = []

    with open(EXPECTED_FILE, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:

            # Only initial video_1 locations.
            # Do not use FO-Lxxx rows here.
            if row["video_id"] != "video_1":
                continue

            if row["location_id"].startswith("FO-"):
                continue

            expected_type = row["expected_type"].strip()

            # "object" is not a specific infrastructure class.
            if normalize_type(expected_type) not in {
                normalize_type(x) for x in INFRASTRUCTURE_TYPES
            }:
                continue

            locations.append({
                "location_id": row["location_id"],
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "timestamp_start_ms": int(row["timestamp_start_ms"]),
                "timestamp_end_ms": int(row["timestamp_end_ms"]),
                "expected_infrastructure": expected_type,
            })

    return locations


def load_detections():
    with open(DETECTIONS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        data = data.get("detections", [])

    detections = []

    for detection in data:

        if detection.get("source") != "infrastructure":
            continue

        if detection.get("latitude") is None:
            continue

        if detection.get("longitude") is None:
            continue

        if detection.get("timestamp_ms") is None:
            continue

        detected_type = detection.get("type")

        if not detected_type:
            continue

        detections.append({
            "type": detected_type,
            "confidence": detection.get("confidence"),
            "latitude": float(detection["latitude"]),
            "longitude": float(detection["longitude"]),
            "timestamp_ms": int(detection["timestamp_ms"]),
            "frame_id": detection.get("frame_id"),
        })

    return detections


def check_infrastructure():

    expected_locations = load_expected_locations()
    detections = load_detections()

    results = []

    for location in expected_locations:

        expected_type = location["expected_infrastructure"]
        expected_normalized = normalize_type(expected_type)

        nearby_detections = []

        for detection in detections:

            timestamp = detection["timestamp_ms"]

            # Timestamp must fall inside expected window.
            if not (
                location["timestamp_start_ms"]
                <= timestamp
                <= location["timestamp_end_ms"]
            ):
                continue

            distance = haversine_distance(
                location["latitude"],
                location["longitude"],
                detection["latitude"],
                detection["longitude"],
            )

            if distance <= MATCH_RADIUS_METERS:
                nearby_detections.append(
                    (detection, distance)
                )

        # First look for correct infrastructure type.
        matching = [
            item
            for item in nearby_detections
            if normalize_type(item[0]["type"]) == expected_normalized
        ]

        if matching:

            # Highest confidence correct detection wins.
            matching.sort(
                key=lambda x: (
                    x[0]["confidence"]
                    if x[0]["confidence"] is not None
                    else 0
                ),
                reverse=True,
            )

            detection, _ = matching[0]

            status = "PRESENT"
            detected_type = detection["type"]
            confidence = detection["confidence"]

        elif nearby_detections:

            # Something was detected at the expected location/time,
            # but it is the wrong infrastructure type.
            nearby_detections.sort(
                key=lambda x: (
                    x[0]["confidence"]
                    if x[0]["confidence"] is not None
                    else 0
                ),
                reverse=True,
            )

            detection, _ = nearby_detections[0]

            status = "WRONG"
            detected_type = detection["type"]
            confidence = detection["confidence"]

        else:

            # Nothing detected.
            status = "MISSING"
            detected_type = None
            confidence = None

        results.append({
            "location_id": location["location_id"],
            "latitude": round(location["latitude"], 6),
            "longitude": round(location["longitude"], 6),
            "expected_infrastructure": expected_type,
            "detected_infrastructure": detected_type,
            "status": status,
            "confidence": confidence,
        })

    return results


def write_output(results):

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Infrastructure output written to: {OUTPUT_FILE}")
    print(f"Locations processed: {len(results)}")

    from collections import Counter

    counts = Counter(
        item["status"]
        for item in results
    )

    print("Status:", counts)


if __name__ == "__main__":

    results = check_infrastructure()
    write_output(results)