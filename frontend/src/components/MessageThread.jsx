// ✅ LOCKED: 2025-04-23 – Fixed bubble sides + API_BASE applied for consistency

import React, { useCallback, useEffect, useRef, useState } from "react";
import axios from "axios";
import dayjs from "dayjs";

const API_BASE =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost"
    : "http://web");

export default function MessageThread({ lead, messages: initialMessages }) {
  const [messages, setMessages] = useState(initialMessages || []);
  const [newMsg, setNewMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const bottomRef = useRef(null);

  const fetchThread = useCallback(async (id) => {
    try {
      const { data } = await axios.get(`${API_BASE}/api/message-thread/${id}/`);
      setMessages(data.messages || []);
    } catch (err) {
      console.error(err);
    }
  }, []);

  const handleSend = async () => {
    if (!newMsg.trim() || !lead?.id) return;
    setBusy(true);
    try {
      await axios.post(`${API_BASE}/api/send-message/`, {
        lead_id: lead.id,
        content: newMsg,
        source: "Manual",
      });
      setNewMsg("");
      await fetchThread(lead.id);
    } catch (err) {
      console.error(err);
      alert("Send failed, see console");
    } finally {
      setBusy(false);
    }
  };

  const Bubble = ({ msg }) => {
    const outbound = msg.direction === "OUT" || msg.sent_by_ai;
    const inbound = !outbound;

    const container = `mb-3 flex ${inbound ? "justify-start" : "justify-end"}`;
    const bubble =
      `max-w-[70%] rounded-lg p-2 text-sm whitespace-pre-wrap break-words ` +
      (inbound
        ? "bg-gray-200 text-gray-800"
        : msg.sent_by_ai
        ? "bg-blue-600 text-white"
        : "bg-green-600 text-white");

    return (
      <div className={container}>
        <div className={bubble}>
          <div className="mb-1 text-[10px] text-right text-white/70">
            {dayjs(msg.timestamp).format("M/D h:mm A")}
          </div>
          {msg.content ?? msg.body ?? msg.message}
        </div>
      </div>
    );
  };

  useEffect(() => {
    if (!lead?.id || initialMessages) return;
    fetchThread(lead.id);
  }, [lead?.id, initialMessages, fetchThread]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (!lead)
    return <p className="italic text-gray-500 p-4">Select a lead to view the conversation.</p>;

  return (
    <div className="flex h-full flex-col rounded bg-white shadow-sm">
      <header className="border-b p-3 font-semibold">
        📨 Thread – {lead.first_name || lead.name} {lead.last_name || ""}
      </header>

      <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
        {messages.length ? (
          messages.map((m) => <Bubble key={m.id || m.timestamp} msg={m} />)
        ) : (
          <p className="italic text-sm text-gray-500">No messages yet.</p>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="border-t p-3 flex gap-2">
        <input
          className="flex-1 rounded border p-2"
          value={newMsg}
          onChange={(e) => setNewMsg(e.target.value)}
          placeholder="Type your message…"
        />
        <button
          onClick={handleSend}
          disabled={busy}
          className="rounded bg-green-600 px-4 py-2 text-white hover:bg-green-700 disabled:opacity-50"
        >
          {busy ? "Sending…" : "Send"}
        </button>
      </div>
    </div>
  );
}
