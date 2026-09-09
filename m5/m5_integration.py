import json

from priority_engine import calculate_priority
from prediction_engine import calculate_prediction
from waterlogging_risk import calculate_waterlogging_risk


def process_m5_event(event):
    """
    Main M5 integration function.

    Input:
        Combined event data from M2 + M3/context.

    Processing:
        1. Waterlogging risk
        2. Prediction
        3. Priority

    Timestamps:
        timestamp_ms -> video/event timeline
        timestamp    -> real observation time
    """

    latitude = event.get("latitude")
    longitude = event.get("longitude")

    # ==========================================
    # 1. WATERLOGGING RISK
    # ==========================================

    if latitude is not None and longitude is not None:

        waterlogging_result = calculate_waterlogging_risk(
            latitude=latitude,
            longitude=longitude,
            recent_waterlogging=event.get(
                "recent_waterlogging",
                False
            ),
            historical_waterlogging=event.get(
                "historical_waterlogging",
                False
            ),
            road_vulnerability=event.get(
                "road_vulnerability",
                False
            )
        )

    else:

        waterlogging_result = {
            "waterlogging_risk_score": 0,
            "waterlogging_risk_level": "UNKNOWN",
            "factors": [
                "GPS data unavailable"
            ]
        }

    # ==========================================
    # 2. PREDICTION ENGINE
    # ==========================================

    prediction_result = calculate_prediction(
        sighting_count=event.get(
            "sighting_count",
            0
        ),
        recency_weight=event.get(
            "recency_weight",
            1.0
        ),
        severity_trend_slope=event.get(
            "severity_trend_slope",
            0
        ),
        congestion_trend=event.get(
            "congestion_trend",
            0
        ),
        recent_observation=event.get(
            "recent_observation",
            False
        )
    )

    # ==========================================
    # 3. PRIORITY ENGINE
    # ==========================================

    # Make a copy so original input is not modified
    priority_event = dict(event)

    # M2 provides "avg_speed"
    # Priority engine expects "average_speed"
    priority_event["average_speed"] = event.get(
        "avg_speed"
    )

    priority_result = calculate_priority(
        priority_event
    )

    # ==========================================
    # 4. FINAL M5 OUTPUT
    # ==========================================

    final_result = {

        # Event information
        "event_id": event.get(
            "event_id"
        ),

        "defect_type": event.get(
            "defect_type"
        ),

        "severity": event.get(
            "severity"
        ),

        # GPS
        "latitude": latitude,
        "longitude": longitude,

        # Both timestamps
        "timestamp_ms": event.get(
            "timestamp_ms"
        ),

        "timestamp": event.get(
            "timestamp"
        ),

        # M2 traffic information
        "vehicle_count": event.get(
            "vehicle_count"
        ),

        "current_vehicle_count": event.get(
            "current_vehicle_count"
        ),

        "avg_speed": event.get(
            "avg_speed"
        ),

        "congestion_level": event.get(
            "congestion_level"
        ),

        # Waterlogging observation
        "waterlogging_detected": event.get(
            "waterlogging_detected",
            False
        ),

        # M5 intelligence
        "priority": priority_result,

        "prediction": prediction_result,

        "waterlogging_risk": waterlogging_result
    }

    return final_result


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    # Read the existing dummy input
    with open(
        "m5/dummy_m5_input.json",
        "r"
    ) as file:

        event = json.load(file)

    # Process through complete M5 pipeline
    result = process_m5_event(event)

    # ==========================================
    # PRINT RESULT
    # ==========================================

    print(
        "\n========== FINAL M5 RESULT ==========\n"
    )

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    # ==========================================
    # UPDATE EXISTING output.json
    # ==========================================

    with open(
        "m5/output.json",
        "w"
    ) as file:

        json.dump(
            result,
            file,
            indent=4
        )

    print(
        "\nM5 output updated successfully in m5/output.json"
    )