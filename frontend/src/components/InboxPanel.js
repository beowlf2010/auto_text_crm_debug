// frontend/src/components/InboxPanel.js
import React, { useEffect, useState } from "react";
import axios from "axios";

/**
 * Real–time inbox panel
 *
 * Props
 * ─────
 * selectedLeadId  – integer ID of the lead to display
 */
export default function InboxPanel({ selectedLeadId }) {
  const API = process.env.REACT_APP_API_URL || ""; // fallback to same origin
  const [lead, setLead] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(false);

  /* ------------------------------------------------------------ */
  /*  Fetch thread when lead changes                              */
  /* ------------------------------------------------------------ */
  useEffect(() => {
    if (!selectedLeadId) return;
    fetchInboxData(selectedLeadId);

    // poll every 5 s for new replies
    const id = setInterval(() => fetchInboxData(selectedLeadId), 5000);
    return () => clearInterval(id);
  }, [selectedLeadId]);

  const fetchInboxData = async (id) => {
    try {
      // 1) lead detail  2) message history
      const [leadRes, threadRes] = await Promise.all([
        axios.get(`${API}/api/leads/${id}/`),
        axios.get(`${API}/message-thread/${id}/`),
      ]);
      setLead(leadRes.data);
      setMessages(threadRes.data);
    } catch (err) {
      console.error("Inbox fetch error:", err);
    }
  };

  /* ------------------------------------------------------------ */
  /*  Helpers: send text                                          */
  /* ------------------------------------------------------------ */
  const postMessage = async (content, source = "Manual") => {
    if (!content.trim()) return;
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/api/send-message/`, {
        lead_id: selectedLeadId,
        content,
        source,
      });
      // append optimistically
      setMessages((prev) => [
        ...prev,
        {
          id: data.id ?? Date.now(), // fallback key
          content,
          direction: "OUT",
          source,
          timestamp: new Date().toISOString(),
        },
      ]);
      setNewMessage("");
    } catch (err) {
      console.error("Send error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleManualSend = () => postMessage(newMessage, "Manual");

  const handleGenerateAndSendAI = async () => {
    setLoading(true);
    try {
      const { data } = await axios.post(
        `${API}/api/generate-ai-message/`,
        { lead_id: selectedLeadId }
      );
      await postMessage(data.message, "AI");
    } catch (err) {
      console.error("AI generate error:", err);
      setLoading(false);
    }
  };

  /* ------------------------------------------------------------ */
  /*  Render                                                      */
  /* ------------------------------------------------------------ */
  return (
    <div className="flex h-full flex-col rounded-xl border bg-white p-4 shadow">
      {lead && (
        <header className="mb-2">
          <h2 className="text-xl font-bold">{lead.name}</h2>
          <p className="text-sm text-gray-600">{lead.cellphone}</p>
        </header>
      )}

      {/* message thread */}
      <section className="flex-1 overflow-y-auto rounded border bg-gray-50 p-2">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`mb-2 rounded p-2 text-sm ${
              m.direction === "IN"
                ? "bg-yellow-100 text-left"
                : m.source === "AI"
                ? "bg-green-100 text-right"
                : "bg-blue-100 text-right"
            }`}
          >
            <div className="text-xs text-gray-600">
              {m.source} – {new Date(m.timestamp).toLocaleString()}
            </div>
            {m.content}
          </div>
        ))}
      </section>

      {/* composer */}
      <footer className="mt-4 flex flex-col">
        <textarea
          rows={3}
          className="mb-2 rounded border p-2"
          placeholder="Type a message…"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
        <div className="flex gap-2">
          <button
            onClick={handleManualSend}
            disabled={loading || !newMessage.trim()}
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Send Manual
          </button>
          <button
            onClick={handleGenerateAndSendAI}
            disabled={loading}
            className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50"
          >
            Generate + Send AI
          </button>
        </div>
      </footer>
    </div>
  );
}
