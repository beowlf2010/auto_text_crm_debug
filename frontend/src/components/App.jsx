// src/App.jsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Dashboard    from "./pages/Dashboard";
import UploadPage   from "./pages/UploadPage";
import LeadsPage    from "./pages/LeadsPage";
import AutoTexting  from "./pages/AutoTextingTab";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  return (
    <Router>
      <div className="flex">
        <Sidebar />
        <div className="ml-64 w-full p-6">
          <Routes>
            <Route path="/"            element={<Dashboard   />} />
            <Route path="/upload"      element={<UploadPage  />} />
            <Route path="/leads"       element={<LeadsPage   />} />
            <Route path="/auto-texting" element={<AutoTexting />} />
            <Route path="/settings"    element={<SettingsPage/>} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}
