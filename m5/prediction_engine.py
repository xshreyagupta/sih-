def calculate_prediction(
    sighting_count=0,
    recency_weight=1.0,
    severity_trend_slope=0.0,
    congestion_trend=0.0,
    recent_observation=False
):
    """
    Calculate future risk using historical observations and trends.

    This is a rule/statistics-based prediction.
    No machine learning model is used.
    """

    # --------------------------------------------------
    # 1. Recurrence score
    # --------------------------------------------------

    sighting_count = max(1, sighting_count)

    recurrence_score = (
        sighting_count * recency_weight
    )

    # --------------------------------------------------
    # 2. Severity trend
    # --------------------------------------------------

    severity_trend_score = max(
        0.0,
        severity_trend_slope
    )

    # --------------------------------------------------
    # 3. Congestion trend
    # --------------------------------------------------

    congestion_trend_score = max(
        0.0,
        congestion_trend
    )

    # --------------------------------------------------
    # 4. Recent observation
    # --------------------------------------------------

    recent_score = 10 if recent_observation else 0

    # --------------------------------------------------
    # 5. Final prediction score
    # --------------------------------------------------

    prediction_score = (
        recurrence_score
        + severity_trend_score * 5
        + congestion_trend_score * 0.15
        + recent_score
    )

    # Keep score between 0 and 100
    prediction_score = min(
        100,
        max(0, prediction_score)
    )

    # --------------------------------------------------
    # 6. Convert score to prediction level
    # --------------------------------------------------

    if prediction_score >= 75:
        prediction_level = "HIGH"

    elif prediction_score >= 40:
        prediction_level = "MEDIUM"

    else:
        prediction_level = "LOW"

    return {
        "prediction_score": round(prediction_score, 2),
        "prediction_level": prediction_level,
        "recurrence_score": round(recurrence_score, 2),
        "severity_trend_score": round(
            severity_trend_score * 5, 2
        ),
        "congestion_trend_score": round(
            congestion_trend_score * 0.15, 2
        ),
        "recent_observation_score": recent_score
    }


# ------------------------------------------------------
# Basic test
# ------------------------------------------------------

if __name__ == "__main__":

    result = calculate_prediction(
        sighting_count=5,
        recency_weight=1.0,
        severity_trend_slope=3,
        congestion_trend=50,
        recent_observation=True
    )

    print("\nPrediction Result:")
    print(result)