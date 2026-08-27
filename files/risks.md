# Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Poor YOLO detection accuracy (esp. potholes/waterlogging not in stock COCO weights) | High | High | Use a pretrained pothole dataset/model if available; fall back to a smaller "good enough for demo" class set (vehicles, traffic lights are easy — lean on those if potholes underperform); curate a few clean demo clips | Member 1 |
| Insufficient/no labeled dataset for custom classes | High | Medium | Use existing open pothole/road-damage datasets (e.g. Roboflow public sets) rather than labeling from scratch | Member 1 |
| False positives flooding the dashboard | Medium | Medium | Confidence threshold tuning; dedup collapses repeated false flags into one low-priority incident instead of many | Member 1 / 3 |
| GPS simulation doesn't match video path realistically | Medium | Medium | Simple linear interpolation along a predefined route polyline using video timestamp is good enough — explicitly labeled `gps_source: simulated` everywhere so it's never confused with real data | Member 3 |
| Duplicate events not merging correctly | Medium | Medium | Keep dedup rule dead simple (distance+time+type) and test it in isolation with synthetic data before relying on real detections | Member 3 |
| API/integration mismatches between modules | High | High | Canonical Event schema frozen early (this doc), sample payloads in `data/sample_events/`, everyone tests against the schema before integration day | Member 4 (contract owner) |
| Database schema churn breaking others' code | Medium | High | Schema frozen after Phase 0 review; changes require team sign-off; migrations tracked | Member 3/4 |
| Model inference too slow for demo (laggy dashboard) | Medium | Medium | Sample frames (e.g. every Nth frame, not every frame); pre-process demo video offline rather than live if needed | Member 1/2 |
| Public video licensing / usage restrictions | Low | Medium | Use clearly licensed/creative-commons dashcam footage or self-recorded clips only | Whole team |
| Limited hackathon time (scope creep) | High | High | Strict MVP scope (see `mvp-scope.md`), cut "should have"/"nice to have" ruthlessly if behind schedule | Whole team / lead |
| Team members modifying shared contracts without coordination | Medium | High | `data/contracts/**` and core docs flagged as "never modify casually" (see `architecture.md`); PR review required on those paths | Lead architect + Member 4 |
| Frontend blocked waiting on real backend | Medium | Medium | Backend publishes `data/sample_events/*.json` and a mock server / static JSON fixtures early so Frontend can build against the contract before the real API exists | Member 4 / 6 |
