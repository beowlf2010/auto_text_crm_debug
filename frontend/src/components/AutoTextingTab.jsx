import React, { useState, useEffect } from "react";
import axios from "axios";

const AutoTextingTab = () => {
  const [leads, setLeads] = useState([]);
  const [status, setStatus] = useState({});

  useEffect(() => {
    axios
      .get(`${process.env.REACT_APP_API_URL}/api/leads/`)
      .then((res) => setLeads(res.data))
      .catch((err) => console.error("Error fetching leads:", err));
  }, []);

  const triggerAutoText = async (leadId) => {
    setStatus((prev) => ({ ...prev, [leadId]: "Sending..." }));

    try {
      // 1. Generate AI message
      const aiRes = await axios.post(`${process.env.REACT_APP_API_URL}/api/generate-ai-message/`, {
        lead_id: leadId,
      });

      const message = aiRes.data.message;

      // 2. Send message
      await axios.post(`${process.env.REACT_APP_API_URL}/api/send-message/`, {
        lead_id: leadId,
        message,
      });

      setStatus((prev) => ({ ...prev, [leadId]: "Sent ✅" }));
    } catch (err) {
      console.error("Auto-text failed:", err);
      setStatus((prev) => ({ ...prev, [leadId]: "Error ❌" }));
    }
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-semibold mb-4">🤖 Auto Texting Dashboard</h2>
      <div className="space-y-3">
        {leads.map((lead) => (
          <div
            key={lead.id}
            className="bg-white shadow border rounded p-4 flex justify-between items-center"
          >
            <div>
              <p className="text-sm font-semibold">{lead.name}</p>
              <p className="text-xs text-gray-500">📞 {lead.cellphone}</p>
              <p className="text-xs text-gray-400 italic">Source: {lead.source || "N/A"}</p>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => triggerAutoText(lead.id)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 rounded"
              >
                Trigger Follow-up
              </button>
              <span className="text-xs text-gray-600">{status[lead.id]}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AutoTextingTab;
