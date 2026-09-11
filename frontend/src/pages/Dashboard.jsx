import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { requestIssuesRefresh } from "../issuesRefresh";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function Dashboard() {
  const [events, setEvents] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [priorityResults, setPriorityResults] = useState([]);
  const [verificationRecords, setVerificationRecords] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [uploading, setUploading] = useState(false);
  const [uploadPhase, setUploadPhase] = useState(null);
  const [detectionData, setDetectionData] = useState(null);
  const [uploadError, setUploadError] = useState("");

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [
        eventsResponse,
        priorityResponse,
        verificationResponse,
        incidentsResponse,
      ] = await Promise.all([
        fetch(`${API_BASE_URL}/events`),
        fetch(`${API_BASE_URL}/priority`),
        fetch(`${API_BASE_URL}/verification/records`),
        fetch(`${API_BASE_URL}/incidents`),
      ]);

      if (
        !eventsResponse.ok ||
        !priorityResponse.ok ||
        !verificationResponse.ok ||
        !incidentsResponse.ok
      ) {
        throw new Error("Failed to load dashboard data.");
      }

      const eventsData = await eventsResponse.json();
      const priorityData = await priorityResponse.json();
      const verificationData = await verificationResponse.json();
      const incidentsData = await incidentsResponse.json();

      setEvents(eventsData);
      setPriorityResults(priorityData);
      setVerificationRecords(verificationData);
      setIncidents(
        Array.isArray(incidentsData)
          ? incidentsData.filter(
              (i) => String(i.status || "").toLowerCase() !== "resolved"
            )
          : []
      );
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function refreshDashboard() {
    try {
      const [
        eventsResponse,
        priorityResponse,
        verificationResponse,
        incidentsResponse,
      ] = await Promise.all([
        fetch(`${API_BASE_URL}/events`),
        fetch(`${API_BASE_URL}/priority`),
        fetch(`${API_BASE_URL}/verification/records`),
        fetch(`${API_BASE_URL}/incidents`),
      ]);

      if (eventsResponse.ok) setEvents(await eventsResponse.json());
      if (priorityResponse.ok) setPriorityResults(await priorityResponse.json());
      if (verificationResponse.ok)
        setVerificationRecords(await verificationResponse.json());
      if (incidentsResponse.ok) {
        const incidentsData = await incidentsResponse.json();
        setIncidents(
          Array.isArray(incidentsData)
            ? incidentsData.filter(
                (i) => String(i.status || "").toLowerCase() !== "resolved"
              )
            : []
        );
      }
    } catch (err) {
      console.error("Dashboard refresh failed:", err);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const handleVideoUpload = async (event, phase) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setUploadPhase(phase);
    setUploadError("");
    setDetectionData(null);

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("phase", phase);

      const response = await fetch(`${API_BASE_URL}/detection/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Video processing failed.");
      }

      setDetectionData(data);
      requestIssuesRefresh();
      await refreshDashboard();
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
      setUploadPhase(null);
      event.target.value = "";
    }
  };

  const getDetectionVideoUrl = (data) => {
    if (!data?.detection_video) return "";
    const fileName = data.detection_video.split("/").pop();
    return `${API_BASE_URL}/detection/video/${fileName}`;
  };

  const getDetectionSummary = (data) => {
    if (!data?.detections) return [];

    const counts = {};

    data.detections.forEach((detection) => {
      const key = `${detection.source}|${detection.type}`;

      if (!counts[key]) {
        counts[key] = {
          source: detection.source,
          type: detection.type,
          count: 0,
        };
      }

      counts[key].count += 1;
    });

    return Object.values(counts);
  };

  if (loading) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-card">
          <p>Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-card">
          <p>Unable to load dashboard data.</p>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  const criticalCount = incidents.filter(
    (item) => item.priority?.toUpperCase() === "CRITICAL"
  ).length;

  const getVerificationStatus = (item) =>
    String(item.verification_result || "")
      .trim()
      .replaceAll("_", " ")
      .replace(/\s+/g, " ")
      .toLowerCase();

  const pendingVerificationCount = verificationRecords.filter(
    (item) => getVerificationStatus(item) === "verified present"
  ).length;

  const verifiedCount = verificationRecords.filter(
    (item) => getVerificationStatus(item) === "verified closed"
  ).length;

  const disputedCount = verificationRecords.filter(
    (item) => getVerificationStatus(item) === "verified wrong"
  ).length;

  const highPriorityResults = priorityResults
    .filter((item) => {
      const priority = item.priority?.toUpperCase();
      return priority === "CRITICAL" || priority === "HIGH";
    })
    .sort((a, b) => (b.risk_score || 0) - (a.risk_score || 0))
    .slice(0, 3);

  const stats = [
    {
      label: "Active Incidents",
      value: String(incidents.length).padStart(2, "0"),
      description: "Detected incidents from fleet",
    },
    {
      label: "Critical Issues",
      value: String(criticalCount).padStart(2, "0"),
      description: "Require immediate attention",
    },
    {
      label: "Events Detected",
      value: String(incidents.length).padStart(2, "0"),
      description: "Incidents recorded by the system",
    },
    {
      label: "Pending Verifications",
      value: String(pendingVerificationCount).padStart(2, "0"),
      description: "Issues awaiting verification",
    },
  ];

  const incidentStatus = [
    { label: "Detected", count: incidents.length, className: "open" },
    { label: "Critical", count: criticalCount, className: "acknowledged" },
    {
      label: "Pending Verification",
      count: pendingVerificationCount,
      className: "pending",
    },
    { label: "Verified", count: verifiedCount, className: "resolved" },
    { label: "Disputed", count: disputedCount, className: "in-progress" },
  ];

  const detectionSummary = getDetectionSummary(detectionData);

  return (
    <div className="dashboard-page">
      <div className="stats-grid">
        {stats.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <span className="stat-label">{stat.label}</span>
            <strong className="stat-value">{stat.value}</strong>
            <span className="stat-description">{stat.description}</span>
          </div>
        ))}
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card detection-card">
          <div className="dashboard-card-header">
            <div>
              <h3>Incident Status Overview</h3>
              <p>Current distribution of detected incidents.</p>
            </div>
            <Link to="/issues" className="dashboard-link">
              View Issues
            </Link>
          </div>

          <div className="incident-status-overview">
            {incidentStatus.map((status) => (
              <div className="incident-status-item" key={status.label}>
                <div className="incident-status-info">
                  <span
                    className={`incident-status-indicator ${status.className}`}
                  />
                  <span>{status.label}</span>
                </div>
                <strong>{status.count}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="dashboard-card-header">
            <div>
              <h3>Priority Alerts</h3>
              <p>High-risk results requiring attention.</p>
            </div>
            <Link to="/issues" className="dashboard-link">
              View Issues
            </Link>
          </div>

          <div className="priority-alerts">
            {highPriorityResults.length > 0 ? (
              highPriorityResults.map((item) => (
                <div className="priority-alert" key={item.incident_id}>
                  <div className="priority-alert-content">
                    <span className="priority-alert-id">
                      INC-{String(item.incident_id).padStart(3, "0")}
                    </span>
                    <strong>{item.priority} priority event</strong>
                  </div>
                  <span
                    className={`priority-badge ${item.priority?.toLowerCase()}`}
                  >
                    {item.priority}
                  </span>
                </div>
              ))
            ) : (
              <p>No high-priority events currently available.</p>
            )}
          </div>
        </div>
      </div>

      <div className="dashboard-card" style={{ marginTop: "24px" }}>
        <div className="dashboard-card-header">
          <div>
            <h3>Video Processing</h3>
            <p>
              Upload an input video to detect issues, then upload an output
              video to mark the repaired ones as resolved.
            </p>
          </div>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: "16px",
          }}
        >
          <div
            style={{
              padding: "20px",
              border: "2px dashed #93c5fd",
              background: "#eff6ff",
              borderRadius: "10px",
              textAlign: "center",
            }}
          >
            <h4 style={{ marginTop: 0, marginBottom: "8px", color: "#1d4ed8" }}>
              Input Video
            </h4>
            <p style={{ fontSize: "13px", color: "#3b82f6", marginTop: 0 }}>
              Detects issues and creates incidents.
            </p>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => handleVideoUpload(e, "input")}
              disabled={uploading}
            />
            {uploading && uploadPhase === "input" && (
              <p style={{ marginTop: "12px", fontWeight: "600" }}>
                Processing input video...
              </p>
            )}
          </div>

          <div
            style={{
              padding: "20px",
              border: "2px dashed #86efac",
              background: "#f0fdf4",
              borderRadius: "10px",
              textAlign: "center",
            }}
          >
            <h4 style={{ marginTop: 0, marginBottom: "8px", color: "#15803d" }}>
              Output Video
            </h4>
            <p style={{ fontSize: "13px", color: "#16a34a", marginTop: 0 }}>
              Marks missing issues as resolved.
            </p>
            <input
              type="file"
              accept="video/*"
              onChange={(e) => handleVideoUpload(e, "output")}
              disabled={uploading}
            />
            {uploading && uploadPhase === "output" && (
              <p style={{ marginTop: "12px", fontWeight: "600" }}>
                Processing output video...
              </p>
            )}
          </div>
        </div>

        {uploadError && (
          <p style={{ marginTop: "16px", color: "#dc2626", fontWeight: 600 }}>
            {uploadError}
          </p>
        )}

        {detectionData && (
          <div
            style={{
              marginTop: "20px",
              padding: "14px 16px",
              borderRadius: "8px",
              borderLeft: "4px solid #22c55e",
              background: "#f0fdf4",
            }}
          >
            {detectionData.phase === "input" ? (
              <p style={{ margin: 0, fontWeight: 600, color: "#166534" }}>
                {detectionData.incidents_created} incident
                {detectionData.incidents_created === 1 ? "" : "s"} created from{" "}
                {detectionData.detection_count} detections.
              </p>
            ) : (
              <p style={{ margin: 0, fontWeight: 600, color: "#166534" }}>
                {detectionData.incidents_resolved} incident
                {detectionData.incidents_resolved === 1 ? "" : "s"} marked as
                resolved. {detectionData.incidents_still_present?.length ?? 0}{" "}
                still present.
              </p>
            )}
          </div>
        )}

        {detectionData && (
          <div style={{ marginTop: "24px" }}>
            <div style={{ marginBottom: "20px" }}>
              <h3>Detection Results</h3>
              <p style={{ color: "#6b7280", fontSize: "13px" }}>
                {detectionData.detection_count} detections in{" "}
                {detectionData.filename} ({detectionData.phase} video).
              </p>
            </div>

            <div
              style={{
                width: "100%",
                background: "#000",
                borderRadius: "10px",
                overflow: "hidden",
                marginBottom: "24px",
              }}
            >
              <video
                controls
                style={{ width: "100%", display: "block", maxHeight: "600px" }}
                src={getDetectionVideoUrl(detectionData)}
              />
            </div>

            <h3>Detected Objects</h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
                gap: "12px",
                marginTop: "15px",
              }}
            >
              {detectionSummary.map((item, index) => (
                <div
                  key={`${item.source}-${item.type}-${index}`}
                  style={{
                    border: "1px solid #e5e7eb",
                    borderRadius: "8px",
                    padding: "15px",
                  }}
                >
                  <strong style={{ display: "block", marginBottom: "8px" }}>
                    {item.type}
                  </strong>
                  <span
                    style={{
                      display: "block",
                      fontSize: "13px",
                      color: "#6b7280",
                      marginBottom: "5px",
                    }}
                  >
                    Source: {item.source}
                  </span>
                  <span style={{ fontSize: "13px", color: "#6b7280" }}>
                    Detections: {item.count}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;