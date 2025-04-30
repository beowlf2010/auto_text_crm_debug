// frontend/src/pages/SmartInbox.jsx  (side‑swap + timestamp fix)
//-------------------------------------------------------------------
import React, { useState, useEffect, useCallback, useRef } from "react";
import dayjs from "dayjs";
import API from "../axios";

/* — small inline modal — */
function Modal({ open, onClose, children }) {
  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-lg shadow-xl p-4 w-full max-w-lg"
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}

export default function SmartInbox({ lead, refreshLeads }) {
  const [thread, setThread] = useState([]);
  const [draft, setDraft] = useState("");
  const [showModal, setShowModal] = useState(false);
  const threadEndRef = useRef(null);

  /* load messages */
  const loadThread = useCallback(async () => {
    if (!lead) return;
    const { data } = await API.get(`/api/message-thread/${lead.id}/`);
    setThread(data.messages);
  }, [lead]);

  /* initial + poll */
  useEffect(() => {
    loadThread();
    const id = setInterval(loadThread, 10000);
    return () => clearInterval(id);
  }, [loadThread]);

  /* scroll to bottom whenever thread changes */
  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [thread]);

  /* send */
  const send = async () => {
    if (!draft.trim()) return;
    await API.post("/api/send-message/", {
      lead_id: lead.id,
      content: draft.trim(),
      source: "Manual",
    });
    setDraft("");
    loadThread();
    refreshLeads();
  };

  /* regenerate */
  const regenerate = async () => {
    const { data } = await API.post(`/api/regenerate-message/${lead.id}/`);
    setDraft(data.message);
    setShowModal(true);
  };

  if (!lead) return <div className="p-8">Select a lead…</div>;

  return (
    <div className="flex flex-col h-full">
      <header className="p-3 border-b flex items-center justify-between">
        <h2 className="font-semibold">{lead.name}</h2>
        <button
          onClick={regenerate}
          className="text-sm text-blue-600 hover:underline"
        >
          ✍️ Regenerate
        </button>
      </header>

      {/* thread */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2 bg-gray-50">
        {thread.map((m, i) => (
          <div
            key={i}
            className={`max-w-[75%] rounded-lg p-2 whitespace-pre-wrap break-words ${
              m.from_customer
                ? "bg-gray-200 text-gray-800 mr-auto" // inbound – left
                : m.sent_by_ai
                ? "bg-blue-200 text-blue-900 ml-auto" // outbound AI – right
                : "bg-green-200 text-green-900 ml-auto" // outbound human – right
            }`}
          >
            <div className="text-[10px] text-right text-gray-500 mb-1">
              {dayjs(m.timestamp).format("M/D h:mm A")}
            </div>
            {m.body}
          </div>
        ))}
        <div ref={threadEndRef} />
      </div>

      {/* composer */}
      <div className="p-3 border-t flex gap-2 bg-white">
        <textarea
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="flex-1 border rounded p-2 resize-none"
          rows={2}
          placeholder="Type a message…"
        />
        <button
          onClick={send}
          disabled={!draft.trim()}
          className="bg-green-600 text-white px-4 rounded hover:bg-green-700 disabled:opacity-50"
        >
          Send
        </button>
      </div>

      {/* regenerate modal */}
      <Modal open={showModal} onClose={() => setShowModal(false)}>
        <h3 className="font-medium mb-2">Edit draft</h3>
        <textarea
          className="w-full border rounded p-2 resize-none mb-3"
          rows={5}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <div className="text-right">
          <button
            onClick={() => setShowModal(false)}
            className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700"
          >
            Use draft
          </button>
        </div>
      </Modal>
    </div>
  );
}
