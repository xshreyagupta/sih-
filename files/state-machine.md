# Event/Incident Status State Machine

Status lives on the **Incident** (the deduplicated real-world defect), not on every raw
Event — raw events are immutable sightings. See `event-schema.md` / `database-schema.md` for
the Event vs Incident distinction.

## States

```
OPEN
  │  (ops/admin acknowledges, or auto after N sightings)
  ▼
ACKNOWLEDGED
  │  (repair crew dispatched — manual API call)
  ▼
IN_PROGRESS
  │  (repair crew marks done — manual API call)
  ▼
RESOLVED
  │  (system waits for next bus pass over that segment)
  ▼
PENDING_VERIFICATION
  │
  ├── no re-detection within N passes ──► VERIFIED
  │
  └── re-detected (same type, same location) ──► DISPUTED ──► RE_ESCALATED ──► back to OPEN/ACKNOWLEDGED
```

## Transition table

| From | To | Trigger | Who/what triggers it |
|---|---|---|---|
| — | `OPEN` | New incident created (first sighting, or dedup groups sightings) | Backend, automatic |
| `OPEN` | `ACKNOWLEDGED` | Ops reviews and confirms it's real / assigns to a crew | Manual, via `PATCH /events/{id}/status` |
| `ACKNOWLEDGED` | `IN_PROGRESS` | Repair work started | Manual |
| `IN_PROGRESS` | `RESOLVED` | Repair crew reports completion | Manual |
| `RESOLVED` | `PENDING_VERIFICATION` | Automatic, immediately on entering `RESOLVED` | Backend, automatic |
| `PENDING_VERIFICATION` | `VERIFIED` | No re-detection of same `event_type` within `VERIFICATION_PASSES_REQUIRED` (default **2**) subsequent bus passes over that road segment | Backend, automatic (see `verification` logic) |
| `PENDING_VERIFICATION` | `DISPUTED` | Same `event_type` re-detected on that road segment while status is `PENDING_VERIFICATION` | Backend, automatic |
| `DISPUTED` | `RE_ESCALATED` | Ops confirms the re-detection is genuine (not a false positive) | Manual, or automatic if confidence > threshold |
| `RE_ESCALATED` | `OPEN` (or directly `ACKNOWLEDGED`) | Ops restarts the repair workflow | Manual |
| `OPEN`/`ACKNOWLEDGED` | `DISPUTED` | not valid — dispute only applies post-resolution | — |

**Invalid transitions** (reject with HTTP 409): any transition that skips states forward
(e.g. `OPEN` → `RESOLVED` directly) except for admin override, which must be explicit
(`force=true` query param, logged in status history with a reason).

## Status history

Every transition is appended to `STATUS_HISTORY` (see `database-schema.md`) with:
`incident_id, from_status, to_status, changed_by, changed_at, reason (optional), triggering_event_id (optional, for automatic re-detection transitions)`.

This is required — it's what makes the verification/re-escalation story demoable and
auditable, and it's cheap to build (one extra table + one insert per transition).
