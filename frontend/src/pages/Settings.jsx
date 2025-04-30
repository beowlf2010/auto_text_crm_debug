// C:\Projects\auto_text_crm_dockerized_clean\frontend\pages\Settings.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const API_BASE =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "http://web:8000");

const Settings = () => {
  const [startHour, setStartHour] = useState("08:00");
  const [endHour, setEndHour] = useState("19:00");
  const [autoFollowUps, setAutoFollowUps] = useState(true);
  const [saving, setSaving] = useState(false);

  // ───────────────────── fetch on mount
  useEffect(() => {
    (async () => {
      try {
        const { data } = await axios.get(`${API_BASE}/api/settings/`);
        setStartHour(data.start_hour || "08:00");
        setEndHour(data.end_hour || "19:00");
        setAutoFollowUps(data.auto_followups);
      } catch (err) {
        console.error("Fetch settings failed:", err);
        toast.error("⚠️ Could not load settings.");
      }
    })();
  }, []);

  // ───────────────────── save handler
  const saveSettings = async () => {
    // simple validation
    if (startHour >= endHour) {
      toast.warn("Start hour must be earlier than end hour.");
      return;
    }
    setSaving(true);
    try {
      await axios.put(`${API_BASE}/api/settings/`, {
        start_hour: startHour,
        end_hour: endHour,
        auto_followups: autoFollowUps,
      });
      toast.success("✅ Settings saved!");
    } catch (err) {
      console.error(err);
      toast.error("❌ Failed to update settings.");
    } finally {
      setSaving(false);
    }
  };

  // ───────────────────── render
  return (
    <div className="p-6 space-y-6">
      <ToastContainer position="bottom-right" autoClose={3000} />

      <h1 className="text-2xl font-bold">⚙️ Settings</h1>

      <div className="space-y-4 max-w-lg">
        <div>
          <label className="block font-medium mb-1">Texting Start Hour</label>
          <input
            type="time"
            value={startHour}
            onChange={(e) => setStartHour(e.target.value)}
            className="border rounded p-2 w-full"
          />
        </div>

        <div>
          <label className="block font-medium mb-1">Texting End Hour</label>
          <input
            type="time"
            value={endHour}
            onChange={(e) => setEndHour(e.target.value)}
            className="border rounded p-2 w-full"
          />
        </div>

        <div className="flex items-center gap-2">
          <input
            id="autoFollowUps"
            type="checkbox"
            checked={autoFollowUps}
            onChange={() => setAutoFollowUps(!autoFollowUps)}
          />
          <label htmlFor="autoFollowUps" className="font-medium">
            Enable AI Auto Follow‑ups
          </label>
        </div>

        <button
          onClick={saveSettings}
          disabled={saving}
          className={`px-4 py-2 rounded text-white ${
            saving ? "bg-gray-400" : "bg-blue-600 hover:bg-blue-700"
          }`}
        >
          {saving ? "Saving…" : "Save Settings"}
        </button>
      </div>
    </div>
  );
};

export default Settings;
