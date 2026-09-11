import { useState } from "react";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const issueCategoryData = [
  { category: "Potholes", count: 42 },
  { category: "Waterlogging", count: 28 },
  { category: "Traffic", count: 36 },
  { category: "Infrastructure", count: 19 },
];

const historicalTrendData = {
  "Last 24 Hours": [
    { day: "2 PM", incidents: 8 },
    { day: "4 PM", incidents: 12 },
    { day: "6 PM", incidents: 16 },
    { day: "8 PM", incidents: 13 },
    { day: "10 PM", incidents: 9 },
    { day: "12 AM", incidents: 6 },
    { day: "2 AM", incidents: 4 },
    { day: "4 AM", incidents: 5 },
    { day: "6 AM", incidents: 8 },
    { day: "8 AM", incidents: 14 },
    { day: "10 AM", incidents: 18 },
    { day: "12 PM", incidents: 15 },
  ],

  "Last 7 Days": [
    { day: "Mon", incidents: 18 },
    { day: "Tue", incidents: 24 },
    { day: "Wed", incidents: 21 },
    { day: "Thu", incidents: 32 },
    { day: "Fri", incidents: 28 },
    { day: "Sat", incidents: 36 },
    { day: "Sun", incidents: 30 },
  ],

  "Last 30 Days": [
    { day: "Week 1", incidents: 112 },
    { day: "Week 2", incidents: 128 },
    { day: "Week 3", incidents: 146 },
    { day: "Week 4", incidents: 139 },
  ],
};

const hotspotData = [
  {
    location: "Karol Bagh",
    issues: 18,
    trend: "Increasing",
    risk: "High",
  },
  {
    location: "Ring Road",
    issues: 14,
    trend: "Increasing",
    risk: "High",
  },
  {
    location: "ITO",
    issues: 11,
    trend: "Stable",
    risk: "Medium",
  },
  {
    location: "Connaught Place",
    issues: 8,
    trend: "Improving",
    risk: "Low",
  },
];

const futureRiskData = [
  {
    location: "Karol Bagh",
    riskScore: 82,
    riskLevel: "High",
    trend: "Increasing",
    issue: "Pothole",
  },
  {
    location: "ITO Junction",
    riskScore: 76,
    riskLevel: "High",
    trend: "Increasing",
    issue: "Traffic Congestion",
  },
  {
    location: "Ring Road",
    riskScore: 61,
    riskLevel: "Moderate",
    trend: "Stable",
    issue: "Waterlogging",
  },
  {
    location: "Connaught Place",
    riskScore: 38,
    riskLevel: "Low",
    trend: "Decreasing",
    issue: "Road Damage",
  },
];

function Analytics() {
  const [timeRange, setTimeRange] = useState("Last 7 Days");

  return (
    <div className="analytics-page">
      <div className="analytics-chart-grid">
        <div className="analytics-chart-card">
          <div className="section-header analytics-trend-header">
            <div>
              <h3>Detection Trend</h3>
              <p>
                Incidents detected across the selected time period.
              </p>
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
            <ResponsiveContainer width="100%" height={280}>
              <LineChart
                data={historicalTrendData[timeRange]}
                margin={{
                  top: 10,
                  right: 10,
                  left: 0,
                  bottom: 0,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="day" />
                <YAxis />
                <Tooltip />

                <Line
                  type="monotone"
                  dataKey="incidents"
                  stroke="#2563eb"
                  strokeWidth={2.5}
                  dot={{ r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
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
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={issueCategoryData}
                margin={{
                  top: 10,
                  right: 10,
                  left: 0,
                  bottom: 0,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />

                <Bar
                  dataKey="count"
                  fill="#2563eb"
                  radius={[5, 5, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="analytics-chart-card hotspot-card">
        <div className="section-header">
          <div>
            <h3>Top Risk Hotspots</h3>
            <p>
              Locations with the highest concentration of detected issues.
            </p>
          </div>
        </div>

        <div className="hotspot-table-container">
          <table className="hotspot-table">
            <thead>
              <tr>
                <th>Location</th>
                <th>Issues</th>
                <th>Trend</th>
                <th>Risk</th>
              </tr>
            </thead>

            <tbody>
              {hotspotData.map((item) => (
                <tr key={item.location}>
                  <td>
                    <strong>{item.location}</strong>
                  </td>

                  <td>{item.issues}</td>

                  <td>
                    <span
                      className={`hotspot-trend ${item.trend
                        .toLowerCase()
                        .replace(" ", "-")}`}
                    >
                      {item.trend === "Increasing" && "↑"}
                      {item.trend === "Stable" && "→"}
                      {item.trend === "Improving" && "↓"}{" "}
                      {item.trend}
                    </span>
                  </td>

                  <td>
                    <span
                      className={`hotspot-risk ${item.risk.toLowerCase()}`}
                    >
                      {item.risk}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="analytics-chart-card future-risk-card">
        <div className="section-header">
          <div>
            <h3>Future Risk Prediction</h3>
            <p>
              Predicted urban risks based on recent detection trends.
            </p>
          </div>
        </div>

        <div className="future-risk-list">
          {futureRiskData.map((item) => (
            <div
              className="future-risk-item"
              key={item.location}
            >
              <div className="future-risk-location">
                <strong>{item.location}</strong>
                <span>
                  {item.issue} · Trend: {item.trend}
                </span>
              </div>

              <div className="future-risk-score">
                <div className="future-risk-score-value">
                  <strong>{item.riskScore}</strong>
                  <span>/100</span>
                </div>

                <div
                  className={`future-risk-badge ${item.riskLevel.toLowerCase()}`}
                >
                  {item.riskLevel} Risk
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Analytics;