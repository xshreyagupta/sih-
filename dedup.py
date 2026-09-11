from db import query
from authority_lookup import get_authority_for_event

RELEVANT_CLASSES = {
    "longitudinal_crack", "transverse_crack", "alligator_crack", "pothole"
}

def estimate_severity(bbox):
    x1, y1, x2, y2 = bbox
    area = (x2 - x1) * (y2 - y1)
    if area < 5000: return "small"
    elif area < 20000: return "medium"
    else: return "large"

def find_or_create_event(defect_type, lat, lng, severity, bus_id, frame_id, track_id=None):
    existing = query("""
        SELECT id FROM events
        WHERE defect_type = %s
          AND status NOT IN ('verified_closed')
          AND ST_DWithin(geom, ST_MakePoint(%s,%s)::geography, 15)
        ORDER BY detected_at DESC LIMIT 1
    """, (defect_type, lng, lat))

    if existing:
        eid = existing[0]["id"]
        query("""
            UPDATE events SET sighting_count = sighting_count + 1, detected_at = now()
            WHERE id = %s
        """, (eid,), fetch=False)
        return eid, None
    else:
        result = query("""
            INSERT INTO events (defect_type, severity, geom, bus_id)
            VALUES (%s, %s, ST_MakePoint(%s,%s)::geography, %s)
            RETURNING id
        """, (defect_type, severity, lng, lat, bus_id))
    eid= result[0]["id"]
    authority = get_authority_for_event(defect_type)
    return eid, authority