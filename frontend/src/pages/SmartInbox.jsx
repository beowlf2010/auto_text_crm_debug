// C:\Projects\auto_text_crm_dockerized_clean\frontend\src\pages\SmartInbox.jsx
// 🔄 2025-05-06 – merged & fixed syntax (className template literal)

import React, { useCallback, useEffect, useRef, useState } from "react";
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";
import axios from "../axios";
import toast from "react-hot-toast";
import useSound from "use-sound";
import notificationSfx from "../assets/notification.mp3";

dayjs.extend(duration);

/* ───── helper functions ───── */
const formatCountdown = (ts) => {
  const diff = dayjs(ts).diff(dayjs(), "second");
  if (diff <= 0) return "now";
  const d = dayjs.duration(diff, "second");
  return `${Math.floor(d.asHours())}h ${d.minutes()}m`;
};

const countdownClass = (ts) =>
  dayjs(ts).diff(dayjs(), "hour") < 1 ? "text-red-600 font-semibold" : "text-gray-500";

const statusColor = (s) =>
  (
    {
      not_started: "bg-gray-400",
      pending: "bg-yellow-400",
      approved: "bg-blue-500",
      sent: "bg-green-500",
    }[s] || "bg-gray-400"
  );

/* ───── component ───── */
export default function SmartInbox() {
  const [leads, setLeads] = useState([]);
  const [lastUnreadCount, setLastUnreadCount] = useState(0);
  const [selectedLead, setSelectedLead] = useState(null);
  const [messageInput, setMessageInput] = useState("");
  const messageEndRef = useRef(null);
  const [play] = useSound(notificationSfx);

  /* fetch leads every 30 s */
  const fetchLeads = useCallback(async () => {
    try {
      const { data } = await axios.get("/api/leads/");
      const list = data?.leads ?? [];
      const unread = list.filter((l) => l.new_message).length;
      if (unread > lastUnreadCount) {
        play();
        toast.success("New customer message");
      }
      setLastUnreadCount(unread);
      setLeads(list);
    } catch (err) {
      console.error("Lead fetch error:", err);
    }
  }, [lastUnreadCount, play]);

  useEffect(() => {
    fetchLeads();
    const id = setInterval(fetchLeads, 30_000);
    return () => clearInterval(id);
  }, [fetchLeads]);

  /* open thread */
  const openThread = useCallback(async (leadId) => {
    try {
      const { data } = await axios.get(`/api/message-thread/${leadId}/`);
      const lead = leads.find((l) => l.id === leadId);
      if (!lead) return;
      setSelectedLead({ ...lead, thread: data.messages ?? [] });
      setTimeout(() => messageEndRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    } catch (err) {
      console.error("Thread fetch error:", err);
    }
  }, [leads]);

  /* manual reply */
  const handleReply = async () => {
    const body = messageInput.trim();
    if (!selectedLead || !body) return;
    try {
      await axios.post("/api/send-message/", { lead_id: selectedLead.id, message: body });
      toast.success("Message sent");
      setMessageInput("");
      await openThread(selectedLead.id);
      await fetchLeads();
    } catch (err) {
      console.error(err);
      toast.error(err?.response?.data?.error || "Send failed");
    }
  };

  /* auto-open first */
  useEffect(() => {
    if (leads.length && !selectedLead) openThread(leads[0].id);
  }, [leads, selectedLead, openThread]);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold">Smart Inbox</h1>
      <div className="grid grid-cols-2 gap-4">
        {/* lead list */}
        <div className="space-y-2 overflow-y-auto h-[32rem] pr-2">
          {leads.map((lead) => (
            <div
              key={lead.id}
              onClick={() => openThread(lead.id)}
              className={`cursor-pointer border rounded p-2 shadow-sm hover:shadow transition ${selectedLead?.id === lead.id ? "ring-2 ring-blue-500" : ""}`}
            >
              <div className="flex items-center justify-between">
                <span className="font-medium">{lead.firstname ?? lead.name ?? "(no name)"}</span>
                <span className={`inline-block w-2 h-2 rounded-full ${statusColor(lead.message_status)}`} title={lead.message_status} />
              </div>
              {lead.next_ai_send_at && (
                <div className="mt-0.5 flex items-center gap-1">
                  <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-0.5 rounded">
                    📅 {new Date(lead.next_ai_send_at).toLocaleString(undefined, { month: "short", day: "numeric", hour: "numeric", minute: "2-digit" })}
                  </span>
                  <span className={`text-xs ${countdownClass(lead.next_ai_send_at)}`}>⏳ {formatCountdown(lead.next_ai_send_at)}</span>
                </div>
              )}
              {lead.ai_message ? (
                <div className="mt-1 text-xs text-gray-600 line-clamp-2">“{lead.ai_message}”</div>
              ) : (
                <div className="mt-1 text-xs italic text-gray-400">No AI draft yet</div>
              )}
            </div>
          ))}
        </div>

        {/* thread */}
        <div>
          {selectedLead ? (
            <div className="bg-white rounded-xl p-4 shadow border h-full flex flex-col">
              <h3 className="text-xl font-bold mb-2">{selectedLead.name}</h3>
              <div className="flex-1 overflow-y-auto bg-gray-50 p-2 mb-2">
                {selectedLead.thread.map((m, idx) => (
                  <div key={idx} className={`mb-1 text-sm ${m.from_customer ? "text-left" : "text-right"}`}>
                    <span className="inline-block bg-blue-100 px-2 py-1 rounded-md max-w-xs">{m.body}</span>
                  </div>
                ))}
                <div ref={messageEndRef} />
              </div>
              <div className="flex gap-2">
                <input
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                  placeholder="Type a reply…"
                  className="flex-1 border rounded px-2"
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      handleReply();
                    }
                  }}
                />
                <button onClick={handleReply} className="px-4 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 text-sm">
                  Send
                </button>
              </div>
            </div>
          ) : (
            <div className="italic text-gray-400 p-4">Select a lead…</div>
          )}
        </div>
      </div>
    </div>
  );
}
