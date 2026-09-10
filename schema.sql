CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE events (
  id SERIAL PRIMARY KEY,
  defect_type TEXT NOT NULL,
  severity TEXT,
  geom GEOGRAPHY(POINT, 4326),
  detected_at TIMESTAMP DEFAULT now(),
  bus_id TEXT,
  status TEXT DEFAULT 'open',
  sighting_count INT DEFAULT 1
);
CREATE INDEX events_geom_idx ON events USING GIST (geom);

CREATE TABLE authorities (
  id SERIAL PRIMARY KEY,
  name TEXT,
  defect_type TEXT
);

CREATE TABLE alerts (
  id SERIAL PRIMARY KEY,
  event_id INT REFERENCES events(id),
  authority_id INT REFERENCES authorities(id),
  sent_at TIMESTAMP DEFAULT now(),
  sla_deadline TIMESTAMP
);

CREATE TABLE status_history (
  id SERIAL PRIMARY KEY,
  event_id INT REFERENCES events(id),
  old_status TEXT,
  new_status TEXT,
  changed_at TIMESTAMP DEFAULT now()
);

CREATE TABLE verification_queue (
  id SERIAL PRIMARY KEY,
  event_id INT REFERENCES events(id),
  geom GEOGRAPHY(POINT, 4326),
  defect_type TEXT,
  marked_resolved_at TIMESTAMP DEFAULT now(),
  passes_checked INT DEFAULT 0,
  passes_needed INT DEFAULT 2,
  status TEXT DEFAULT 'pending_verification'
);

CREATE TABLE reference_signboards (
  id SERIAL PRIMARY KEY,
  expected_type TEXT NOT NULL,
  geom GEOGRAPHY(POINT, 4326) NOT NULL,
  notes TEXT
);
CREATE INDEX ref_signboards_geom_idx ON reference_signboards USING GIST (geom);

CREATE TABLE signboard_checks (
  id SERIAL PRIMARY KEY,
  reference_id INT REFERENCES reference_signboards(id),
  pass_id TEXT,
  detected_type TEXT,
  match_status TEXT,
  checked_at TIMESTAMP DEFAULT now()
);

INSERT INTO authorities (name, defect_type) VALUES
('PWD', 'pothole'),
('PWD', 'longitudinal_crack'),
('PWD', 'transverse_crack'),
('PWD', 'alligator_crack'),
('Traffic Police', 'signboard_mismatch'),
('Traffic Police', 'signboard_missing'),
('Traffic Police', 'traffic_light_broken'),
('Electrical Dept', 'street_light_broken'),
('Munnicipal Dept', 'waterlogging'),
('Fire Department', 'fire_hazard'),
('Water Department', 'drain_blockage');

INSERT INTO reference_signboards (expected_type, geom, notes) VALUES
('speed_limit_sign', ST_MakePoint(77.1050, 28.7060)::geography, 'Near waypoint 2'),
('stop_sign',   ST_MakePoint(77.1100, 28.7100)::geography, 'Near waypoint 4');

CREATE TABLE congestion_readings (
  id SERIAL PRIMARY KEY,
  geom GEOGRAPHY(POINT, 4326),
  vehicle_count INT,
  avg_speed FLOAT,
  congestion_level TEXT,
  bus_id TEXT,
  recorded_at TIMESTAMP DEFAULT now()
);
CREATE INDEX congestion_geom_idx ON congestion_readings USING GIST (geom);