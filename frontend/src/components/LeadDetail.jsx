// ✅ LOCKED: 2025-04-23 – Fully synced with /api/leads/<id>/ endpoint

import React, { useEffect, useState } from "react";
import axios from "axios";
import MessageThread from "./MessageThread";

const API_BASE =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost"
    : "http://web");

export default function LeadDetail({ leadId }) {
  const [lead, setLead] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!leadId) return;

    setLoading(true);
    setError(null);

    axios
      .get(`${API_BASE}/api/leads/${leadId}/`)
      .then((res) => setLead(res.data))
      .catch((err) => {
        console.error(err);
        setError("Could not load lead.");
      })
      .finally(() => setLoading(false));
  }, [leadId]);

  if (!leadId)
    return <p className="text-gray-500 italic">Select a lead to view details.</p>;
  if (loading)
    return <p className="text-gray-500 italic">Loading lead…</p>;
  if (error)
    return <p className="text-red-600 italic">{error}</p>;
  if (!lead)
    return <p className="text-gray-500 italic">Lead not found.</p>;

  const {
    name,
    cellphone,
    message_status,
    salesperson,
    source,
    vehicle_interest,
  } = lead;

  return (
    <div className="rounded bg-white p-4 shadow">
      <h2 className="mb-3 text-xl font-semibold">📋 Lead Detail</h2>

      <ul className="space-y-1 text-sm">
        <li>
          <strong>Name:</strong> {name}
        </li>
        <li>
          <strong>Cellphone:</strong> {cellphone}
        </li>
        <li>
          <strong>Status:</strong> {message_status || "—"}
        </li>
        <li>
          <strong>Salesperson:</strong> {salesperson || "—"}
        </li>
        <li>
          <strong>Source:</strong> {source || "—"}
        </li>
        <li>
          <strong>Vehicle Interest:</strong> {vehicle_interest || "—"}
        </li>
      </ul>

      {/* full thread */}
      <div className="mt-4 border-t pt-4">
        <MessageThread leadId={lead.id} />
      </div>
    </div>
  );
}
