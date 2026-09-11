import { useEffect, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

// Map backend priority (LOW/MEDIUM/HIGH/CRITICAL) to a 0-100 score
const PRIORITY_SCORES = {
  low: 25,
  medium: 50,
  high: 75,
  critical: 100,
};

// Title-case for display
function titleCase(value) {
  if (!value) return "—";
  const s = String(value).toLowerCase();
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Build a display-friendly "location" from lat/lng
function formatLocation(lat, lng) {
  if (lat === null || lat === undefined || lng === null || lng === undefined) {
    return "Location unavailable";
  }
  return `${Number(lat).toFixed(4)}, ${Number(lng).toFixed(4)}`;
}

// Map a backend incident to the shape the table expects
function formatIncident(incident) {
  const priorityKey = String(incident.priority || "low").toLowerCase();

  const score =
    typeof incident.risk_score === "number" && incident.risk_score > 0
      ? Math.round(incident.risk_score)
      : PRIORITY_SCORES[priorityKey] ?? 25;

  return {
    id: `INC-${String(incident.id).padStart(3, "0")}`,
    backendId: incident.id,
    type: titleCase(incident.event_type || "Incident"),
    location: formatLocation(incident.latitude, incident.longitude),
    severity: titleCase(priorityKey), // Critical / High / Medium / Low
    priority: score,
    priorityLevel: `${titleCase(priorityKey)} Priority`,
    status: incident.status || "Open",
    authority: incident.authority || "Authority unavailable",
    busRoute: "—",
    confidence: "—",
    sightingCount: 1,
    jurisdiction: "—",
  };
}

function Issues() {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("All Types");
  const [severityFilter, setSeverityFilter] = useState("All Severities");
  const [statusFilter, setStatusFilter] = useState("All Statuses");
  const [selectedIssue, setSelectedIssue] = useState(null);

  async function loadIssues() {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_BASE_URL}/incidents`);

      if (!response.ok) {
        throw new Error("Failed to load issues.");
      }

      const data = await response.json();
      const formatted = Array.isArray(data) ? data.map(formatIncident) : [];

      setIssues(formatted);
    } catch (err) {
      setError(err.message || "Failed to load issues.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadIssues();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Derive unique types for the filter dropdown
  const typeOptions = [
    "All Types",
    ...Array.from(new Set(issues.map((i) => i.type))).sort(),
  ];

  const filteredIssues = issues.filter((issue) => {
    const searchValue = search.toLowerCase();

    const matchesSearch =
      issue.id.toLowerCase().includes(searchValue) ||
      issue.type.toLowerCase().includes(searchValue) ||
      issue.location.toLowerCase().includes(searchValue);

    const matchesType =
      typeFilter === "All Types" || issue.type === typeFilter;

    const matchesSeverity =
      severityFilter === "All Severities" || issue.severity === severityFilter;

    const matchesStatus =
      statusFilter === "All Statuses" || issue.status === statusFilter;

    return matchesSearch && matchesType && matchesSeverity && matchesStatus;
  });

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
          {typeOptions.map((type) => (
            <option key={type}>{type}</option>
          ))}
        </select>

        <select
          className="issues-filter"
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
        >
          <option>All Severities</option>
          <option>Critical</option>
          <option>High</option>
          <option>Medium</option>
          <option>Low</option>
        </select>

        <select
          className="issues-filter"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option>All Statuses</option>
          <option>Open</option>
          <option>Acknowledged</option>
          <option>In Progress</option>
          <option>Resolved</option>
          <option>Pending Verification</option>
          <option>Verified</option>
          <option>Disputed</option>
          <option>Re-escalated</option>
        </select>
      </div>

      {loading ? (
        <div className="issues-table-container">
          <div className="no-issues">
            <strong>Loading issues...</strong>
          </div>
        </div>
      ) : error ? (
        <div className="issues-table-container">
          <div className="no-issues">
            <strong>Unable to load issues</strong>
            <span>{error}</span>
          </div>
        </div>
      ) : (
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
                        className={`severity-badge ${issue.severity.toLowerCase()}`}
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
                            style={{ width: `${issue.priority}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>

                    <td>
                      <span
                        className={`status-badge ${issue.status
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
                    <span>
                      Try changing your search or filter selection.
                    </span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {selectedIssue && (
        <div
          className="issue-modal-overlay"
          onMouseDown={(e) => {
            if (e.target === e.currentTarget) {
              setSelectedIssue(null);
            }
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
                <span>Bus / Route</span>
                <strong>{selectedIssue.busRoute}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Location</span>
                <strong>{selectedIssue.location}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Severity</span>
                <strong>
                  <span
                    className={`severity-badge ${selectedIssue.severity.toLowerCase()}`}
                  >
                    {selectedIssue.severity}
                  </span>
                </strong>
              </div>

              <div className="issue-detail-item">
                <span>Detection Confidence</span>
                <strong>{selectedIssue.confidence}</strong>
              </div>

              <div className="issue-detail-item">
                <span>Status</span>
                <strong>{selectedIssue.status}</strong>
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
                <span>Jurisdiction</span>
                <strong>{selectedIssue.jurisdiction}</strong>
              </div>
            </div>

            <div className="priority-explanation">
              <div className="priority-explanation-header">
                <div>
                  <span className="priority-explanation-label">
                    Priority Assessment
                  </span>

                  <strong
                    className={`priority-explanation-level ${selectedIssue.severity.toLowerCase()}`}
                  >
                    {selectedIssue.priorityLevel}
                  </strong>
                </div>

                <div className="priority-explanation-score">
                  {selectedIssue.priority}
                  <span>/100</span>
                </div>
              </div>

              <p>
                Priority score and priority level are provided by the
                system's intelligence and backend services.
              </p>

              <div className="priority-factors">
                <span>Severity</span>
                <span>Sightings</span>
                <span>Detection confidence</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Issues;