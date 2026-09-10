import json

from db import query
from authority_lookup import get_authority_for_event

OUTPUT_FILE = "events.json"


def generate_events_output():
    """
    Export already-deduplicated events from the events table.

    Deduplication is handled exclusively by dedup.py.
    This file only formats the database records into JSON.
    """

    rows = query("""
        SELECT
            defect_type,
            severity,
            detected_at,
            ST_Y(geom::geometry) AS latitude,
            ST_X(geom::geometry) AS longitude
        FROM events
        ORDER BY detected_at ASC
    """)

    results = []

    for row in rows:
        authority = get_authority_for_event(row["defect_type"])

        results.append({
            "class_name": row["defect_type"],
            "severity": row["severity"],
            "latitude": round(float(row["latitude"]), 6),
            "longitude": round(float(row["longitude"]), 6),
            "detected_at": (
                row["detected_at"].isoformat()
                if row["detected_at"] is not None
                else None
            ),
            "authority": authority
        })

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Events output written to: {OUTPUT_FILE}")
    print(f"Events exported: {len(results)}")


if __name__ == "__main__":
    generate_events_output()