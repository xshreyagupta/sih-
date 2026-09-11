import { useEffect, useMemo, useState } from "react";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

function Traffic() {
  const [trafficData, setTrafficData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadTraffic() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(`${API_BASE_URL}/traffic`);

        if (!response.ok) {
          throw new Error("Failed to load traffic data.");
        }

        const data = await response.json();
        setTrafficData(data);
      } catch (err) {
        setError(err.message || "Failed to load traffic data.");
      } finally {
        setLoading(false);
      }
    }

    loadTraffic();
  }, []);

  const trafficStats = useMemo(() => {
    if (trafficData.length === 0) {
      return {
        vehiclesDetected: 0,
        congestedZones: 0,
        averageSpeed: 0,
      };
    }

    const vehiclesDetected = trafficData.reduce(
      (total, item) => total + Number(item.vehicle_count || 0),
      0
    );

    const congestedZones = trafficData.filter((item) => {
      const level = String(item.congestion_level || "").toLowerCase();

      return (
        level.includes("high") ||
        level.includes("heavy") ||
        level.includes("severe") ||
        level.includes("critical")
      );
    }).length;

    const validSpeedRecords = trafficData.filter(
      (item) => Number(item.avg_speed) > 0
    );

    const averageSpeed =
      validSpeedRecords.length > 0
        ? validSpeedRecords.reduce(
            (total, item) => total + Number(item.avg_speed),
            0
          ) / validSpeedRecords.length
        : 0;

    return {
      vehiclesDetected,
      congestedZones,
      averageSpeed,
    };
  }, [trafficData]);

  const trendData = useMemo(() => {
    if (trafficData.length === 0) return [];

    const chunkSize = Math.max(1, Math.ceil(trafficData.length / 6));
    const chunks = [];

    for (let i = 0; i < trafficData.length; i += chunkSize) {
      const chunk = trafficData.slice(i, i + chunkSize);

      const vehicles = chunk.reduce(
        (total, item) => total + Number(item.vehicle_count || 0),
        0
      );

      const average =
        chunk.length > 0 ? vehicles / chunk.length : 0;

      chunks.push({
        label: `Period ${chunks.length + 1}`,
        vehicles: Math.round(average),
      });
    }

    return chunks.slice(0, 6);
  }, [trafficData]);

  if (loading) {
    return (
      <div className="traffic-page">
        <div className="traffic-chart-card">
          <div className="traffic-empty-state">
            <strong>Loading traffic data...</strong>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="traffic-page">
        <div className="traffic-chart-card">
          <div className="traffic-empty-state">
            <strong>Unable to load traffic data</strong>
            <span>{error}</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="traffic-page">
      <div className="traffic-overview">
        <div className="traffic-card">
          <span className="traffic-card-label">
            Vehicles Detected
          </span>
          <strong>
            {trafficStats.vehiclesDetected.toLocaleString("en-IN")}
          </strong>
          <span>Recorded traffic observations</span>
        </div>

        <div className="traffic-card">
          <span className="traffic-card-label">
            Congested Zones
          </span>
          <strong>{trafficStats.congestedZones}</strong>
          <span>High congestion observations</span>
        </div>

        <div className="traffic-card">
          <span className="traffic-card-label">
            Average Speed
          </span>
          <strong>
            {trafficStats.averageSpeed > 0
              ? trafficStats.averageSpeed.toFixed(1)
              : "—"}
          </strong>
          <span>
            {trafficStats.averageSpeed > 0
              ? "Recorded average speed"
              : "Speed data unavailable"}
          </span>
        </div>
      </div>

      <div className="traffic-chart-card">
        <div className="section-header">
          <div>
            <h3>Traffic Trend</h3>
            <p>
              Vehicle observations across the available sensing data.
            </p>
          </div>
        </div>

        <div className="traffic-chart">
          {trendData.length > 0 ? (
            <div className="traffic-trend-list">
              {trendData.map((item) => (
                <div
                  className="traffic-trend-item"
                  key={item.label}
                >
                  <span>{item.label}</span>

                  <div className="traffic-trend-bar">
                    <div
                      className="traffic-trend-bar-fill"
                      style={{
                        width: `${
                          (item.vehicles /
                            Math.max(
                              ...trendData.map(
                                (trend) => trend.vehicles
                              ),
                              1
                            )) *
                          100
                        }%`,
                      }}
                    />
                  </div>

                  <strong>{item.vehicles}</strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="traffic-empty-state">
              <strong>No traffic data available</strong>
              <span>
                Traffic observations will appear when sensing data
                is available.
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Traffic;
