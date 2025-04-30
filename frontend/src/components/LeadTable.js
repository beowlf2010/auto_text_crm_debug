// frontend/src/components/LeadTable.js
import React, { useState } from "react";
import axios from "axios";

export default function LeadTable({ leads }) {
  const [loadingId, setLoadingId] = useState(null);
  const [generated, setGenerated] = useState({});

  const API = process.env.REACT_APP_API_URL || ""; // same origin fallback

  const generateMessage = async (leadId) => {
    setLoadingId(leadId);
    try {
      const { data } = await axios.post(
        `${API}/api/generate-ai-message/`,
        { lead_id: leadId }
      );
      setGenerated((prev) => ({ ...prev, [leadId]: data.message }));
    } catch (err) {
      console.error(err);
      setGenerated((prev) => ({
        ...prev,
        [leadId]: "❌ Error generating message",
      }));
    } finally {
      setLoadingId(null);
    }
  };

  return (
    <div className="rounded-xl bg-white p-4 shadow-md">
      <h2 className="mb-4 text-xl font-semibold">📇 Leads</h2>

      <table className="w-full table-auto border">
        <thead>
          <tr className="bg-gray-200 text-left">
            <th className="p-2">Name</th>
            <th className="p-2">Phone</th>
            <th className="p-2">Vehicle</th>
            <th className="p-2">Message</th>
            <th className="p-2">Action</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <tr key={lead.id} className="border-t">
              <td className="p-2">
                {lead.firstname} {lead.lastname}
              </td>
              <td className="p-2">{lead.cellphone}</td>
              <td className="p-2">{lead.vehicle_interest}</td>
              <td className="whitespace-pre-wrap p-2 text-sm">
                {generated[lead.id] || "—"}
              </td>
              <td className="p-2">
                <button
                  className="rounded bg-green-600 px-3 py-1 text-white hover:bg-green-700 disabled:opacity-50"
                  disabled={loadingId === lead.id}
                  onClick={() => generateMessage(lead.id)}
                >
                  {loadingId === lead.id ? "Generating…" : "💬 Generate"}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
