function Settings() {
  return (
    <div className="settings-page">
      <div className="settings-grid">
        <div className="settings-card">
          <div className="section-header">
            <h3>Dashboard Preferences</h3>
            <p>Command center display configuration.</p>
          </div>

          <div className="system-info-row">
            <span>Dashboard</span>
            <strong>Standard View</strong>
          </div>

          <div className="system-info-row">
            <span>Map</span>
            <strong>City Overview</strong>
          </div>

          <div className="system-info-row">
            <span>Data Display</span>
            <strong>Standard</strong>
          </div>
        </div>

        <div className="settings-card">
          <div className="section-header">
            <h3>Alert Configuration</h3>
            <p>Alert handling is managed by the command center.</p>
          </div>

          <div className="system-info-row">
            <span>Critical Alerts</span>
            <strong>Enabled</strong>
          </div>

          <div className="system-info-row">
            <span>High Priority Alerts</span>
            <strong>Enabled</strong>
          </div>

          <div className="system-info-row">
            <span>Notification Management</span>
            <strong>Authority Controlled</strong>
          </div>
        </div>

        <div className="settings-card system-info-card">
          <div className="section-header">
            <h3>System Information</h3>
            <p>Current status of the sensing platform.</p>
          </div>

          <div className="system-info-row">
            <span>System Status</span>
            <span className="system-online">
              <span className="status-dot"></span>
              Online
            </span>
          </div>

          <div className="system-info-row">
            <span>Active Buses</span>
            <strong>18</strong>
          </div>

          <div className="system-info-row">
            <span>Last Data Sync</span>
            <strong>2 minutes ago</strong>
          </div>

          <div className="system-info-row">
            <span>Platform Version</span>
            <strong>v1.0.0</strong>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Settings;