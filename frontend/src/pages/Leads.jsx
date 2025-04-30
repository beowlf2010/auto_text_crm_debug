// ✅ LOCKED: 2025-04-23 – Leads view synced with backend: filter, AI controls, SmartInbox

import React, { useEffect, useState, useCallback } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import API from "../axios";
import SmartInbox from "../components/SmartInbox";

dayjs.extend(relativeTime);

const REFRESH_MS = 10_000;

const statusClasses = {
  "Not Started": "bg-gray-200 text-gray-700",
  Generated: "bg-yellow-200 text-yellow-800",
  Sent: "bg-green-200 text-green-800",
};

const FILTER_BUTTONS = [
  { k: "all",          lbl: "All" },
  { k: "replied",      lbl: "💬 Replied" },
  { k: "hot",          lbl: "🔥 Hot" },
  { k: "scheduled",    lbl: "⏱ Scheduled" },
  { k: "paused",       lbl: "⏸ Paused" },
  { k: "not_opted_in", lbl: "❌ No AI" },
];

export default function Leads() {
  const [leads, setLeads]             = useState([]);
  const [selectedLead, setSelected]   = useState(null);
  const [filter, setFilter]           = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  const fetchLeads = useCallback(async () => {
    const { data } = await API.get(`/api/leads/?filter=${filter}`);
    setLeads(Array.isArray(data) ? data : data.leads || []);
  }, [filter]);

  useEffect(() => {
    fetchLeads();
    const id = setInterval(fetchLeads, REFRESH_MS);
    return () => clearInterval(id);
  }, [fetchLeads]);

  const handleStartAI    = async (id) => { await API.post(`/api/start-ai/${id}/`);    fetchLeads(); };
  const handlePauseAI    = async (id) => { await API.post(`/api/pause-ai/${id}/`);    fetchLeads(); };
  const handleRegenerate = async (id) => { await API.post(`/api/regenerate-message/${id}/`); fetchLeads(); };

  const filteredLeads = leads
    .filter((lead) => {
      const matchesQuery =
        !searchQuery.trim() ||
        lead.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        lead.cellphone?.includes(searchQuery);
      if (!matchesQuery) return false;

      switch (filter) {
        case "replied":
          return lead.new_message;
        case "hot":
          return (lead.score || 0) >= 60;
        case "scheduled":
          return lead.ai_active === true;
        case "paused":
          return lead.opted_in_for_ai && !lead.ai_active;
        case "not_opted_in":
          return !lead.opted_in_for_ai;
        default:
          return true;
      }
    })
    .sort((a, b) => (b.score || 0) - (a.score || 0));

  const statusChip = (status) => (
    <span
      className={`inline-block px-2 py-0.5 text-xs rounded-full ${
        statusClasses[status] || "bg-gray-100 text-gray-700"
      }`}
    >
      {status === "Generated"
        ? "✍️ Generated"
        : status === "Sent"
        ? "📤 Sent"
        : "🕓 Not Started"}
    </span>
  );

  const scoreBadge = (score = 0) => {
    const label =
      score >= 60 ? "🔥 Hot" : score >= 30 ? "🌤 Warm" : "❄️ Cold";
    const color =
      score >= 60
        ? "text-red-600"
        : score >= 30
        ? "text-yellow-600"
        : "text-blue-500";
    return <span className={`text-xs font-semibold ${color}`}>{label} ({score})</span>;
  };

  return (
    <div className="flex h-screen">
      <div className="w-1/3 border-r overflow-y-auto p-4 bg-white">
        <h2 className="text-xl font-semibold mb-4">📋 All Leads</h2>

        <input
          placeholder="Search by name or phone…"
          className="mb-3 w-full border px-3 py-1 text-sm rounded"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />

        <div className="flex gap-2 mb-4 text-xs flex-wrap">
          {FILTER_BUTTONS.map((b) => (
            <button
              key={b.k}
              onClick={() => setFilter(b.k)}
              className={`px-2 py-1 rounded border ${
                filter === b.k ? "bg-blue-600 text-white" : "bg-gray-100"
              }`}
            >
              {b.lbl}
            </button>
          ))}
        </div>

        <div className="space-y-8">
          {Object.entries(
            filteredLeads.reduce((acc, lead) => {
              const stage = lead.follow_up_stage || "Uncategorised";
              (acc[stage] = acc[stage] || []).push(lead);
              return acc;
            }, {})
          ).map(([stage, list]) => (
            <div key={stage}>
              <h3 className="text-sm font-semibold text-gray-700 mb-1">📆 {stage}</h3>
              <ul className="space-y-4">
                {list.map((lead) => {
                  const idleDays = lead.last_texted
                    ? dayjs().diff(dayjs(lead.last_texted), "day")
                    : null;

                  return (
                    <li
                      key={lead.id}
                      onClick={() => setSelected(lead)}
                      className={`border p-3 rounded shadow-sm hover:bg-blue-50 cursor-pointer ${
                        idleDays >= 7 ? "border-red-500 bg-red-50" : ""
                      }`}
                    >
                      <div className="font-bold flex justify-between items-center">
                        <span>{lead.name || "Unnamed"}</span>
                        {scoreBadge(lead.score)}
                      </div>

                      <div className="text-xs text-gray-500 italic">
                        {idleDays != null
                          ? idleDays >= 7
                            ? `⏱ Idle ${idleDays} days`
                            : `⏱ No reply ${idleDays} day${idleDays !== 1 ? "s" : ""}`
                          : "No messages sent yet"}
                      </div>

                      <div className="text-sm text-gray-700">{lead.cellphone}</div>
                      <div className="text-xs text-gray-500">{lead.vehicle_interest}</div>

                      <div className="text-xs flex flex-wrap items-center gap-1 mt-1">
                        {lead.opted_in_for_ai ? (
                          lead.ai_active ? (
                            <>
                              ✅ Opted‑In •
                              <button
                                className="text-blue-600 underline"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handlePauseAI(lead.id);
                                }}
                              >
                                ❚❚ Pause
                              </button>
                            </>
                          ) : (
                            <>
                              ⏸ Paused •
                              <button
                                className="text-green-700 underline"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleStartAI(lead.id);
                                }}
                              >
                                ▶️ Resume AI
                              </button>
                            </>
                          )
                        ) : (
                          <button
                            className="text-green-700 underline"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStartAI(lead.id);
                            }}
                          >
                            ▶️ Start AI
                          </button>
                        )}

                        {lead.new_message && "• 💬 Replied"}
                        {lead.appointment_time && (
                          <>• 📅 {dayjs(lead.appointment_time).format("MMM D, h:mm A")}</>
                        )}
                        {statusChip(lead.message_status)}
                      </div>

                      <div className="mt-1 text-xs">
                        <button
                          className="text-indigo-700 underline"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRegenerate(lead.id);
                          }}
                        >
                          🔁 Regenerate Message
                        </button>

                        {lead.next_ai_send_at && (
                          <div className="mt-1">
                            <span className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-1 rounded">
                              📅 Next: {dayjs(lead.next_ai_send_at).format("MMM D, h:mm A")}
                            </span>
                          </div>
                        )}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
        <SmartInbox lead={selectedLead} refreshLeads={fetchLeads} />
      </div>
    </div>
  );
}
