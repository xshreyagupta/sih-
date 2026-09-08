from datetime import datetime, timezone
from typing import Any, Dict
import json
import math
import os


# ============================================================
# M5 - PRIORITY / RISK ENGINE
# ============================================================

# ------------------------------------------------------------
# File paths
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_FILE = os.path.join(BASE_DIR, "test_data.json")
OUTPUT_FILE = os.path.join(BASE_DIR, "output.json")


# ------------------------------------------------------------
# Priority thresholds
# ------------------------------------------------------------

LOW_THRESHOLD = 25
MEDIUM_THRESHOLD = 50
HIGH_THRESHOLD = 75


# ------------------------------------------------------------
# Weights used in risk calculation
# ------------------------------------------------------------

SIGHTING_WEIGHT = 8.0
SEVERITY_TREND_WEIGHT = 5.0
CONGESTION_WEIGHT = 0.15
BOTTLENECK_WEIGHT = 10.0


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clamp(value: float, minimum: float = 0, maximum: float = 100) -> float:
    """
    Keep a value between minimum and maximum.
    """
    return max(minimum, min(value, maximum))


def normalize(value: float, minimum: float, maximum: float) -> float:
    """
    Convert a value from a given range into 0-100.
    """
    if maximum <= minimum:
        return 0.0

    return clamp(
        ((value - minimum) / (maximum - minimum)) * 100
    )


def calculate_recency_weight(timestamp: Any) -> float:
    """
    Recent observations get a higher weight.

    Uses approximately a 24-hour half-life.
    """

    if timestamp is None:
        return 1.0

    try:

        # If timestamp is numeric, treat it as Unix timestamp.
        if isinstance(timestamp, (int, float)):
            event_time = datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc
            )

        else:
            timestamp_string = str(timestamp)

            # Handle timestamps ending in Z
            if timestamp_string.endswith("Z"):
                timestamp_string = timestamp_string[:-1] + "+00:00"

            event_time = datetime.fromisoformat(timestamp_string)

            # If no timezone is provided, assume UTC.
            if event_time.tzinfo is None:
                event_time = event_time.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)

        age_hours = max(
            0,
            (now - event_time).total_seconds() / 3600
        )

        # 24-hour half-life
        weight = math.pow(0.5, age_hours / 24)

        return clamp(weight, 0, 1)

    except Exception:
        # If timestamp is invalid, don't crash the whole system.
        return 1.0


def severity_to_score(severity: Any) -> float:
    """
    Convert severity into a 0-100 score.
    """

    if severity is None:
        return 25.0

    severity_string = str(severity).strip().lower()

    severity_map = {
        "low": 25,
        "small": 25,

        "medium": 50,
        "moderate": 50,

        "high": 75,
        "large": 75,

        "critical": 100,
        "severe": 100
    }

    # If severity is already numeric
    if isinstance(severity, (int, float)):
        return clamp(float(severity))

    return severity_map.get(severity_string, 25.0)


def congestion_to_score(congestion_level: Any) -> float:
    """
    Convert M2's congestion level into a numerical score.

    M2 outputs:
        LOW
        MEDIUM
        HIGH

    M5 converts these into numerical values for risk calculation.
    """

    if congestion_level is None:
        return 0.0

    # If M2 or another module already gives a number,
    # use it directly.
    if isinstance(congestion_level, (int, float)):
        return clamp(float(congestion_level))

    level = str(congestion_level).strip().lower()

    congestion_map = {
        "low": 25.0,
        "medium": 50.0,
        "high": 75.0,
        "critical": 100.0
    }

    return congestion_map.get(level, 0.0)


# ============================================================
# CONGESTION CALCULATION
# ============================================================

