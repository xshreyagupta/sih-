from datetime import datetime, timezone
from typing import Any, Dict


# ============================================================
# Priority Engine - M5
# ============================================================

# Priority thresholds
LOW_THRESHOLD = 25
MEDIUM_THRESHOLD = 50
HIGH_THRESHOLD = 75

# Weights used by the risk calculation
SIGHTING_WEIGHT = 8.0
SEVERITY_TREND_WEIGHT = 5.0
CONGESTION_WEIGHT = 0.15
BOTTLENECK_BONUS = 10.0


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    """Keep a value between minimum and maximum."""
    return max(minimum, min(value, maximum))


def normalize(value: float, minimum: float, maximum: float) -> float:
    """
    Convert a value into a 0-100 range.
    """
    if maximum <= minimum:
        return 0.0

    score = ((value - minimum) / (maximum - minimum)) * 100
    return clamp(score)


def calculate_recency_weight(
    timestamp: str,
    current_time: datetime | None = None
) -> float:
    """
    Calculate a recency weight.

    Very recent events receive a higher weight.
    Older events gradually become less important.

    Returns a value between 0 and 1.
    """

    if not timestamp:
        return 0.5

    try:
        event_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone.utc)

        if current_time is None:
            current_time = datetime.now(timezone.utc)

        age_hours = max(
            0,
            (current_time - event_time).total_seconds() / 3600
        )

        # Recency decreases as the event becomes older.
        # Half-life is approximately 24 hours.
        recency = 1 / (1 + (age_hours / 24))

        return clamp(recency, 0.0, 1.0)

    except (ValueError, TypeError):
        return 0.5


def severity_to_score(severity: Any) -> float:
    """
    Convert severity into a 0-100 score.

    Accepted values:
        low / small
        medium
        high / large
        critical / severe
    """

    if isinstance(severity, (int, float)):
        return clamp(float(severity))

    if not severity:
        return 0.0

    severity = str(severity).strip().lower()

    severity_scores = {
        "low": 25.0,
        "small": 25.0,
        "medium": 50.0,
        "moderate": 50.0,
        "high": 75.0,
        "large": 75.0,
        "critical": 100.0,
        "severe": 100.0,
    }

    return severity_scores.get(severity, 0.0)


