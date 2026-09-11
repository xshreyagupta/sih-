import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./layouts/MainLayout";
import Dashboard from "./pages/Dashboard";
import LiveMap from "./pages/LiveMap";
import Issues from "./pages/Issues";
import Alerts from "./pages/Alerts";
import Traffic from "./pages/Traffic";
import Analytics from "./pages/Analytics";
import Verification from "./pages/Verification";
import Settings from "./pages/Settings";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/live-map" element={<LiveMap />} />
          <Route path="/issues" element={<Issues />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/traffic" element={<Traffic />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/verification" element={<Verification />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;