from weather_api import get_weather


def calculate_waterlogging_risk(
    latitude,
    longitude,
    recent_waterlogging=False,
    historical_waterlogging=False,
    road_vulnerability=False
):
    """
    Calculate waterlogging risk using weather and road/location factors.

    Returns:
        A dictionary containing risk score, risk level, and contributing factors.
    """

    weather = get_weather(latitude, longitude)

    if weather is None:
        return {
            "waterlogging_risk_score": 0,
            "waterlogging_risk_level": "UNKNOWN",
            "factors": ["Weather data unavailable"]
        }

    score = 0
    factors = []

    # --------------------------------------------------
    # 1. Current precipitation
    # --------------------------------------------------

    precipitation = weather.get("precipitation") or 0

    if precipitation >= 10:
        score += 40
        factors.append("Heavy precipitation")

    elif precipitation >= 5:
        score += 25
        factors.append("Moderate precipitation")

    elif precipitation > 0:
        score += 10
        factors.append("Light precipitation")

    # --------------------------------------------------
    # 2. Probability of precipitation
    # --------------------------------------------------

    probability = weather.get("precipitation_probability") or 0

    if probability >= 80:
        score += 25
        factors.append("Very high precipitation probability")

    elif probability >= 50:
        score += 15
        factors.append("High precipitation probability")

    elif probability >= 30:
        score += 5
        factors.append("Moderate precipitation probability")

    # --------------------------------------------------
    # 3. Recent waterlogging observations
    # --------------------------------------------------

    if recent_waterlogging:
        score += 20
        factors.append("Recent waterlogging observation")

    # --------------------------------------------------
    # 4. Historical waterlogging at this location
    # --------------------------------------------------

    if historical_waterlogging:
        score += 15
        factors.append("Historical waterlogging at location")

    # --------------------------------------------------
    # 5. Road/location vulnerability
    # --------------------------------------------------

    if road_vulnerability:
        score += 10
        factors.append("Vulnerable road/location")

    # --------------------------------------------------
    # Keep score between 0 and 100
    # --------------------------------------------------

    score = min(score, 100)

    # --------------------------------------------------
    # Convert score into risk level
    # --------------------------------------------------

    if score >= 70:
        risk_level = "HIGH"

    elif score >= 40:
        risk_level = "MEDIUM"

    else:
        risk_level = "LOW"

    return {
        "latitude": latitude,
        "longitude": longitude,
        "waterlogging_risk_score": score,
        "waterlogging_risk_level": risk_level,
        "factors": factors,
        "weather": weather
    }


# ------------------------------------------------------
# Test
# ------------------------------------------------------

if __name__ == "__main__":

    latitude = 28.6
    longitude = 77.2

    result = calculate_waterlogging_risk(
        latitude,
        longitude,
        recent_waterlogging=False,
        historical_waterlogging=False,
        road_vulnerability=False
    )

    print("\nWaterlogging Risk Result:")
    print(result)