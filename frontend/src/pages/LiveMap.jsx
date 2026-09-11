import CityMap from "../components/CityMap";

function LiveMap() {
  return (
    <div className="live-map-page">
      <div className="live-map-layout">
        <div className="live-map-main">
          <CityMap />
        </div>

        <aside className="map-info-panel">
          <div className="map-info-section">
            <h3>Map Legend</h3>
            <p>Understanding the live sensing data.</p>
          </div>

          <div className="map-legend">
            <div className="legend-item legend-section-label">
              <div>
                <strong>Detected Issues</strong>
                <span>Marker color indicates priority</span>
              </div>
            </div>

            <div className="legend-severity-list">
              <div className="legend-severity-item">
                <span className="legend-dot severity-critical"></span>
                <span>Critical</span>
              </div>

              <div className="legend-severity-item">
                <span className="legend-dot severity-high"></span>
                <span>High</span>
              </div>

              <div className="legend-severity-item">
                <span className="legend-dot severity-medium"></span>
                <span>Medium</span>
              </div>

              <div className="legend-severity-item">
                <span className="legend-dot severity-low"></span>
                <span>Low</span>
              </div>
            </div>

            <div className="legend-item">
              <span className="legend-heat"></span>

              <div>
                <strong>Detection Density</strong>
                <span>Areas with detected events</span>
              </div>
            </div>

            <div className="legend-item">
              <span className="legend-infrastructure-marker"></span>

              <div>
                <strong>Infrastructure Detection</strong>
                <span>Infrastructure-related observations</span>
              </div>
            </div>

            <div className="legend-item">
              <span className="legend-traffic-marker"></span>

              <div>
                <strong>Traffic Observation</strong>
                <span>Recorded traffic observations</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default LiveMap;