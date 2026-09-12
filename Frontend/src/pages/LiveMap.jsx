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
            {/* Detected Issues */}

            <div className="legend-item legend-section-label">
              <div>
                <strong>Detected Issues</strong>
                <span>Marker color indicates severity</span>
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

            {/* Active Buses */}

            <div className="legend-item">
              <span className="legend-bus-marker">B</span>

              <div>
                <strong>Active Sensing Buses</strong>
                <span>Currently collecting data</span>
              </div>
            </div>

            {/* Routes */}

            <div className="legend-item">
              <span className="legend-line"></span>

              <div>
                <strong>Route Traces</strong>
                <span>Sampled bus routes</span>
              </div>
            </div>

            {/* Detection Density */}

            <div className="legend-item">
              <span className="legend-heat"></span>

              <div>
                <strong>Detection Density</strong>
                <span>Higher intensity = more detections</span>
              </div>
            </div>

            {/* Road Health */}

            <div className="legend-item legend-road-health">
              <div className="road-health-legend-content">
                <strong>Road Health</strong>
                <span>Color indicates road condition</span>
              </div>
            </div>

            <div className="road-health-list">
              <div className="road-health-item">
                <span className="road-health-line road-good"></span>
                <span>Good</span>
              </div>

              <div className="road-health-item">
                <span className="road-health-line road-moderate"></span>
                <span>Moderate</span>
              </div>

              <div className="road-health-item">
                <span className="road-health-line road-poor"></span>
                <span>Poor</span>
              </div>

              <div className="road-health-item">
                <span className="road-health-line road-critical"></span>
                <span>Critical</span>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

export default LiveMap;