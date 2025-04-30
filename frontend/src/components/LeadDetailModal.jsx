import React, { useEffect, useState } from "react";
import API from "../axios";

const LeadDetailModal = ({ lead, onClose }) => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiMessage, setAiMessage] = useState(lead?.ai_message || "");

  useEffect(() => {
    if (!lead?.id) return;
    API.get(`/message-thread/${lead.id}/`)
      .then((res) => {
        setMessages(res.data.messages || []);
        setAiMessage(res.data.lead?.ai_message || lead.ai_message || "");
      })
      .catch((err) => console.error("Message fetch failed:", err))
      .finally(() => setLoading(false));
  }, [lead]);

  const regenerate = async () => {
    try {
      const res = await API.post("/api/generate-ai-message/", {
        lead_id: lead.id,
      });
      setAiMessage(res.data.message);
    } catch (err) {
      alert("⚠️ Failed to generate message");
    }
  };

  const sendNow = async () => {
    try {
      await API.post("/api/send-message/", {
        lead_id: lead.id,
        content: aiMessage, // ✅ renamed key from "message" to match backend
        source: "AI",
      });
      alert("✅ Message sent!");
      onClose();
    } catch (err) {
      alert("❌ Failed to send");
      console.error(err);
    }
  };

  if (!lead) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="relative w-full max-w-3xl rounded bg-white p-6 shadow">
        <button
          onClick={onClose}
          className="absolute right-2 top-2 text-gray-600"
        >
          ✖
        </button>

        <h2 className="text-xl font-bold mb-2">{lead.name}</h2>
        <div className="mb-4 text-sm text-gray-500">
          {lead.cellphone} | {lead.vehicle_interest || "No vehicle"}
          <br />
          Source: {lead.source || "N/A"} | Salesperson:{" "}
          {lead.salesperson || "Unassigned"}
        </div>

        <h3 className="mb-1 text-sm font-semibold">📜 Message History</h3>
        <div className="mb-4 max-h-48 overflow-y-auto rounded border bg-gray-50 p-2 text-sm text-gray-700">
          {loading ? (
            "Loading..."
          ) : messages.length > 0 ? (
            messages.map((msg, i) => (
              <div key={i} className="mb-2">
                <span className="font-bold">[{msg.source}]</span>{" "}
                {msg.content || msg.message}
                <div className="text-xs text-gray-400">
                  {new Date(msg.timestamp).toLocaleString()}
                </div>
              </div>
            ))
          ) : (
            <div>No messages yet.</div>
          )}
        </div>

        <label className="mb-1 block text-sm font-medium text-gray-700">
          ✍️ AI Message Preview
        </label>
        <textarea
          className="mb-2 w-full rounded border p-2 text-sm text-gray-700"
          value={aiMessage}
          onChange={(e) => setAiMessage(e.target.value)}
          rows={4}
        />

        <div className="flex justify-between gap-4">
          <button
            onClick={regenerate}
            className="rounded bg-yellow-400 px-4 py-2 text-white shadow hover:bg-yellow-500"
          >
            🔁 Regenerate
          </button>
          <button
            onClick={sendNow}
            className="rounded bg-blue-600 px-4 py-2 text-white shadow hover:bg-blue-700"
          >
            📤 Send Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default LeadDetailModal;
