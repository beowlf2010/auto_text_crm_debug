// frontend/components/LeadRow.jsx   ← replace the old file
import React from "react";
import dayjs from "dayjs";
import axios from "axios";

const API =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost:8000"
    : "http://web:8000");

const statusClasses = {
  "Not Started": "bg-gray-200 text-gray-700",
  Generated: "bg-yellow-200 text-yellow-800",
  Sent: "bg-green-200 text-green-800",
};

export default function LeadRow({ lead, refreshLeads, onRegenerate }) {
  /* ------------ pause / resume helpers */
  const toggleAI = async () => {
    try {
      if (lead.ai_active) {
        await axios.post(`${API}/api/pause-ai/${lead.id}/`);
      } else {
        await axios.post(`${API}/api/start-ai/${lead.id}/`);
      }
      /* pull fresh data so the UI reflects the new flag */
      refreshLeads();          // <-- pass this down from parent list
    } catch (err) {
      console.error(err);
      alert("Could not update AI status (see console)");
    }
  };

  const eta =
    lead.next_ai_send_at &&
    `${dayjs(lead.next_ai_send_at).format("MMM D, h:mm A")} (${dayjs(
      lead.next_ai_send_at
    ).fromNow()})`;

  return (
    <tr className="hover:bg-gray-50 transition">
      <td className="px-3 py-2">
        <div className="font-medium">{lead.name}</div>
        <div className="text-sm text-gray-500">{lead.cellphone}</div>
      </td>

      <td className="px-3 py-2 text-sm">
        {lead.vehicle_interest || "—"}
      </td>

      <td className="px-3 py-2 text-sm">
        <span
          className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
            statusClasses[lead.message_status] ||
            "bg-gray-100 text-gray-700"
          }`}
        >
          {lead.message_status || "—"}
        </span>
      </td>

      <td className="px-3 py-2 text-xs text-gray-500">
        {eta || "Not scheduled"}
      </td>

      {/* ---- action buttons ---- */}
      <td className="px-3 py-2 space-x-2 text-right">
        <button
          onClick={toggleAI}
          className={`text-xs rounded px-2 py-1 ${
            lead.ai_active
              ? "bg-red-200 hover:bg-red-300"
              : "bg-blue-200 hover:bg-blue-300"
          }`}
        >
          {lead.ai_active ? "⏸ Pause AI" : "▶ Resume AI"}
        </button>

        <button
          onClick={() => onRegenerate?.(lead.id)}
          className="text-xs rounded bg-yellow-200 px-2 py-1 hover:bg-yellow-300"
        >
          🔁 Regenerate
        </button>
      </td>
    </tr>
  );
}