def calculate_priority(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate the priority of a road/traffic event.

    Expected event fields may include:

        event_id
        defect_type
        severity
        vehicle_count
        traffic_density
        average_speed
        congestion_level
        congestion_score
        bottleneck
        sighting_count
        severity_trend_slope
        timestamp
        latitude
        longitude

    Returns:

        {
            "event_id": ...,
            "risk_score": ...,
            "priority": ...,
            "factors": {...}
        }
    """

    # --------------------------------------------------------
    # 1. Read input values
    # --------------------------------------------------------

    event_id = event.get("event_id")

    severity = event.get("severity", "low")

    vehicle_count = float(event.get("vehicle_count", 0) or 0)

    traffic_density = float(
        event.get("traffic_density", 0) or 0
    )

    average_speed = float(
        event.get("average_speed", 0) or 0
    )

    congestion_level = float(
        event.get("congestion_level", 0) or 0
    )

    congestion_score_input = event.get("congestion_score")

    bottleneck = event.get("bottleneck", False)

    sighting_count = int(
        event.get("sighting_count", 1) or 1
    )

    severity_trend_slope = float(
        event.get("severity_trend_slope", 0) or 0
    )

    timestamp = event.get("timestamp")

    # --------------------------------------------------------
    # 2. Calculate severity score
    # --------------------------------------------------------

    severity_score = severity_to_score(severity)

    # --------------------------------------------------------
    # 3. Calculate congestion score
    # --------------------------------------------------------

    if congestion_score_input is not None:
        congestion_score = clamp(
            float(congestion_score_input)
        )

    elif congestion_level > 0:
        congestion_score = clamp(congestion_level)

    else:
        # Estimate congestion from vehicle count and speed.
        #
        # Higher vehicle count + lower speed = higher congestion.
        vehicle_score = normalize(
            vehicle_count,
            minimum=0,
            maximum=100
        )

        if average_speed <= 0:
            speed_score = 100.0
        else:
            speed_score = normalize(
                max(0, 60 - average_speed),
                minimum=0,
                maximum=60
            )

        congestion_score = (
            0.5 * vehicle_score +
            0.5 * speed_score
        )

    # --------------------------------------------------------
    # 4. Calculate recency
    # --------------------------------------------------------

    recency_weight = calculate_recency_weight(timestamp)

    # --------------------------------------------------------
    # 5. Calculate recurrence risk
    # --------------------------------------------------------
    #
    # SIH implementation formula:
    #
    # risk_score =
    #     (sighting_count * recency_weight)
    #     +
    #     (severity_trend_slope * weight)
    #
    # --------------------------------------------------------

    recurrence_score = (
        sighting_count
        * recency_weight
        * SIGHTING_WEIGHT
    )

    severity_trend_score = (
        max(0.0, severity_trend_slope)
        * SEVERITY_TREND_WEIGHT
    )

    # --------------------------------------------------------
    # 6. Bottleneck contribution
    # --------------------------------------------------------

    if isinstance(bottleneck, str):
        bottleneck_detected = bottleneck.lower() in {
            "true",
            "yes",
            "1",
            "detected"
        }
    else:
        bottleneck_detected = bool(bottleneck)

    bottleneck_score = (
        BOTTLENECK_BONUS
        if bottleneck_detected
        else 0.0
    )

    # --------------------------------------------------------
    # 7. Congestion contribution
    # --------------------------------------------------------

    congestion_contribution = (
        congestion_score * CONGESTION_WEIGHT
    )

    # --------------------------------------------------------
    # 8. Combine everything
    # --------------------------------------------------------

    raw_score = (
        severity_score * 0.40
        + recurrence_score
        + severity_trend_score
        + congestion_contribution
        + bottleneck_score
    )

    risk_score = round(
        clamp(raw_score),
        2
    )

    # --------------------------------------------------------
    # 9. Convert score into priority tier
    # --------------------------------------------------------

    if risk_score >= HIGH_THRESHOLD:
        priority = "CRITICAL"

    elif risk_score >= MEDIUM_THRESHOLD:
        priority = "HIGH"

    elif risk_score >= LOW_THRESHOLD:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    # --------------------------------------------------------
    # 10. Return explainable result
    # --------------------------------------------------------

    return {
        "event_id": event_id,
        "risk_score": risk_score,
        "priority": priority,

        "factors": {
            "severity_score": round(severity_score, 2),
            "congestion_score": round(congestion_score, 2),
            "sighting_count": sighting_count,
            "recency_weight": round(recency_weight, 3),
            "severity_trend_slope": severity_trend_slope,
            "bottleneck": bottleneck_detected,
            "vehicle_count": vehicle_count,
            "traffic_density": traffic_density,
            "average_speed": average_speed,
        },

        "location": {
            "latitude": event.get("latitude"),
            "longitude": event.get("longitude"),
        },

        "timestamp": timestamp,
    }


# ============================================================
# Simple local testing
# ============================================================

if __name__ == "__main__":

    test_events = [

        {
            "event_id": "TEST-001",
            "defect_type": "pothole",
            "severity": "low",
            "vehicle_count": 20,
            "traffic_density": 20,
            "average_speed": 45,
            "congestion_level": 20,
            "bottleneck": False,
            "sighting_count": 1,
            "severity_trend_slope": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 12.9716,
            "longitude": 77.5946,
        },

        {
            "event_id": "TEST-002",
            "defect_type": "pothole",
            "severity": "high",
            "vehicle_count": 80,
            "traffic_density": 85,
            "average_speed": 15,
            "congestion_level": 85,
            "bottleneck": True,
            "sighting_count": 4,
            "severity_trend_slope": 3,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 12.9716,
            "longitude": 77.5946,
        },

        {
            "event_id": "TEST-003",
            "defect_type": "waterlogging",
            "severity": "critical",
            "vehicle_count": 95,
            "traffic_density": 95,
            "average_speed": 5,
            "congestion_level": 95,
            "bottleneck": True,
            "sighting_count": 8,
            "severity_trend_slope": 5,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": 12.9717,
            "longitude": 77.5947,
        },
    ]

    for event in test_events:

        result = calculate_priority(event)

        print("\n" + "=" * 50)
        print("EVENT:", result["event_id"])
        print("RISK SCORE:", result["risk_score"])
        print("PRIORITY:", result["priority"])
        print("FACTORS:", result["factors"])
        print("LOCATION:", result["location"])