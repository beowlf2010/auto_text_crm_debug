// C:\Projects\auto_text_crm_dockerized_clean\frontend\src\pages\ScheduledMessages.jsx
// 2025‑04‑26 — Countdown timer + Pending/Approved tabs, live 1‑second updates

import React, { useCallback, useEffect, useState } from "react";
import API from "../axios";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";

dayjs.extend(relativeTime);

// helper --------------------------------------------------------------
const overdue = (ts) => dayjs(ts).isBefore(dayjs());
const fmt = (now, ts) => {
  if (!ts) return "";
  const abs = dayjs(ts).format("MMM D h:mm A");
  if (overdue(ts)) return `overdue (${abs})`;
  const diff = dayjs(ts).diff(now, "second");
  const h = Math.floor(diff / 3600)
    .toString()
    .padStart(2, "0");
  const m = Math.floor((diff % 3600) / 60)
    .toString()
    .padStart(2, "0");
  const s = Math.floor(diff % 60)
    .toString()
    .padStart(2, "0");
  return `${h}:${m}:${s} (${abs})`;
};

export default function ScheduledMessages() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(false);
  const [nextSend, setNextSend] = useState(null);
  const [activeTab, setActiveTab] = useState("pending");
  const [now, setNow] = useState(dayjs()); // ⏱ ticker

  // 1‑second ticker for countdown ------------------------------------
  useEffect(() => {
    const id = setInterval(() => setNow(dayjs()), 1000);
    return () => clearInterval(id);
  }, []);

  // fetch lead list ---------------------------------------------------
  const load = useCallback(async () => {
    setLoading(true);
    const { data } = await API.get("/api/leads/?filter=all");
    const enriched = data.leads.map((l) => ({
      ...l,
      isPending: !l.opted_in_for_ai,
    }));
    // banner — earliest future send
    const future = enriched
      .filter((l) => l.next_ai_send_at && !overdue(l.next_ai_send_at))
      .sort((a, b) => new Date(a.next_ai_send_at) - new Date(b.next_ai_send_at));
    setNextSend(future[0]?.next_ai_send_at || null);
    setRows(enriched);
    setLoading(false);
  }, []);

  useEffect(() => {
    load();
    const poll = setInterval(load, 30_000);
    return () => clearInterval(poll);
  }, [load]);

  const act = async (url) => {
    await API.post(url);
    load();
  };

  const visible = rows.filter((r) => (activeTab === "pending" ? r.isPending : !r.isPending));

  // render -------------------------------------------------------------
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold">AI Message Queue</h1>
      {nextSend && (
        <p className="text-sm text-gray-600">
          Next AI message in {dayjs(nextSend).from(now, true)} ({dayjs(nextSend).format("MMM D h:mm A")})
        </p>
      )}

      {/* tabs */}
      <div className="flex space-x-2 border-b mt-2">
        {[
          { id: "pending", label: `Pending Approval (${rows.filter((r) => r.isPending).length})` },
          { id: "approved", label: `Approved (${rows.filter((r) => !r.isPending).length})` },
        ].map((t) => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`px-4 py-1.5 text-sm border-b-2 transition-colors ${
              activeTab === t.id
                ? "border-blue-600 font-medium"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && <p className="mt-4 text-sm">Loading…</p>}

      {visible.length === 0 ? (
        <p className="mt-4 italic text-gray-500">Nothing here.</p>
      ) : (
        <div className="mt-4 space-y-4">
          {visible.map((l) => (
            <div key={l.id} className="border rounded-lg p-4 shadow-sm hover:shadow transition">
              <header className="flex items-center justify-between mb-2">
                <div>
                  <span className="font-medium">{l.name}</span>{" "}
                  {l.next_ai_send_at && (
                    <span
                      className={`text-xs ${
                        overdue(l.next_ai_send_at)
                          ? "text-red-600 font-semibold"
                          : "text-gray-500"
                      }`}
                    >
                      • {fmt(now, l.next_ai_send_at)}
                    </span>
                  )}
                </div>

                {activeTab === "pending" && (
                  <div className="space-x-2">
                    <button
                      className="px-3 py-1 text-sm rounded bg-green-600 text-white hover:bg-green-700"
                      onClick={() => act(`/api/approve-message/${l.id}/`)}
                    >
                      Approve
                    </button>
                    <button
                      className="px-3 py-1 text-sm rounded bg-yellow-500 text-white hover:bg-yellow-600"
                      onClick={() => act(`/api/skip-message/${l.id}/`)}
                    >
                      Skip 1&nbsp;day
                    </button>
                    <button
                      className="px-3 py-1 text-sm rounded bg-blue-600 text-white hover:bg-blue-700"
                      onClick={() => act(`/api/regenerate-message/${l.id}/`)}
                    >
                      Regenerate
                    </button>
                  </div>
                )}
              </header>

              <pre className="whitespace-pre-wrap text-sm leading-5">
                {l.ai_message || "No draft yet."}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
