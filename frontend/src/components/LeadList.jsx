// frontend/src/components/LeadList.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import MessageThread from "./MessageThread";

export default function LeadList() {
  const [leads, setLeads] = useState([]);
  const [expandedLeadId, setExpandedLeadId] = useState(null);
  const API = process.env.REACT_APP_API_URL || ""; // same‑origin fallback

  /* ------------------------------------------------------------ */
  /*  Fetch leads once on mount                                   */
  /* ------------------------------------------------------------ */
  useEffect(() => {
    axios
      .get(`${API}/api/leads/`)
      .then((res) => setLeads(res.data))
      .catch((err) => console.error("Lead fetch error:", err));
  }, [API]);

  /* ------------------------------------------------------------ */
  /*  Render                                                      */
  /* ------------------------------------------------------------ */
  return (
    <div className="p-6">
      <h1 className="mb-4 text-xl font-bold">📋 Lead List</h1>

      {leads.map((lead) => (
        <div
          key={lead.id}
          className="mb-4 rounded border border-gray-200 bg-white p-4 shadow"
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold">{lead.name}</h2>
              <p className="text-sm text-gray-600">📞 {lead.cellphone}</p>
            </div>

            <button
              onClick={() =>
                setExpandedLeadId(expandedLeadId === lead.id ? null : lead.id)
              }
              className="text-sm text-blue-500 underline"
            >
              {expandedLeadId === lead.id ? "Hide Messages" : "View Messages"}
            </button>
          </div>

          {/* AI message preview */}
          {lead.ai_message ? (
            <p className="mt-2 text-sm text-green-700">💬 {lead.ai_message}</p>
          ) : (
            <p className="mt-2 text-sm text-yellow-600">
              ⚠️ No AI message yet.
            </p>
          )}

          {/* Message thread */}
          {expandedLeadId === lead.id && (
            <div className="mt-4 border-t pt-4">
              <MessageThread leadId={lead.id} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
