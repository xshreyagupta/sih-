import json
import math


DEFECT_FILE = "events.json"
INFRASTRUCTURE_FILE = "infrastructure.json"
FINAL_DETECTIONS_FILE = "final_one.json"

OUTPUT_FILE = "verification.json"

MATCH_RADIUS_METERS = 10


def distance_meters(lat1, lon1, lat2, lon2):

    earth_radius = 6371000

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

    return 2 * earth_radius * math.asin(
        math.sqrt(a)
    )


def load_json(path):

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(name):

    if name is None:
        return None

    name = name.lower().strip()

    name_map = {
        "no_parking_sign": "no_parking",
        "pedestrian_crossing_sign": "pedestrian_crossing",
        "road_work_ahead_sign": "road_work_ahead",
        "school_ahead_sign": "school_ahead",
        "speed_limit_sign": "speed_limit"
    }

    return name_map.get(name, name)


# =========================================================
# DEFECT VERIFICATION
# =========================================================

def verify_defect_event(event, final_detections, event_index):

    event_lat = event["latitude"]
    event_lng = event["longitude"]

    defect_type = normalize(
        event["class_name"]
    )

    matches = []

    for detection in final_detections:

        if detection.get("source") != "road_damage":
            continue

        if detection.get("latitude") is None:
            continue

        if detection.get("longitude") is None:
            continue

        detected_type = normalize(
            detection.get("type")
        )

        if detected_type != defect_type:
            continue

        distance = distance_meters(
            event_lat,
            event_lng,
            detection["latitude"],
            detection["longitude"]
        )

        if distance <= MATCH_RADIUS_METERS:
            matches.append(detection)

    if matches:

        best = max(
            matches,
            key=lambda x: (
                x.get("confidence")
                if x.get("confidence") is not None
                else 0
            )
        )

        confidence = best.get("confidence")

        if confidence is not None:
            confidence = round(
                float(confidence),
                2
            )

        return {
            "event_id": event_index,
            "event_type": "defect",
            "class_name": event["class_name"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "verification_result": "resolution_disputed",
            "confidence": confidence
        }

    return {
        "event_id": event_index,
        "event_type": "defect",
        "class_name": event["class_name"],
        "latitude": event["latitude"],
        "longitude": event["longitude"],
        "verification_result": "verified_closed",
        "confidence": None
    }


# =========================================================
# INFRASTRUCTURE VERIFICATION
# =========================================================

def verify_infrastructure(
    infrastructure,
    final_detections
):

    expected_type = normalize(
        infrastructure["expected_infrastructure"]
    )

    lat = infrastructure["latitude"]
    lng = infrastructure["longitude"]

    matches = []

    for detection in final_detections:

        if detection.get("source") != "infrastructure":
            continue

        if detection.get("latitude") is None:
            continue

        if detection.get("longitude") is None:
            continue

        detected_type = normalize(
            detection.get("type")
        )

        distance = distance_meters(
            lat,
            lng,
            detection["latitude"],
            detection["longitude"]
        )

        if distance <= MATCH_RADIUS_METERS:

            matches.append({
                "type": detected_type,
                "original_type": detection.get("type"),
                "confidence": detection.get("confidence"),
                "distance": distance
            })

    # Nothing detected
    if not matches:

        if infrastructure["status"] == "MISSING":
            result = "verified_missing"
        else:
            result = "not_reproduced"

        return {
            "location_id": infrastructure["location_id"],
            "event_type": "infrastructure",
            "expected_infrastructure":
                infrastructure["expected_infrastructure"],
            "latitude": lat,
            "longitude": lng,
            "verification_result": result,
            "confidence": None
        }

    # Correct infrastructure detected
    correct_matches = [
        item
        for item in matches
        if item["type"] == expected_type
    ]

    if correct_matches:

        best = max(
            correct_matches,
            key=lambda x: (
                x["confidence"]
                if x["confidence"] is not None
                else 0
            )
        )

        confidence = best["confidence"]

        if confidence is not None:
            confidence = round(
                float(confidence),
                2
            )

        return {
            "location_id": infrastructure["location_id"],
            "event_type": "infrastructure",
            "expected_infrastructure":
                infrastructure["expected_infrastructure"],
            "detected_infrastructure":
                best["original_type"],
            "latitude": lat,
            "longitude": lng,
            "verification_result": "verified_present",
            "confidence": confidence
        }

    # Wrong infrastructure detected
    best = max(
        matches,
        key=lambda x: (
            x["confidence"]
            if x["confidence"] is not None
            else 0
        )
    )

    confidence = best["confidence"]

    if confidence is not None:
        confidence = round(
            float(confidence),
            2
        )

    return {
        "location_id": infrastructure["location_id"],
        "event_type": "infrastructure",
        "expected_infrastructure":
            infrastructure["expected_infrastructure"],
        "detected_infrastructure":
            best["original_type"],
        "latitude": lat,
        "longitude": lng,
        "verification_result": "verified_wrong",
        "confidence": confidence
    }


# =========================================================
# MAIN VERIFICATION LOOP
# =========================================================

def run_verification():

    defects = load_json(DEFECT_FILE)

    infrastructure = load_json(
        INFRASTRUCTURE_FILE
    )

    final_detections = load_json(
        FINAL_DETECTIONS_FILE
    )

    results = []

    # -----------------------------------------
    # Verify road defects
    # -----------------------------------------

    print("Verifying defect events...")

    for index, event in enumerate(defects, start=1):

        result = verify_defect_event(
            event,
            final_detections,
            index
        )

        results.append(result)

    # -----------------------------------------
    # Verify infrastructure
    # -----------------------------------------

    print("Verifying infrastructure...")

    for item in infrastructure:

        result = verify_infrastructure(
            item,
            final_detections
        )

        results.append(result)

    # -----------------------------------------
    # Write verification JSON
    # -----------------------------------------

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            results,
            f,
            indent=2
        )

    print(
        f"Verification output written to: "
        f"{OUTPUT_FILE}"
    )

    print(
        f"Total verification results: "
        f"{len(results)}"
    )


if __name__ == "__main__":
    run_verification()