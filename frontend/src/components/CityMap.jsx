import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  useMap,
} from "react-leaflet";

import L from "leaflet";
import "leaflet.heat";

import { onIssuesRefresh } from "../issuesRefresh";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

const priorityColors = {
  CRITICAL: "#dc2626",
  HIGH: "#ea580c",
  MEDIUM: "#ca8a04",
  LOW: "#16a34a",
};

const createIssueIcon = (priority) => {
  const color = priorityColors[priority?.toUpperCase()] || "#64748b";

  return L.divIcon({
    className: "",
    html: `
      <div style="
        width:16px;
        height:16px;
        border-radius:50%;
        background:${color};
        border:3px solid white;
        box-shadow:0 1px 5px rgba(0,0,0,0.3);
      "></div>
    `,
    iconSize: [16, 16],
    iconAnchor: [8, 8],
  });
};

const createInfrastructureIcon = () =>
  L.divIcon({
    className: "",
    html: `
      <div style="
        width:18px;
        height:18px;
        border-radius:4px;
        background:#7c3aed;
        border:3px solid white;
        box-shadow:0 1px 5px rgba(0,0,0,0.3);
      "></div>
    `,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });

function formatEventType(eventType) {
  if (!eventType) return "Unknown";
  return String(eventType)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(date) {
  if (!date) return "—";
  const parsed = new Date(date);
  if (Number.isNaN(parsed.getTime())) return "—";
  return parsed.toLocaleString();
}

function HeatmapLayer({ points }) {
  const map = useMap();

  useEffect(() => {
    if (!map || !points.length) return;

    const heatPoints = points.map((point) => [point[0], point[1], point[2]]);

    const heatLayer = L.heatLayer(heatPoints, {
      radius: 35,
      blur: 25,
      maxZoom: 17,
      max: 1.0,
      minOpacity: 0.35,
      gradient: {
        0.2: "#3b82f6",
        0.4: "#22c55e",
        0.6: "#eab308",
        0.8: "#f97316",
        1.0: "#ef4444",
      },
    });

    heatLayer.addTo(map);

    return () => {
      map.removeLayer(heatLayer);
    };
  }, [map, points]);

  return null;
}

function CityMap() {
  const [incidentMarkers, setIncidentMarkers] = useState([]);
  const [infrastructureMarkers, setInfrastructureMarkers] = useState([]);
  const [trafficMarkers, setTrafficMarkers] = useState([]);

  const [issueFilter, setIssueFilter] = useState("all");

  const [showIssues, setShowIssues] = useState(true);
  const [showInfrastructure, setShowInfrastructure] = useState(true);
  const [showTraffic, setShowTraffic] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);

  async function loadMapData() {
    try {
      const [incidentsResponse, infrastructureResponse, trafficResponse] =
        await Promise.all([
          fetch(`${API_BASE_URL}/incidents`),
          fetch(`${API_BASE_URL}/infrastructure`),
          fetch(`${API_BASE_URL}/traffic`),
        ]);

      if (
        !incidentsResponse.ok ||
        !infrastructureResponse.ok ||
        !trafficResponse.ok
      ) {
        throw new Error("Failed to load map data.");
      }

      const incidents = await incidentsResponse.json();
      const infrastructure = await infrastructureResponse.json();
      const traffic = await trafficResponse.json();

      const formattedIncidents = (Array.isArray(incidents) ? incidents : [])
        .filter(
          (incident) =>
            incident.latitude != null &&
            incident.longitude != null &&
            String(incident.status || "").toLowerCase() !== "resolved"
        )
        .map((incident) => ({
          id: `INC-${String(incident.id).padStart(3, "0")}`,
          backendId: incident.id,
          position: [Number(incident.latitude), Number(incident.longitude)],
          type: formatEventType(incident.event_type),
          severity: String(incident.priority || "LOW").toUpperCase(),
          riskScore:
            typeof incident.risk_score === "number"
              ? incident.risk_score
              : null,
          detectedAt: incident.created_at,
          authority: incident.authority || "—",
          status: incident.status || "Open",
        }));

      const formattedInfrastructure = (
        Array.isArray(infrastructure) ? infrastructure : []
      )
        .filter((item) => item.latitude != null && item.longitude != null)
        .map((item) => ({
          id: item.location_id,
          position: [Number(item.latitude), Number(item.longitude)],
          expected: item.expected_infrastructure,
          detected: item.detected_infrastructure,
          status: item.status,
          confidence: item.confidence,
        }));

      const formattedTraffic = (Array.isArray(traffic) ? traffic : [])
        .filter((item) => item.latitude != null && item.longitude != null)
        .map((item) => ({
          id: item.frame_id,
          position: [Number(item.latitude), Number(item.longitude)],
          vehicleCount: item.vehicle_count,
          averageSpeed: item.avg_speed,
          congestionLevel: item.congestion_level,
          timestamp: item.timestamp_ms,
        }));

      setIncidentMarkers(formattedIncidents);
      setInfrastructureMarkers(formattedInfrastructure);
      setTrafficMarkers(formattedTraffic);
    } catch (error) {
      console.error("Failed to load map data:", error);
      setIncidentMarkers([]);
      setInfrastructureMarkers([]);
      setTrafficMarkers([]);
    }
  }

  useEffect(() => {
    loadMapData();
  }, []);

  useEffect(() => {
    const unsubscribe = onIssuesRefresh(() => {
      loadMapData();
    });
    return unsubscribe;
  }, []);

  const issueTypes = [...new Set(incidentMarkers.map((issue) => issue.type))];

  const filteredIssues =
    issueFilter === "all"
      ? incidentMarkers
      : incidentMarkers.filter((issue) => issue.type === issueFilter);

  const heatmapPoints = filteredIssues.map((issue) => {
    const intensity =
      typeof issue.riskScore === "number"
        ? Math.max(0.3, issue.riskScore / 100)
        : 0.5;
    return [issue.position[0], issue.position[1], intensity];
  });

  return (
    <div className="city-map">
      <div className="map-controls">
        <select
          value={issueFilter}
          onChange={(event) => setIssueFilter(event.target.value)}
        >
          <option value="all">Filter by Issues</option>
          {issueTypes.map((type) => (
            <option value={type} key={type}>
              {type}
            </option>
          ))}
        </select>

        <div className="map-control-divider"></div>

        <label>
          <input
            type="checkbox"
            checked={showIssues}
            onChange={(event) => setShowIssues(event.target.checked)}
          />
          Issues
        </label>

        <label>
          <input
            type="checkbox"
            checked={showInfrastructure}
            onChange={(event) => setShowInfrastructure(event.target.checked)}
          />
          Infrastructure
        </label>

        <label>
          <input
            type="checkbox"
            checked={showTraffic}
            onChange={(event) => setShowTraffic(event.target.checked)}
          />
          Traffic
        </label>

        <label>
          <input
            type="checkbox"
            checked={showHeatmap}
            onChange={(event) => setShowHeatmap(event.target.checked)}
          />
          Heatmap
        </label>
      </div>

      <MapContainer
        center={[28.6358, 77.2245]}
        zoom={12}
        scrollWheelZoom={true}
        style={{ width: "100%", flex: 1 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {showHeatmap && heatmapPoints.length > 0 && (
          <HeatmapLayer points={heatmapPoints} />
        )}

        {showIssues &&
          filteredIssues.map((issue) => (
            <Marker
              key={issue.id}
              position={issue.position}
              icon={createIssueIcon(issue.severity)}
            >
              <Popup>
                <strong>{issue.id}</strong>
                <br />
                Issue: {issue.type}
                <br />
                Priority: {issue.severity}
                <br />
                Risk Score: {issue.riskScore !== null ? issue.riskScore : "—"}
                <br />
                Status: {issue.status}
                <br />
                Detected: {formatDate(issue.detectedAt)}
                <br />
                Authority: {issue.authority}
              </Popup>
            </Marker>
          ))}

        {showInfrastructure &&
          infrastructureMarkers.map((item) => (
            <Marker
              key={item.id}
              position={item.position}
              icon={createInfrastructureIcon()}
            >
              <Popup>
                <strong>Infrastructure Detection</strong>
                <br />
                Location ID: {item.id}
                <br />
                Expected: {item.expected || "—"}
                <br />
                Detected: {item.detected || "—"}
                <br />
                Status: {item.status || "—"}
                <br />
                Confidence:{" "}
                {item.confidence != null
                  ? `${Math.round(item.confidence * 100)}%`
                  : "—"}
              </Popup>
            </Marker>
          ))}

        {showTraffic &&
          trafficMarkers.map((item) => (
            <Circle
              key={item.id}
              center={item.position}
              radius={45}
              pathOptions={{
                color: "#2563eb",
                fillColor: "#2563eb",
                fillOpacity: 0.18,
                weight: 1,
              }}
            >
              <Popup>
                <strong>Traffic Observation</strong>
                <br />
                Frame: {item.id}
                <br />
                Vehicles: {item.vehicleCount}
                <br />
                Average Speed: {item.averageSpeed}
                <br />
                Congestion: {item.congestionLevel}
              </Popup>
            </Circle>
          ))}
      </MapContainer>
    </div>
  );
}

export default CityMap;