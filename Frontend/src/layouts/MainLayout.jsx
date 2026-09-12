import { Outlet, NavLink, useLocation } from "react-router-dom";

import {
  LayoutDashboard,
  Map,
  AlertTriangle,
  Bell,
  Car,
  BarChart3,
  ClipboardCheck,
  Settings,
} from "lucide-react";

function MainLayout() {
  const location = useLocation();

  const navigation = [
    { name: "Dashboard", path: "/", icon: LayoutDashboard },
    { name: "Live Map", path: "/live-map", icon: Map },
    { name: "Issues", path: "/issues", icon: AlertTriangle },
    { name: "Alerts", path: "/alerts", icon: Bell },
    { name: "Traffic", path: "/traffic", icon: Car },
    { name: "Analytics", path: "/analytics", icon: BarChart3 },
    { name: "Verification", path: "/verification", icon: ClipboardCheck },
    { name: "Settings", path: "/settings", icon: Settings },
  ];

  const pageInfo = {
    "/": {
      title: "Operations Dashboard",
      description: "Monitor urban conditions across the city.",
    },
    "/live-map": {
      title: "Live GIS Map",
      description: "Real-time view of detected urban conditions.",
    },
    "/issues": {
      title: "Detected Issues",
      description: "Monitor and manage detected urban issues.",
    },
    "/alerts": {
      title: "Operational Alerts",
      description: "Review and manage important urban condition alerts.",
    },
    "/traffic": {
      title: "Traffic Conditions",
      description: "Monitor traffic density and congestion across the city.",
    },
    "/analytics": {
      title: "Analytics",
      description: "Analyze trends and patterns from urban sensing data.",
    },
    "/verification": {
      title: "Human Verification",
      description: "Review and verify resolved urban issues.",
    },
    "/settings": {
      title: "Settings",
      description: "Manage dashboard preferences and system settings.",
    },
  };

  const currentPage = pageInfo[location.pathname] || pageInfo["/"];

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-mark">ND</div>

          <div>
            <h2>NagarDrishti</h2>
            <span>Command Center</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.name}
                to={item.path}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                <Icon size={19} />
                <span>{item.name}</span>
              </NavLink>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <span className="status-dot"></span>
            <span>System Online</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="topbar-page-info">
            <h1>{currentPage.title}</h1>
            <p>{currentPage.description}</p>
          </div>

          <div className="topbar-right">
            <span className="live-indicator">
              <span className="live-dot"></span>
              Live
            </span>

            <div className="user-profile">
              <div className="avatar">A</div>

              <div>
                <strong>Authority</strong>
                <span>Control Room</span>
              </div>
            </div>
          </div>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  );
}

export default MainLayout;