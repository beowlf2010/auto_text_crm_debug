// ✅ LOCKED: 2025-04-23 – API_BASE fixed for dev mode at port 80

import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import KPIStats from "../components/KPIStats";

dayjs.extend(relativeTime);

const API_BASE =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost"
    : "http://web");

const POLL_MS = 15000;
const card =
  "flex items-center justify-between p-4 bg-white rounded-xl shadow sm:p-6";

export default function Dashboard() {
  const [unreadMessages, setUnreadMessages] = useState([]);
  const [kpi, setKpi] = useState({
    new_leads: 0,
    unread: 0,
    pending_auto: 0,
    sent_today: 0,
    last_send: null,
  });

  const navigate = useNavigate();

  const fetchUnread = async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/api/unread-messages/`);
      setUnreadMessages(data.messages || []);
    } catch (err) {
      console.error("Unread fetch failed:", err);
    }
  };

  const fetchKpi = async () => {
    try {
      const { data } = await axios.get(`${API_BASE}/api/kpi-summary/`);
      setKpi(data);
    } catch (err) {
      console.error("KPI fetch failed:", err);
    }
  };

  const downloadHotCsv = async () => {
    try {
      const res = await axios.get(`${API_BASE}/api/leads/export-hot/`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download = "hot_leads.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error("CSV download failed:", err);
    }
  };

  useEffect(() => {
    fetchUnread();
    fetchKpi();
    const id = setInterval(() => {
      fetchUnread();
      fetchKpi();
    }, POLL_MS);
    return () => clearInterval(id);
  }, []);

  const fmtLastSend = kpi.last_send
    ? `${dayjs(kpi.last_send).format("MMM D, h:mm A")} (${dayjs(
        kpi.last_send
      ).fromNow()})`
    : "—";

  const UnreadCard = ({ msg }) => {
    const goToThread = () => {
      if (!msg.lead_id) return;
      navigate(`/smart-inbox?lead=${msg.lead_id}`);
    };

    return (
      <li
        onClick={goToThread}
        className="cursor-pointer bg-blue-50 border border-blue-200 hover:bg-blue-100 p-3 rounded"
      >
        <div className="font-medium">
          {msg.lead_name} ({msg.from_number})
        </div>
        <div className="text-sm text-gray-800 line-clamp-2">{msg.message}</div>
        <div className="text-xs text-gray-500 italic">
          {dayjs(msg.timestamp).format("MMM D, h:mm A")}
        </div>
      </li>
    );
  };

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-3xl font-bold">🏠 Dashboard</h1>
      <p className="text-sm text-gray-500 mb-4">Live overview · updates every 15 s</p>

      {/* KPI cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className={card}>
          <span className="text-gray-600">New Leads (24 h)</span>
          <span className="text-2xl font-semibold">{kpi.new_leads}</span>
        </div>
        <div className={card}>
          <span className="text-gray-600">Unread Replies</span>
          <span className="text-2xl font-semibold">{kpi.unread}</span>
        </div>
        <div className={card}>
          <span className="text-gray-600">Pending Auto‑Sends</span>
          <span className="text-2xl font-semibold">{kpi.pending_auto}</span>
        </div>
        <div className={card}>
          <span className="text-gray-600">Sent Today</span>
          <span className="text-2xl font-semibold">{kpi.sent_today}</span>
        </div>
      </div>

      {/* quick links */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Link to="/smart-inbox" className={card}>
          <span className="font-semibold">📥 Open Smart Inbox</span>
          <span className="text-sm text-gray-500">Last AI send: {fmtLastSend}</span>
        </Link>
        <Link to="/upload" className={card}>
          <span className="font-semibold">📤 Upload New Leads</span>
          <span className="text-sm text-gray-500">CSV drag‑and‑drop</span>
        </Link>
        <button onClick={downloadHotCsv} className={card}>
          <span className="font-semibold">⬇️ Download Hot Leads CSV</span>
          <span className="text-sm text-gray-500">score ≥ 80</span>
        </button>
      </div>

      {/* unread messages */}
      <div className="bg-white p-4 rounded-xl shadow">
        <h2 className="text-lg font-semibold mb-2">📥 Incoming Messages</h2>
        {unreadMessages.length === 0 ? (
          <p className="text-gray-500 italic">No recent messages.</p>
        ) : (
          <ul className="space-y-3">
            {unreadMessages.map((msg) => (
              <UnreadCard key={`${msg.lead_id}-${msg.timestamp}`} msg={msg} />
            ))}
          </ul>
        )}
      </div>

      <KPIStats />
    </div>
  );
}
