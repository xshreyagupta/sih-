import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function formatAlertId(id) {
  return `ALT-${String(id).padStart(4, "0")}`;
}

function formatAlertDate(date) {
  if (!date) return "Date unavailable";
  const parsedDate = new Date(date);
  if (Number.isNaN(parsedDate.getTime())) return "Date unavailable";

  return parsedDate.toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

function isReAlert(alert) {
  return (
    typeof alert.message === "string" &&
    alert.message.includes("SLA BREACHED")
  );
}

function formatAlert(alert) {
  return {
    id: formatAlertId(alert.id),
    backendId: alert.id,
    incidentId: alert.incident_id,
    date: formatAlertDate(alert.created_at),
    priority: alert.priority || "—",
    message: alert.message || "Urban incident alert",
    authority: alert.authority || "Authority unavailable",
    acknowledged: Boolean(alert.acknowledged),
    isReAlert: isReAlert(alert),
  };
}

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [acknowledgingId, setAcknowledgingId] = useState(null);
  const [reAlertingId, setReAlertingId] = useState(null);
  const [actionError, setActionError] = useState("");
  const [actionSuccess, setActionSuccess] = useState("");

  async function loadAlerts() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/alerts`);

      if (!response.ok) {
        throw new Error("Failed to load alerts.");
      }

      const data = await response.json();

      const formattedAlerts = Array.isArray(data)
        ? data.map(formatAlert).filter((alert) => !alert.acknowledged)
        : [];

      setAlerts(formattedAlerts);
    } catch (err) {
      setError(err.message || "Failed to load alerts.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAlerts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!actionSuccess) return;
    const timer = setTimeout(() => setActionSuccess(""), 4000);
    return () => clearTimeout(timer);
  }, [actionSuccess]);

  async function handleAcknowledge(backendId) {
    try {
      setAcknowledgingId(backendId);
      setActionError("");
      setActionSuccess("");

      const response = await fetch(
        `${API_BASE_URL}/alerts/${backendId}/acknowledge`,
        { method: "PATCH" }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail ||
            `Failed to acknowledge alert (status ${response.status}).`
        );
      }

      setAlerts((prev) =>
        prev.filter((alert) => alert.backendId !== backendId)
      );

      setActionSuccess(`Alert ${formatAlertId(backendId)} acknowledged.`);
    } catch (err) {
      console.error("Acknowledge error:", err);
      setActionError(err.message || "Failed to acknowledge alert.");
    } finally {
      setAcknowledgingId(null);
    }
  }

  async function handleReAlert(backendId, incidentId) {
    try {
      setReAlertingId(backendId);
      setActionError("");
      setActionSuccess("");

      if (incidentId === null || incidentId === undefined) {
        throw new Error(
          "This alert has no linked incident, so it cannot be re-alerted."
        );
      }

      const response = await fetch(
        `${API_BASE_URL}/incidents/${incidentId}/re-alert`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.detail ||
            `Failed to create re-alert SLA (status ${response.status}).`
        );
      }

      const created = Boolean(data.re_alert_created);

      if (created) {
        setActionSuccess(`Re-alert SLA created for incident ${incidentId}.`);
        await loadAlerts();
      } else {
        setActionSuccess(
          data.message || "This incident has already been re-alerted."
        );
      }
    } catch (err) {
      console.error("Re-alert error:", err);
      setActionError(err.message || "Failed to create re-alert SLA.");
    } finally {
      setReAlertingId(null);
    }
  }

  if (loading) {
    return (
      <div className="alerts-page">
        <div className="alert-card">
          <p>Loading alerts...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alerts-page">
        <div className="alert-card">
          <p>Unable to load alerts.</p>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="alerts-page">
      {actionError ? (
        <div className="alert-card" style={{ marginBottom: "16px" }}>
          <p>Unable to update alert.</p>
          <span>{actionError}</span>
        </div>
      ) : null}

      {actionSuccess ? (
        <div
          className="alert-card"
          style={{ marginBottom: "16px", borderLeft: "4px solid #22c55e" }}
        >
          <p>{actionSuccess}</p>
        </div>
      ) : null}

      {alerts.length > 0 ? (
        <div className="alerts-grid">
          {alerts.map((alert) => (
            <div
              className={`alert-card${alert.isReAlert ? " re-alert-card" : ""}`}
              key={alert.backendId}
            >
              <div className="alert-card-header">
                <span className="alert-id">{alert.id}</span>

                <span
                  style={{ display: "flex", alignItems: "center", gap: "8px" }}
                >
                  <span
                    className={`alert-priority ${String(
                      alert.priority
                    ).toLowerCase()}`}
                  >
                    {alert.priority}
                  </span>

                  {alert.isReAlert ? (
                    <span className="alert-badge re-alert">Re-Alert</span>
                  ) : null}
                </span>
              </div>

              <span className="alert-date">{alert.date}</span>

              <h3 className="alert-title">{alert.message}</h3>

              <p className="alert-description">
                Incident ID: <strong>{alert.incidentId ?? "—"}</strong>
              </p>

              <div className="alert-audience">
                <span>Responsible Authority: </span>
                <strong>{alert.authority}</strong>
              </div>

              <div className="alert-action-info">
                <span>Alert Status</span>

                <button
                  type="button"
                  className="acknowledge-button"
                  disabled={acknowledgingId === alert.backendId}
                  onClick={() => handleAcknowledge(alert.backendId)}
                >
                  {acknowledgingId === alert.backendId
                    ? "Acknowledging..."
                    : "Acknowledge"}
                </button>

                <button
                  type="button"
                  className="re-alert-button"
                  disabled={
                    reAlertingId === alert.backendId ||
                    alert.incidentId === null ||
                    alert.incidentId === undefined ||
                    alert.isReAlert
                  }
                  onClick={() =>
                    handleReAlert(alert.backendId, alert.incidentId)
                  }
                  title={
                    alert.isReAlert
                      ? "This is already a re-alert"
                      : "Create a new re-alert SLA"
                  }
                >
                  {reAlertingId === alert.backendId
                    ? "Re-alerting..."
                    : "Re-Alert"}
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="alert-card">
          <p>No alerts currently available.</p>
        </div>
      )}
    </div>
  );
}

export default Alerts;