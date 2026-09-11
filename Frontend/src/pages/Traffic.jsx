import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const trafficTrendData = [
  { time: "8 AM", vehicles: 72 },
  { time: "9 AM", vehicles: 105 },
  { time: "10 AM", vehicles: 128 },
  { time: "11 AM", vehicles: 116 },
  { time: "12 PM", vehicles: 94 },
  { time: "1 PM", vehicles: 82 },
];

function Traffic() {
  return (
    <div className="traffic-page">
      <div className="traffic-overview">
        <div className="traffic-card">
          <span className="traffic-card-label">Vehicles Detected</span>
          <strong>420</strong>
          <span>Across active sensing routes</span>
        </div>

        <div className="traffic-card">
          <span className="traffic-card-label">Congested Zones</span>
          <strong>03</strong>
          <span>Require monitoring</span>
        </div>

        <div className="traffic-card">
          <span className="traffic-card-label">Average Speed</span>
          <strong>29 km/h</strong>
          <span>Across monitored roads</span>
        </div>

        <div className="traffic-card">
          <span className="traffic-card-label">Active Buses</span>
          <strong>18</strong>
          <span>Currently sensing traffic</span>
        </div>
      </div>

      <div className="traffic-chart-card">
        <div className="section-header">
          <div>
            <h3>Traffic Trend</h3>
            <p>Vehicle density over the last 6 hours.</p>
          </div>
        </div>

        <div className="traffic-chart">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={trafficTrendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="time" />
              <YAxis />
              <Tooltip />

              <Line
                type="monotone"
                dataKey="vehicles"
                stroke="#2563eb"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="traffic-weather-card">
        <div className="section-header">
          <div>
            <h3>Weather Impact on Traffic</h3>
            <p>
              Estimated effect of weather conditions on traffic movement.
            </p>
          </div>
        </div>

        <div className="weather-overview">
          <div className="weather-current">
            <span className="weather-label">Current Conditions</span>
            <strong>Moderate Rain</strong>
            <span>Reduced visibility and slower traffic movement</span>
          </div>

          <div className="weather-impact">
            <span className="weather-label">Traffic Impact</span>
            <strong>High</strong>
            <span>Compared with normal conditions</span>
          </div>

          <div className="weather-metric">
            <span className="weather-label">Average Speed</span>
            <strong>21 km/h</strong>
            <span>During current conditions</span>
          </div>

          <div className="weather-metric">
            <span className="weather-label">Congestion Increase</span>
            <strong>+32%</strong>
            <span>Compared with normal traffic</span>
          </div>
        </div>

        <div className="weather-table-container">
          <table className="weather-table">
            <thead>
              <tr>
                <th>Weather Condition</th>
                <th>Traffic Impact</th>
                <th>Expected Effect</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td>
                  <strong>Clear</strong>
                </td>
                <td>
                  <span className="weather-impact-badge low">Low</span>
                </td>
                <td>Normal traffic flow</td>
              </tr>

              <tr>
                <td>
                  <strong>Cloudy</strong>
                </td>
                <td>
                  <span className="weather-impact-badge low">Low</span>
                </td>
                <td>Minimal impact on movement</td>
              </tr>

              <tr>
                <td>
                  <strong>Rain</strong>
                </td>
                <td>
                  <span className="weather-impact-badge high">High</span>
                </td>
                <td>Reduced speed and increased congestion</td>
              </tr>

              <tr>
                <td>
                  <strong>Heavy Rain</strong>
                </td>
                <td>
                  <span className="weather-impact-badge severe">Severe</span>
                </td>
                <td>Significant delays and possible waterlogging</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Traffic;