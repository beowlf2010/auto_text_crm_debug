// frontend/src/components/InboxMessages.js
import React, { useEffect, useState } from "react";
import axios from "axios";

export default function InboxMessages({ leadId }) {
  const [messages, setMessages] = useState([]);
  const API = process.env.REACT_APP_API_URL || ""; // same‑origin fallback

  /* ------------------------------------------------------------ */
  /*  Fetch thread on mount or when leadId changes                */
  /* ------------------------------------------------------------ */
  useEffect(() => {
    if (!leadId) return;

    const fetchMessages = async () => {
      try {
        // Django URL pattern:  message-thread/<int:lead_id>/
        const { data } = await axios.get(
          `${API}/message-thread/${leadId}/`
        );
        setMessages(data);
      } catch (err) {
        console.error("Failed to load messages:", err);
      }
    };

    fetchMessages();
  }, [leadId, API]);

  /* ------------------------------------------------------------ */
  /*  Render                                                      */
  /* ------------------------------------------------------------ */
  return (
    <div className="max-h-96 overflow-y-auto rounded-xl bg-white p-4 shadow-md">
      <h2 className="mb-3 text-xl font-bold">📨 Message History</h2>

      {messages.length === 0 ? (
        <p className="text-gray-500">No messages yet.</p>
      ) : (
        messages.map((msg) => (
          <div
            key={msg.id}
            className={`mb-3 rounded-md border p-2 text-sm ${
              msg.direction === "IN"
                ? "bg-gray-100 text-left"
                : "bg-blue-100 text-right"
            }`}
          >
            <div>{msg.content}</div>
            <div className="text-xs text-gray-400">
              {new Date(msg.timestamp).toLocaleString()}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
