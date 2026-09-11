import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function formatStatus(s) {
  if (!s) return "—";
  return String(s)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function formatType(t) {
  if (!t) return "—";
  return String(t)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

function statusClass(s) {
  if (!s) return "";
  return String(s).toLowerCase().replaceAll("_", "-");
}

function Verification() {
  const [records, setRecords] = useState([]);
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState(null);
  const [actionError, setActionError] = useState("");
  const [actionSuccess, setActionSuccess] = useState("");
  const [acting, setActing] = useState(false);

  async function loadData() {
    try {
      setLoading(true);
      setError("");
      const [r1, r2] = await Promise.all([
        fetch(`${API_BASE_URL}/verification/records`),
        fetch(`${API_BASE_URL}/verification`),
      ]);
      if (!r1.ok || !r2.ok) throw new Error("Failed to load verification data.");
      const recordsData = await r1.json();
      const queueData = await r2.json();
      setRecords(Array.isArray(recordsData) ? recordsData : []);
      setQueue(Array.isArray(queueData) ? queueData : []);
    } catch (err) {
      setError(err.message || "Failed to load verification data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  useEffect(() => {
    if (!actionSuccess) return;
    const t = setTimeout(() => setActionSuccess(""), 4000);
    return () => clearTimeout(t);
  }, [actionSuccess]);

  function findQueueItem(rec) {
    if (!rec) return null;
    return (
      queue.find(
        (q) =>
          (rec.event_id != null && q.incident_id === rec.event_id) ||
          (rec.location_id && q.incident_id === rec.location_id)
      ) || null
    );
  }

  async function handleVerify(id) {
    try {
      setActing(true);
      setActionError("");
      setActionSuccess("");
      const res = await fetch(`${API_BASE_URL}/verification/${id}/verify`, {
        method: "POST",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `Failed (${res.status})`);
      setActionSuccess(data.message || "Verified.");
      await loadData();
      setSelected(null);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActing(false);
    }
  }

  async function handleDispute(id) {
    try {
      setActing(true);
      setActionError("");
      setActionSuccess("");
      const res = await fetch(`${API_BASE_URL}/verification/${id}/dispute`, {
        method: "POST",
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(data.detail || `Failed (${res.status})`);
      setActionSuccess(data.message || "Disputed.");
      await loadData();
      setSelected(null);
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActing(false);
    }
  }

  const infraRecords = records.filter((r) => r.event_type === "infrastructure");
  const defectRecords = records.filter((r) => r.event_type === "defect");

  const pendingCount = queue.filter(
    (q) => String(q.status || "").toLowerCase() === "pending verification"
  ).length;

  const verifiedCount = records.filter((r) =>
    ["verified_present", "verified_closed"].includes(
      String(r.verification_result || "").toLowerCase()
    )
  ).length;

  const disputedCount = records.filter(
    (r) =>
      String(r.verification_result || "").toLowerCase() === "verified_wrong"
  ).length;

  if (loading) {
    return (
      <div className="verification-page">
        <div className="verification-table-card">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="verification-page">
        <div className="verification-table-card">
          <p>Unable to load verification data.</p>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="verification-page">
      <div className="verification-overview">
        <div className="verification-card">
          <span className="verification-card-label">Pending</span>
          <strong>{String(pendingCount).padStart(2, "0")}</strong>
          <span>Awaiting bus re-check</span>
        </div>
        <div className="verification-card">
          <span className="verification-card-label">Verified</span>
          <strong>{String(verifiedCount).padStart(2, "0")}</strong>
          <span>Successfully confirmed</span>
        </div>
        <div className="verification-card">
          <span className="verification-card-label">Disputed</span>
          <strong>{String(disputedCount).padStart(2, "0")}</strong>
          <span>Issue still detected</span>
        </div>
        <div className="verification-card">
          <span className="verification-card-label">Total Records</span>
          <strong>{String(records.length).padStart(2, "0")}</strong>
          <span>All verification entries</span>
        </div>
      </div>

      {actionError && (
        <div
          className="verification-info-box"
          style={{ borderColor: "#fecaca", background: "#fef2f2" }}
        >
          <p style={{ color: "#b91c1c", fontWeight: 600 }}>{actionError}</p>
        </div>
      )}

      {actionSuccess && (
        <div
          className="verification-info-box"
          style={{ borderColor: "#bbf7d0", background: "#f0fdf4" }}
        >
          <p style={{ color: "#166534", fontWeight: 600 }}>{actionSuccess}</p>
        </div>
      )}

      <div className="verification-table-card" style={{ marginBottom: "20px" }}>
        <div className="section-header">
          <h3>Infrastructure Verification</h3>
          <p>Expected vs. detected infrastructure.</p>
        </div>

        <div className="verification-table-container">
          <table className="verification-table">
            <thead>
              <tr>
                <th>Location ID</th>
                <th>Expected</th>
                <th>Detected</th>
                <th>Confidence</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {infraRecords.length > 0 ? (
                infraRecords.map((rec) => (
                  <tr key={rec.id}>
                    <td className="verification-id">
                      {rec.location_id || "—"}
                    </td>
                    <td>
                      <strong>{formatType(rec.expected_infrastructure)}</strong>
                    </td>
                    <td>
                      <strong>{formatType(rec.detected_infrastructure)}</strong>
                    </td>
                    <td>
                      {typeof rec.confidence === "number"
                        ? `${Math.round(rec.confidence * 100)}%`
                        : "—"}
                    </td>
                    <td>
                      <span
                        className={`verification-status ${statusClass(
                          rec.verification_result
                        )}`}
                      >
                        {formatStatus(rec.verification_result)}
                      </span>
                    </td>
                    <td>
                      <button
                        className="verification-action"
                        onClick={() => setSelected(rec)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="6"
                    style={{ textAlign: "center", padding: "24px" }}
                  >
                    No infrastructure records.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="verification-table-card">
        <div className="section-header">
          <h3>Defect Verification</h3>
          <p>Road damage records.</p>
        </div>

        <div className="verification-table-container">
          <table className="verification-table">
            <thead>
              <tr>
                <th>Event ID</th>
                <th>Class</th>
                <th>Location</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>

            <tbody>
              {defectRecords.length > 0 ? (
                defectRecords.map((rec) => (
                  <tr key={rec.id}>
                    <td className="verification-id">
                      {rec.event_id != null
                        ? `INC-${String(rec.event_id).padStart(3, "0")}`
                        : "—"}
                    </td>
                    <td>{formatType(rec.class_name)}</td>
                    <td>
                      {rec.latitude != null && rec.longitude != null
                        ? `${Number(rec.latitude).toFixed(4)}, ${Number(
                            rec.longitude
                          ).toFixed(4)}`
                        : "—"}
                    </td>
                    <td>
                      <span
                        className={`verification-status ${statusClass(
                          rec.verification_result
                        )}`}
                      >
                        {formatStatus(rec.verification_result)}
                      </span>
                    </td>
                    <td>
                      <button
                        className="verification-action"
                        onClick={() => setSelected(rec)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="5"
                    style={{ textAlign: "center", padding: "24px" }}
                  >
                    No defect records.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {selected && (
        <div
          className="issue-modal-overlay"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) setSelected(null);
          }}
        >
          <div
            className="issue-details-panel"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="issue-details-header">
              <div>
                <span className="issue-details-id">
                  {selected.event_type === "infrastructure"
                    ? selected.location_id || "—"
                    : selected.event_id != null
                    ? `INC-${String(selected.event_id).padStart(3, "0")}`
                    : "—"}
                </span>
              </div>
              <button
                className="issue-close-button"
                onClick={() => setSelected(null)}
              >
                ×
              </button>
            </div>

            <div className="issue-details-content">
              <div className="issue-detail-item">
                <span>Type</span>
                <strong>
                  {selected.event_type === "infrastructure"
                    ? formatType(selected.expected_infrastructure)
                    : formatType(selected.class_name)}
                </strong>
              </div>

              {selected.event_type === "infrastructure" && (
                <>
                  <div className="issue-detail-item">
                    <span>Expected</span>
                    <strong>{formatType(selected.expected_infrastructure)}</strong>
                  </div>
                  <div className="issue-detail-item">
                    <span>Detected</span>
                    <strong>{formatType(selected.detected_infrastructure)}</strong>
                  </div>
                  <div className="issue-detail-item">
                    <span>Confidence</span>
                    <strong>
                      {typeof selected.confidence === "number"
                        ? `${Math.round(selected.confidence * 100)}%`
                        : "—"}
                    </strong>
                  </div>
                </>
              )}

              <div className="issue-detail-item">
                <span>Location</span>
                <strong>
                  {selected.latitude != null && selected.longitude != null
                    ? `${Number(selected.latitude).toFixed(4)}, ${Number(
                        selected.longitude
                      ).toFixed(4)}`
                    : "—"}
                </strong>
              </div>

              <div className="issue-detail-item">
                <span>Status</span>
                <strong>{formatStatus(selected.verification_result)}</strong>
              </div>
            </div>

            {(() => {
              const q = findQueueItem(selected);
              if (!q) return null;
              const st = String(q.status || "").toLowerCase();
              if (st === "verified" || st === "disputed") return null;
              return (
                <div
                  style={{ display: "flex", gap: "10px", marginTop: "10px" }}
                >
                  <button
                    className="issue-acknowledge-button"
                    disabled={acting}
                    onClick={() => handleVerify(q.id)}
                    style={{ flex: 1 }}
                  >
                    {acting ? "Working..." : "Confirm Verification"}
                  </button>
                  <button
                    className="issue-reescalate-button"
                    disabled={acting}
                    onClick={() => handleDispute(q.id)}
                    style={{ flex: 1 }}
                  >
                    {acting ? "Working..." : "Dispute"}
                  </button>
                </div>
              );
            })()}
          </div>
        </div>
      )}
    </div>
  );
}

export default Verification;