import { useState } from "react";

function Settings() {
  const [autoRefresh, setAutoRefresh] = useState("30");
  const [defaultMapView, setDefaultMapView] = useState("city");
  const [dashboardDensity, setDashboardDensity] = useState("comfortable");

  const [criticalAlerts, setCriticalAlerts] = useState(true);
  const [highPriorityAlerts, setHighPriorityAlerts] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(false);

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);

    setTimeout(() => {
      setSaved(false);
    }, 2500);
  };

  return (
    <div className="settings-page">
      <div className="settings-grid">
        <div className="settings-card">
          <div className="section-header">
            <h3>Dashboard Preferences</h3>
            <p>Manage how the command center displays information.</p>
          </div>

          <div className="setting-row">
            <div>
              <strong>Auto Refresh</strong>
              <span>Automatically refresh dashboard data.</span>
            </div>

            <select
              value={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.value)}
            >
              <option value="15">15 seconds</option>
              <option value="30">30 seconds</option>
              <option value="60">1 minute</option>
              <option value="300">5 minutes</option>
            </select>
          </div>

          <div className="setting-row">
            <div>
              <strong>Default Map View</strong>
              <span>
                Choose the initial map view when opening Live Map.
              </span>
            </div>

            <select
              value={defaultMapView}
              onChange={(e) => setDefaultMapView(e.target.value)}
            >
              <option value="city">City Overview</option>
              <option value="traffic">Traffic Zones</option>
              <option value="issues">Issue Hotspots</option>
            </select>
          </div>

          <div className="setting-row">
            <div>
              <strong>Dashboard Density</strong>
              <span>
                Choose how much information is displayed at once.
              </span>
            </div>

            <select
              value={dashboardDensity}
              onChange={(e) => setDashboardDensity(e.target.value)}
            >
              <option value="compact">Compact</option>
              <option value="comfortable">Comfortable</option>
            </select>
          </div>
        </div>

        <div className="settings-card">
          <div className="section-header">
            <h3>Alert Preferences</h3>
            <p>Choose which alerts should be displayed.</p>
          </div>

          <div className="setting-row">
            <div>
              <strong>Critical Alerts</strong>
              <span>Show alerts requiring immediate attention.</span>
            </div>

            <label className="toggle">
              <input
                type="checkbox"
                checked={criticalAlerts}
                onChange={(e) => setCriticalAlerts(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="setting-row">
            <div>
              <strong>High Priority Alerts</strong>
              <span>Show important urban condition alerts.</span>
            </div>

            <label className="toggle">
              <input
                type="checkbox"
                checked={highPriorityAlerts}
                onChange={(e) => setHighPriorityAlerts(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
          </div>

          <div className="setting-row">
            <div>
              <strong>Email Notifications</strong>
              <span>Receive important alerts through email.</span>
            </div>

            <label className="toggle">
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
              />
              <span className="toggle-slider"></span>
            </label>
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

      <div className="settings-actions">
        <button className="save-settings-button" onClick={handleSave}>
          Save Preferences
        </button>

        {saved && (
          <span className="settings-saved-message">
            ✓ Preferences saved
          </span>
        )}
      </div>
    </div>
  );
}

export default Settings;
