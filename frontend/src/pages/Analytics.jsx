import { useEffect, useMemo, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function formatEventType(eventType) {
  if (!eventType) return "Unknown";
  return String(eventType)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function Analytics() {
  const [timeRange, setTimeRange] = useState("Last 7 Days");
  const [incidents, setIncidents] = useState([]);
  const [priorityResults, setPriorityResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAnalyticsData() {
      try {
        setLoading(true);
        setError("");

        const [incidentsResponse, priorityResponse] = await Promise.all([
          fetch(`${API_BASE_URL}/incidents`),
          fetch(`${API_BASE_URL}/priority`),
        ]);

        if (!incidentsResponse.ok || !priorityResponse.ok) {
          throw new Error("Failed to load analytics data.");
        }

        const incidentsData = await incidentsResponse.json();
        const priorityData = await priorityResponse.json();

        setIncidents(Array.isArray(incidentsData) ? incidentsData : []);
        setPriorityResults(Array.isArray(priorityData) ? priorityData : []);
      } catch (err) {
        setError(err.message || "Failed to load analytics data.");
      } finally {
        setLoading(false);
      }
    }

    loadAnalyticsData();
  }, []);

  const categoryData = useMemo(() => {
    const counts = {};

    incidents.forEach((incident) => {
      const category = formatEventType(incident.event_type);
      counts[category] = (counts[category] || 0) + 1;
    });

    return Object.entries(counts)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count);
  }, [incidents]);

  const detectionTrend = useMemo(() => {
    if (incidents.length === 0) return [];

    const sortedIncidents = [...incidents].sort(
      (a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0)
    );

    const buckets = 6;
    const chunkSize = Math.max(
      1,
      Math.ceil(sortedIncidents.length / buckets)
    );

    const result = [];

    for (let i = 0; i < sortedIncidents.length; i += chunkSize) {
      const chunk = sortedIncidents.slice(i, i + chunkSize);
      result.push({
        label: `Period ${result.length + 1}`,
        count: chunk.length,
      });
    }

    return result.slice(0, buckets);
  }, [incidents, timeRange]);

  const hotspots = useMemo(() => {
    const locationCounts = {};

    incidents.forEach((incident) => {
      if (incident.latitude == null || incident.longitude == null) return;

      const key = `${Number(incident.latitude).toFixed(4)},${Number(
        incident.longitude
      ).toFixed(4)}`;

      if (!locationCounts[key]) {
        locationCounts[key] = {
          latitude: Number(incident.latitude),
          longitude: Number(incident.longitude),
          count: 0,
        };
      }
      locationCounts[key].count += 1;
    });

    return Object.values(locationCounts)
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  }, [incidents]);

  const prioritySummary = useMemo(() => {
    const counts = { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 };

    priorityResults.forEach((item) => {
      const priority = item.priority?.toUpperCase();
      if (counts[priority] !== undefined) counts[priority] += 1;
    });

    return counts;
  }, [priorityResults]);

  if (loading) {
    return (
      <div className="analytics-page">
        <div className="analytics-chart-card">
          <div className="analytics-empty-state">
            <strong>Loading analytics...</strong>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-page">
        <div className="analytics-chart-card">
          <div className="analytics-empty-state">
            <strong>Unable to load analytics</strong>
            <span>{error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="analytics-page">
      <div className="analytics-chart-grid">
        <div className="analytics-chart-card">
          <div className="section-header analytics-trend-header">
            <div>
              <h3>Detection Trend</h3>
              <p>Incidents detected across the selected time period.</p>
            </div>

            <select
              className="analytics-time-filter"
              value={timeRange}
              onChange={(event) => setTimeRange(event.target.value)}
            >
              <option>Last 24 Hours</option>
              <option>Last 7 Days</option>
              <option>Last 30 Days</option>
            </select>
          </div>

          <div className="analytics-chart">
            {detectionTrend.length > 0 ? (
              <div className="analytics-trend-list">
                {detectionTrend.map((item) => (
                  <div className="analytics-trend-item" key={item.label}>
                    <span>{item.label}</span>

                    <div className="analytics-trend-bar">
                      <div
                        className="analytics-trend-bar-fill"
                        style={{
                          width: `${
                            (item.count /
                              Math.max(
                                ...detectionTrend.map((t) => t.count),
                                1
                              )) *
                            100
                          }%`,
                        }}
                      />
                    </div>

                    <strong>{item.count}</strong>
                  </div>
                ))}
              </div>
            ) : (
              <div className="analytics-empty-state">
                <strong>No detection data available</strong>
                <span>
                  Detection trends will appear when incidents are available.
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="analytics-chart-card">
          <div className="section-header">
            <div>
              <h3>Issues by Category</h3>
              <p>Distribution of detected urban issues.</p>
            </div>
          </div>

          <div className="analytics-chart">
            {categoryData.length > 0 ? (
              <div className="analytics-category-list">
                {categoryData.map((item) => (
                  <div className="analytics-category-item" key={item.category}>
                    <div className="analytics-category-info">
                      <span>{item.category}</span>
                      <strong>{item.count}</strong>
                    </div>

                    <div className="analytics-category-bar">
                      <div
                        className="analytics-category-bar-fill"
                        style={{
                          width: `${
                            (item.count /
                              Math.max(
                                ...categoryData.map((c) => c.count),
                                1
                              )) *
                            100
                          }%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="analytics-empty-state">
                <strong>No category data available</strong>
                <span>
                  Issue distribution will appear when incident data is
                  available.
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="analytics-chart-card hotspot-card">
        <div className="section-header">
          <div>
            <h3>Top Risk Hotspots</h3>
            <p>
              Locations with the highest concentration of detected incidents.
            </p>
          </div>
        </div>

        <div className="hotspot-table-container">
          {hotspots.length > 0 ? (
            <table className="hotspot-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Location</th>
                  <th>Detections</th>
                </tr>
              </thead>

              <tbody>
                {hotspots.map((hotspot, index) => (
                  <tr key={`${hotspot.latitude}-${hotspot.longitude}`}>
                    <td>#{index + 1}</td>
                    <td>
                      {hotspot.latitude.toFixed(4)},{" "}
                      {hotspot.longitude.toFixed(4)}
                    </td>
                    <td>
                      <strong>{hotspot.count}</strong>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="analytics-empty-state analytics-table-empty-state">
              <strong>No hotspot data available</strong>
              <span>
                Risk hotspots will appear when location data is available.
              </span>
            </div>
          )}
        </div>
      </div>

      <div className="analytics-chart-card priority-summary-card">
        <div className="section-header">
          <div>
            <h3>Priority Distribution</h3>
            <p>Distribution of backend-generated priority results.</p>
          </div>
        </div>

        <div className="priority-summary-grid">
          <div className="priority-summary-item critical">
            <span>Critical</span>
            <strong>{prioritySummary.CRITICAL}</strong>
          </div>

          <div className="priority-summary-item high">
            <span>High</span>
            <strong>{prioritySummary.HIGH}</strong>
          </div>

          <div className="priority-summary-item medium">
            <span>Medium</span>
            <strong>{prioritySummary.MEDIUM}</strong>
          </div>

          <div className="priority-summary-item low">
            <span>Low</span>
            <strong>{prioritySummary.LOW}</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;