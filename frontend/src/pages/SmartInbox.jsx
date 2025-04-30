// ✅ LOCKED: 2025-04-23 — Smart Inbox functional: AI preview, reply, opt-in/out, timers

import React, { useEffect, useState, useRef, useCallback } from "react";
import axios from "../axios";
import toast from "react-hot-toast";
import useSound from 'use-sound';
import notificationSfx from "../assets/notification.mp3";

const SmartInbox = () => {
  const [leads, setLeads] = useState([]);
  const [activeTab, setActiveTab] = useState("replied");
  const [play] = useSound(notificationSfx);
  const [lastUnreadCount, setLastUnreadCount] = useState(0);
  const [selectedLead, setSelectedLead] = useState(null);
  const [messageInput, setMessageInput] = useState("");
  const messageEndRef = useRef(null);

  const fetchLeads = useCallback(async () => {
    try {
      const res = await axios.get("/api/leads/");
      const data = res.data?.leads || [];
      const unread = data.filter(l => l.new_message).length;
      setLeads(data);

      if (unread > lastUnreadCount) {
        play();
        toast.success("New customer message");
      }
      setLastUnreadCount(unread);
    } catch (err) {
      console.error("Lead fetch error:", err);
    }
  }, [lastUnreadCount, play]);

  const fetchThread = async (leadId) => {
    try {
      const res = await axios.get(`/api/message-thread/${leadId}/`);
      const lead = leads.find(l => l.id === leadId);
      setSelectedLead({ ...lead, thread: res.data, typing: true });

      setTimeout(() => setSelectedLead(prev => ({ ...prev, typing: false })), 1200);
    } catch (err) {
      console.error("Thread fetch error:", err);
    }
  };

  const handleReply = async () => {
    if (!selectedLead || !messageInput) return;
    try {
      await axios.post("/api/send-message/", {
        lead_id: selectedLead.id,
        message: messageInput
      });
      toast.success("Message sent");
      setMessageInput("");
      fetchThread(selectedLead.id);
      fetchLeads();
    } catch (err) {
      console.error("Send error:", err);
      toast.error("Failed to send");
    }
  };

  const handleRegenerate = async (leadId) => {
    try {
      await axios.post(`/api/regenerate-message/${leadId}/`);
      toast.success("Message regenerated");
      fetchLeads();
    } catch (err) {
      toast.error("Failed to regenerate");
    }
  };

  const toggleOptIn = async (lead) => {
    try {
      const url = lead.opted_in_for_ai ? `/api/pause-ai/${lead.id}/` : `/api/start-ai/${lead.id}/`;
      await axios.post(url);
      toast.success("AI follow-up toggled");
      fetchLeads();
    } catch (err) {
      console.error("Toggle error:", err);
      toast.error("Toggle failed");
    }
  };

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(fetchLeads, 8000);
    return () => clearInterval(interval);
  }, [fetchLeads]);

  useEffect(() => {
    if (messageEndRef.current) {
      messageEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [selectedLead?.thread]);

  const formatCountdown = (timestamp) => {
    const diff = new Date(timestamp).getTime() - Date.now();
    if (diff <= 0) return "now";
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    return `${hours}h ${mins}m`;
  };

  const countdownColor = (timestamp) => {
    const diff = new Date(timestamp).getTime() - Date.now();
    return diff < 3600000 ? "text-red-600 font-semibold" : "text-gray-500";
  };

  const isOverdue = (lead) => {
    return lead.next_ai_send_at && new Date(lead.next_ai_send_at) < Date.now() && !lead.new_message;
  };

  const filtered = leads
    .filter((lead) => {
      if (activeTab === "replied") return lead.new_message;
      if (activeTab === "scheduled") return lead.opted_in_for_ai;
      if (activeTab === "paused") return !lead.opted_in_for_ai;
      return true;
    })
    .sort((a, b) => {
      const aTime = new Date(a.next_ai_send_at || 0).getTime();
      const bTime = new Date(b.next_ai_send_at || 0).getTime();
      return aTime - bTime;
    });

  return (
    <div className="p-4">
      <div className="mb-4 flex gap-2">
        <button onClick={() => setActiveTab("replied")} className="btn">Replied</button>
        <button onClick={() => setActiveTab("scheduled")} className="btn">Scheduled</button>
        <button onClick={() => setActiveTab("paused")} className="btn">Paused</button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* LEFT PANE: Lead List */}
        <div>
          {filtered.map((lead) => (
            <div key={lead.id}
              className={`bg-white rounded-xl p-4 shadow mb-4 border cursor-pointer ${isOverdue(lead) ? "border-red-600 bg-red-50" : ""}`}
              onClick={() => fetchThread(lead.id)}
            >
              <div className="flex justify-between items-center">
                <div>
                  <h3 className="text-xl font-bold">{lead.firstname} {lead.lastname}</h3>
                  <p className="text-gray-500">{lead.cellphone}</p>
                  <p className="text-xs italic text-gray-400">
                    Score: {lead.score || 0} • Last AI: {lead.last_texted || "-"}
                  </p>
                </div>
                {lead.new_message && <span className="text-red-500 font-bold">NEW</span>}
              </div>

              <div className="mt-2 flex gap-2 flex-wrap items-center">
                <button onClick={() => handleRegenerate(lead.id)} className="btn btn-sm">Regenerate</button>
                <button onClick={() => fetchThread(lead.id)} className="btn btn-sm btn-primary">Send</button>
                <button onClick={() => toggleOptIn(lead)} className="btn btn-sm btn-secondary">
                  {lead.opted_in_for_ai ? "Pause" : "Resume"}
                </button>

                {lead.next_ai_send_at && (
                  <>
                    <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
                      📅 Next: {new Date(lead.next_ai_send_at).toLocaleString()}
                    </span>
                    <span className={`text-xs ${countdownColor(lead.next_ai_send_at)}`}>
                      ⏳ Next in: {formatCountdown(lead.next_ai_send_at)}
                    </span>
                  </>
                )}
              </div>

              {lead.ai_message ? (
                <div className="mt-2 text-sm text-gray-600">
                  💬 <span className="font-semibold">Next Message Preview:</span>
                  <div className="mt-1 bg-gray-50 border border-gray-200 p-2 rounded">
                    {lead.ai_message}
                  </div>
                </div>
              ) : (
                <div className="mt-2 text-sm italic text-gray-400">
                  No AI message generated yet.
                </div>
              )}
            </div>
          ))}
        </div>

        {/* RIGHT PANE: Thread View */}
        <div>
          {selectedLead ? (
            <div className="bg-white rounded-xl p-4 shadow border h-full">
              <h3 className="text-xl font-bold mb-2">Message Thread</h3>
              <div className="h-64 overflow-y-scroll bg-gray-50 p-2 mb-2">
                {selectedLead.thread?.map((msg, idx) => (
                  <div key={idx} className={`mb-1 text-sm ${msg.from_customer ? "text-left" : "text-right"}`}>
                    <span className="inline-block bg-blue-100 px-2 py-1 rounded-md max-w-xs">{msg.body}</span>
                  </div>
                ))}
                {selectedLead.typing && <div className="italic text-sm text-gray-400 mt-1">Typing...</div>}
                <div ref={messageEndRef} />
              </div>
              <div className="flex gap-2">
                <input value={messageInput} onChange={e => setMessageInput(e.target.value)} placeholder="Type a reply..." className="flex-1 border rounded px-2" />
                <button onClick={handleReply} className="btn btn-sm btn-primary">Reply</button>
              </div>
            </div>
          ) : (
            <div className="text-gray-400 italic p-4">Select a lead to view the message thread</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SmartInbox;
