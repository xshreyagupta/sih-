import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

// Numeric score for the priority bar
const PRIORITY_SCORES = {
  low: 25,
  medium: 50,
  high: 75,
  critical: 100,
};

function formatEventType(eventType) {
  if (!eventType) return "Unknown";
  return String(eventType)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatLocation(latitude, longitude) {
  if (latitude == null || longitude == null) {
    return "Location unavailable";
  }
  return `${Number(latitude).toFixed(4)}, ${Number(longitude).toFixed(4)}`;
}

function titleCase(value) {
  if (!value) return "—";
  const s = String(value).toLowerCase();
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function Issues() {
  const [issues, setIssues] = useState([]);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All Types");
  const [severityFilter, setSeverityFilter] = useState("All Severities");
  const [statusFilter, setStatusFilter] = useState("All Statuses");
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadIssues() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(`${API_BASE_URL}/incidents`);

        if (!response.ok) {
          throw new Error("Failed to load issues.");
        }

        const incidents = await response.json();

        const formattedIssues = (Array.isArray(incidents) ? incidents : []).map(
          (incident) => {
            const priorityKey = String(
              incident.priority || "low"
            ).toLowerCase();

            const riskScore =
              typeof incident.risk_score === "number"
                ? incident.risk_score
                : PRIORITY_SCORES[priorityKey] ?? 0;

            return {
              id: `INC-${String(incident.id).padStart(3, "0")}`,
              backendId: incident.id,

              type: formatEventType(incident.event_type),

              location: formatLocation(
                incident.latitude,
                incident.longitude
              ),

              latitude: incident.latitude,
              longitude: incident.longitude,

              severity: priorityKey.toUpperCase(),

              priority: priorityKey.toUpperCase(),

              riskScore,

              status: incident.status || "Open",

              confidence: "—",

              sightingCount: "—",

              authority: incident.authority || "—",

              detectedAt: incident.created_at || null,
            };
          }
        );

        setIssues(formattedIssues);
      } catch (err) {
        setError(err.message || "Failed to load issues.");
      } finally {
        setLoading(false);
      }
    }

    loadIssues();
  }, []);

  const filteredIssues = issues.filter((issue) => {
    const searchValue = String(search ?? "").toLowerCase().trim();

    const matchesSearch =
      String(issue.id ?? "").toLowerCase().includes(searchValue) ||
      String(issue.type ?? "").toLowerCase().includes(searchValue) ||
      String(issue.location ?? "").toLowerCase().includes(searchValue);

    const matchesType =
      typeFilter === "All Types" || issue.type === typeFilter;

    const matchesSeverity =
      severityFilter === "All Severities" || issue.severity === severityFilter;

    const matchesStatus =
      statusFilter === "All Statuses" || issue.status === statusFilter;

    return matchesSearch && matchesType && matchesSeverity && matchesStatus;
  });

  if (loading) {
    return (
      <div className="issues-page">
        <div className="issues-table-container">
          <p>Loading issues...</p>
        </div>
      </div>
    );
  }

  if (error && issues.length === 0) {
    return (
      <div className="issues-page">
        <div className="issues-table-container">
          <p>Unable to load issues.</p>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="issues-page">
      <div className="issues-toolbar">
        <input
          type="text"
          placeholder="Search by issue, ID or location..."
          className="issues-search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />

        <select
          className="issues-filter"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
        >
          <option>All Types</option>
          {[...new Set(issues.map((issue) => issue.type))].map((type) => (
            <option key={type}>{type}</option>
          ))}
        </select>

        <select
          className="issues-filter"
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
        >
          <option>All Severities</option>
          <option>CRITICAL</option>
          <option>HIGH</option>
          <option>MEDIUM</option>
          <option>LOW</option>
        </select>

        <select
          className="issues-filter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option>All Statuses</option>
          <option>Open</option>
          <option>Verified Present</option>
          <option>Acknowledged</option>
          <option>Resolved</option>
          <option>Verified</option>
          <option>Disputed</option>
        </select>
      </div>

      {error && <div className="issues-error">{error}</div>}

      <div className="issues-table-container">
        <table className="issues-table">
          <thead>
            <tr>
              <th>Issue</th>
              <th>Location</th>
              <th>Severity</th>
              <th>Priority</th>
              <th>Status</th>
            </tr>
          </thead>

          <tbody>
            {filteredIssues.length > 0 ? (
              filteredIssues.map((issue) => (
                <tr
                  key={issue.backendId}
                  className="issue-row"
                  onClick={() => setSelectedIssue(issue)}
                >
                  <td>
                    <div className="issue-name">{issue.type}</div>
                    <div className="issue-id">{issue.id}</div>
                  </td>

                  <td>{issue.location}</td>

                  <td>
                    <span
                      className={`severity-badge ${String(
                        issue.severity ?? ""
                      ).toLowerCase()}`}
                    >
                      {issue.severity}
                    </span>
                  </td>

                  <td>
                    <div className="priority-cell">
                      <span className="priority-score">
                        {issue.priority}
                      </span>

                      <div className="priority-bar">
                        <div
                          className="priority-bar-fill"
                          style={{
                            width: `${Math.min(
                              issue.riskScore ?? 0,
                              100
                            )}%`,
                          }}
                        />
                      </div>
                    </div>
                  </td>

                  <td>
                    <span
                      className={`status-badge ${String(issue.status ?? "")
                        .toLowerCase()
                        .replaceAll(" ", "-")}`}
                    >
                      {issue.status}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5" className="no-issues">
                  <strong>No issues found</strong>
                  <span>Try changing your search or filter selection.</span>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {selectedIssue && (
        <div
          className="issue-modal-overlay"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) setSelectedIssue(null);
          }}
        >
          <div
            className="issue-details-panel"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="issue-details-header">
              <div>
                <span className="issue-details-id">{selectedIssue.id}</span>
              </div>
              <button
                className="issue-close-button"
                onClick={() => setSelectedIssue(null)}
                aria-label="Close issue details"
              >
                ×
              </button>
            </div>

            <div className="issue-details-content">
              <div className="issue-detail-item">
                <span>Type</span>
                <strong>{selectedIssue.type}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Location</span>
                <strong>{selectedIssue.location}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Severity</span>
                <strong>
                  <span
                    className={`severity-badge ${String(
                      selectedIssue.severity ?? ""
                    ).toLowerCase()}`}
                  >
                    {selectedIssue.severity}
                  </span>
                </strong>
              </div>

              <div className="issue-detail-item">
                <span>Priority</span>
                <strong>{selectedIssue.priority}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Status</span>
                <strong>{selectedIssue.status}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Detection Confidence</span>
                <strong>{selectedIssue.confidence}</strong>
              </div>

              <div className="issue-detail-item">
                <span>No. of Sightings</span>
                <strong>{selectedIssue.sightingCount}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Responsible Authority</span>
                <strong>{selectedIssue.authority}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Risk Score</span>
                <strong>
                  {typeof selectedIssue.riskScore === "number"
                    ? `${selectedIssue.riskScore}/100`
                    : "—"}
                </strong>
              </div>
            </div>

            <div className="priority-explanation">
              <div className="priority-explanation-header">
                <div>
                  <span className="priority-explanation-label">
                    Priority Assessment
                  </span>
                  <strong
                    className={`priority-explanation-level ${String(
                      selectedIssue.priority ?? ""
                    ).toLowerCase()}`}
                  >
                    {selectedIssue.priority}
                  </strong>
                </div>

                <div className="priority-explanation-score">
                  {typeof selectedIssue.riskScore === "number"
                    ? Math.round(selectedIssue.riskScore)
                    : "—"}
                  <span>/100</span>
                </div>
              </div>

              <p>
                Priority and risk information are provided by the backend
                intelligence service.
              </p>

              <div className="priority-factors">
                <span>Severity</span>
                <span>Risk score</span>
                <span>Responsible authority</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Issues;