def calculate_congestion_score(event: Dict[str, Any]) -> float:
    """
    Determine congestion contribution to the risk score.

    Priority:

    1. Use congestion_score if supplied.
    2. Otherwise use congestion_level from M2.
    3. Otherwise estimate congestion from vehicle count
       and average speed.
    """

    # --------------------------------------------------------
    # Case 1: numerical congestion score already supplied
    # --------------------------------------------------------

    if event.get("congestion_score") is not None:

        try:
            return clamp(
                float(event["congestion_score"])
            )

        except (ValueError, TypeError):
            pass


    # --------------------------------------------------------
    # Case 2: M2 gives LOW / MEDIUM / HIGH
    # --------------------------------------------------------

    if event.get("congestion_level") is not None:

        score = congestion_to_score(
            event["congestion_level"]
        )

        if score > 0:
            return score


    # --------------------------------------------------------
    # Case 3: derive congestion from traffic data
    # --------------------------------------------------------

    vehicle_count = event.get("vehicle_count", 0)
    average_speed = event.get("average_speed")

    try:
        vehicle_count = float(vehicle_count)
    except (ValueError, TypeError):
        vehicle_count = 0.0

    try:
        average_speed = float(average_speed)
    except (ValueError, TypeError):
        average_speed = None


    # High vehicle density
    density_score = normalize(
        vehicle_count,
        0,
        50
    )

    # Lower speed = higher congestion
    if average_speed is not None:

        speed_score = clamp(
            100 - normalize(
                average_speed,
                0,
                60
            )
        )

    else:
        speed_score = 0.0


    # Combine density and speed
    if average_speed is not None:
        return (
            density_score * 0.6
            + speed_score * 0.4
        )

    return density_score


# ============================================================
# PRIORITY CALCULATION
# ============================================================

