# Detection Taxonomy (canonical class names — never vary between modules)

Vehicles are split into subtypes because tracking/counting needs it, but they roll up to a
single parent for anything that just needs "is this a vehicle" (priority engine, dedup).

## Priority 1 — road defects (core value prop)
- `pothole`
- `vehicle_car`
- `vehicle_bus`
- `vehicle_truck`
- `vehicle_motorcycle`
  - parent group: `vehicle` (used only for aggregate counting/congestion, never emitted as
    a raw `event_type`)

## Priority 2 — traffic infrastructure
- `traffic_sign`
- `traffic_light`
- `road_divider`
- `zebra_crossing`

## Priority 3 — context / environment
- `waterlogging`
- `pedestrian`
- `streetlight`

## Rules

1. `event_type` in the Event schema must be one of the **leaf** class names above — never
   `vehicle` alone.
2. The CV module (Member 1) outputs raw YOLO class names, which MUST already match this list
   exactly (train/label using these names, or map at inference time in `cv/classes.py`).
3. Tracking (Member 2) uses the `vehicle_*` classes for counting/speed/congestion but does not
   invent new class names.
4. Adding a new class requires updating: `cv/classes.py`, `data/contracts/detection_classes.json`,
   this file, and the DB enum/check-constraint in `database-schema.md` — announce in team
   channel before doing so (this is a shared contract file).

## Canonical list (flat, copy-paste for code)

```
pothole
vehicle_car
vehicle_bus
vehicle_truck
vehicle_motorcycle
traffic_sign
traffic_light
road_divider
zebra_crossing
waterlogging
pedestrian
streetlight
```
