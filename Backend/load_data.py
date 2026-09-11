import json
from pathlib import Path
from datetime import datetime

from app.database import SessionLocal
from app import models


DATA_DIR = Path(__file__).resolve().parent / "data"


def load_events(db):
    if db.query(models.Event).count() > 0:
        print("Events already loaded. Skipping.")
        return

    with open(DATA_DIR / "events.json", "r", encoding="utf-8") as file:
        events = json.load(file)

    for item in events:
        db.add(
            models.Event(
                class_name=item["class_name"],
                severity=item["severity"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                detected_at=datetime.fromisoformat(item["detected_at"]),
                authority=item["authority"],
            )
        )

    print(f"Loaded {len(events)} events.")


def load_infrastructure(db):
    if db.query(models.Infrastructure).count() > 0:
        print("Infrastructure already loaded. Skipping.")
        return

    with open(
        DATA_DIR / "infrastructure.json",
        "r",
        encoding="utf-8"
    ) as file:
        infrastructure = json.load(file)

    for item in infrastructure:
        db.add(
            models.Infrastructure(
                location_id=item["location_id"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                expected_infrastructure=item["expected_infrastructure"],
                detected_infrastructure=item["detected_infrastructure"],
                status=item["status"],
                confidence=item["confidence"],
            )
        )

    print(f"Loaded {len(infrastructure)} infrastructure records.")


def load_traffic(db):
    if db.query(models.TrafficObservation).count() > 0:
        print("Traffic already loaded. Skipping.")
        return

    with open(
        DATA_DIR / "traffic_congestion.json",
        "r",
        encoding="utf-8"
    ) as file:
        traffic = json.load(file)

    for item in traffic:
        db.add(
            models.TrafficObservation(
                frame_id=item["frame_id"],
                timestamp_ms=item["timestamp_ms"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                vehicle_count=item["vehicle_count"],
                avg_speed=item["avg_speed"],
                congestion_level=item["congestion_level"],
            )
        )

    print(f"Loaded {len(traffic)} traffic records.")


def load_verification(db):
    if db.query(models.VerificationRecord).count() > 0:
        print("Verification already loaded. Skipping.")
        return

    with open(
        DATA_DIR / "verification.json",
        "r",
        encoding="utf-8"
    ) as file:
        verification = json.load(file)

    for item in verification:
        db.add(
            models.VerificationRecord(
                event_id=item.get("event_id"),
                location_id=item.get("location_id"),
                event_type=item["event_type"],
                class_name=item.get("class_name"),
                expected_infrastructure=item.get("expected_infrastructure"),
                detected_infrastructure=item.get("detected_infrastructure"),
                latitude=item["latitude"],
                longitude=item["longitude"],
                verification_result=item["verification_result"],
                confidence=item.get("confidence"),
            )
        )

    print(f"Loaded {len(verification)} verification records.")


def load_priority_results(db):
    if db.query(models.PriorityResult).count() > 0:
        print("Priority results already loaded. Skipping.")
        return

    with open(
        DATA_DIR / "output.json",
        "r",
        encoding="utf-8"
    ) as file:
        priority_results = json.load(file)

    for item in priority_results:
        db.add(
            models.PriorityResult(
                event_id=item["event_id"],
                risk_score=item["risk_score"],
                priority=item["priority"],
                factors=item["factors"],
                location=item["location"],
                timestamp=datetime.fromisoformat(item["timestamp"]),
            )
        )

    print(f"Loaded {len(priority_results)} priority results.")


def main():
    db = SessionLocal()

    try:
        load_events(db)
        load_infrastructure(db)
        load_traffic(db)
        load_verification(db)
        load_priority_results(db)

        db.commit()

        print("\nAll JSON data loaded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()