def calculate_priority(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate the final risk score and priority
    for one event.
    """

    # --------------------------------------------------------
    # Basic event information
    # --------------------------------------------------------

    event_id = event.get(
        "event_id",
        "unknown_event"
    )

    defect_type = event.get(
        "defect_type",
        event.get("type", "unknown")
    )

    severity = event.get(
        "severity",
        "low"
    )

    # --------------------------------------------------------
    # Severity score
    # --------------------------------------------------------

    severity_score = severity_to_score(
        severity
    )


    # --------------------------------------------------------
    # Recurrence / repeated sightings
    # --------------------------------------------------------

    sighting_count = event.get(
        "sighting_count",
        1
    )

    try:
        sighting_count = max(
            1,
            float(sighting_count)
        )

    except (ValueError, TypeError):
        sighting_count = 1.0


    recency_weight = calculate_recency_weight(
        event.get("timestamp")
    )


    recurrence_score = (
        sighting_count
        * recency_weight
        * SIGHTING_WEIGHT
    )


    # --------------------------------------------------------
    # Severity trend
    # --------------------------------------------------------

    severity_trend_slope = event.get(
        "severity_trend_slope",
        0
    )

    try:
        severity_trend_slope = float(
            severity_trend_slope
        )

    except (ValueError, TypeError):
        severity_trend_slope = 0.0


    # Only worsening severity contributes.
    severity_trend_score = (
        max(0, severity_trend_slope)
        * SEVERITY_TREND_WEIGHT
    )


    # --------------------------------------------------------
    # Congestion
    # --------------------------------------------------------

    congestion_score = calculate_congestion_score(
        event
    )

    congestion_contribution = (
        congestion_score
        * CONGESTION_WEIGHT
    )


    # --------------------------------------------------------
    # Bottleneck
    # --------------------------------------------------------

    bottleneck = event.get(
        "bottleneck",
        False
    )

    # Handle strings such as "true" / "false"
    if isinstance(bottleneck, str):

        bottleneck = bottleneck.strip().lower() in (
            "true",
            "yes",
            "1"
        )

    bottleneck_score = (
        BOTTLENECK_WEIGHT
        if bottleneck
        else 0.0
    )


    # ========================================================
    # FINAL RISK SCORE
    # ========================================================

    raw_score = (

        # Severity is the main factor
        severity_score * 0.40

        # Repeated sightings
        + recurrence_score

        # Worsening condition
        + severity_trend_score

        # Traffic/congestion
        + congestion_contribution

        # Bottleneck bonus
        + bottleneck_score
    )


    risk_score = clamp(
        raw_score
    )


    # ========================================================
    # PRIORITY LEVEL
    # ========================================================

    if risk_score >= HIGH_THRESHOLD:

        priority = "CRITICAL"

    elif risk_score >= MEDIUM_THRESHOLD:

        priority = "HIGH"

    elif risk_score >= LOW_THRESHOLD:

        priority = "MEDIUM"

    else:

        priority = "LOW"


    # ========================================================
    # OUTPUT
    # ========================================================

    return {

        "event_id": event_id,

        "defect_type": defect_type,

        "risk_score": round(
            risk_score,
            2
        ),

        "priority": priority,

        "factors": {

            "severity_score": round(
                severity_score,
                2
            ),

            "sighting_count": sighting_count,

            "recency_weight": round(
                recency_weight,
                4
            ),

            "recurrence_score": round(
                recurrence_score,
                2
            ),

            "severity_trend_slope": round(
                severity_trend_slope,
                2
            ),

            "severity_trend_score": round(
                severity_trend_score,
                2
            ),

            "congestion_score": round(
                congestion_score,
                2
            ),

            "congestion_contribution": round(
                congestion_contribution,
                2
            ),

            "bottleneck": bottleneck,

            "bottleneck_score": round(
                bottleneck_score,
                2
            )
        }
    }


# ============================================================
# LOAD INPUT
# ============================================================

def load_input() -> Any:

    if not os.path.exists(INPUT_FILE):

        print(
            f"ERROR: Input file not found: {INPUT_FILE}"
        )

        return []

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        return data

    except json.JSONDecodeError as error:

        print(
            "ERROR: test_data.json contains invalid JSON."
        )

        print(error)

        return []

    except Exception as error:

        print(
            f"ERROR while reading input: {error}"
        )

        return []


# ============================================================
# SAVE OUTPUT
# ============================================================

def save_output(results: list):

    try:

        with open(
            OUTPUT_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                results,
                file,
                indent=4
            )

        print(
            f"\nOutput saved to: {OUTPUT_FILE}"
        )

    except Exception as error:

        print(
            f"ERROR while saving output: {error}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("M5 PRIORITY ENGINE")
    print("=" * 60)

    print(
        f"\nReading input from:\n{INPUT_FILE}"
    )

    data = load_input()


    # --------------------------------------------------------
    # Accept either:
    #
    # 1. A list of events
    #
    # [
    #   {...},
    #   {...}
    # ]
    #
    # OR
    #
    # 2. An object containing "events"
    #
    # {
    #   "events": [...]
    # }
    # --------------------------------------------------------

    if isinstance(data, dict):

        events = data.get(
            "events",
            []
        )

    elif isinstance(data, list):

        events = data

    else:

        print(
            "ERROR: Input must be a JSON list or an object containing 'events'."
        )

        return


    print(
        f"\nEvents loaded: {len(events)}"
    )


    results = []


    # --------------------------------------------------------
    # Process every event
    # --------------------------------------------------------

    for index, event in enumerate(events, start=1):

        if not isinstance(event, dict):

            print(
                f"Skipping event {index}: not a JSON object."
            )

            continue


        result = calculate_priority(
            event
        )

        results.append(
            result
        )


        print(
            f"\nEvent {index}: "
            f"{result['event_id']}"
        )

        print(
            f"Risk Score: "
            f"{result['risk_score']}"
        )

        print(
            f"Priority: "
            f"{result['priority']}"
        )


    # --------------------------------------------------------
    # Save final output
    # --------------------------------------------------------

    save_output(
        results
    )


    print("\n" + "=" * 60)
    print("M5 PRIORITY ENGINE COMPLETE")
    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()