// frontend/src/App.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";

import Layout            from "./components/Layout";       // ⬅️ sidebar wrapper
import Dashboard         from "./pages/Dashboard";
import Leads             from "./pages/Leads";
import Upload            from "./pages/Upload";
import SmartInbox        from "./pages/SmartInbox";
import ScheduledMessages from "./pages/ScheduledMessages"; // 👈 NEW
import Settings          from "./pages/Settings";

export default function App() {
  return (
    <Layout>
      <Routes>
        {/* --- main nav -------------------------------------------------- */}
        <Route path="/"            element={<Navigate to="/dashboard" />} />
        <Route path="/dashboard"   element={<Dashboard />} />

        <Route path="/leads"       element={<Leads />} />
        <Route path="/upload"      element={<Upload />} />

        {/* inbox / messaging */}
        <Route path="/smart-inbox" element={<SmartInbox />} />
        <Route path="/inbox"       element={<SmartInbox />} />

        {/* AI message queue (formerly AutoTexting) */}
        <Route path="/auto-texting" element={<ScheduledMessages />} />

        {/* settings placeholder */}
        <Route path="/settings"    element={<Settings />} />

        {/* catch‑all ----------------------------------------------------- */}
        <Route path="*" element={<p className="p-8">404 — page not found</p>} />
      </Routes>
    </Layout>
  );
}
