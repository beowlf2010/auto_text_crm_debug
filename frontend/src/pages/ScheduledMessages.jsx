// C:\Projects\auto_text_crm_dockerized_clean\frontend\src\pages\ScheduledMessages.jsx
// ✨ 2025-05-03 – treats “sent” drafts as done
import React, { useCallback, useEffect, useState } from "react";
import API from "../axios";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import { toast } from "react-toastify";

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);

const HTTP_METHOD = "POST";

/* time helpers */
const toLocal = (ts) => dayjs.utc(ts).tz(dayjs.tz.guess());
const overdue = (ts) => toLocal(ts).isBefore(dayjs());
const absFmt  = (ts) => toLocal(ts).format("MMM D h:mm A");
const diffFmt = (now, ts) => {
  if (!ts) return "";
  if (overdue(ts)) return `overdue (${absFmt(ts)})`;
  const diff = toLocal(ts).diff(now, "second");
  const h = String(Math.floor(diff / 3600)).padStart(2, "0");
  const m = String(Math.floor((diff % 3600) / 60)).padStart(2, "0");
  const s = String(diff % 60).padStart(2, "0");
  return `${h}:${m}:${s} (${absFmt(ts)})`;
};

export default function ScheduledMessages() {
  const [rows, setRows]       = useState([]);
  const [loading, setLoading] = useState(false);
  const [nextSend, setNext]   = useState(null);
  const [tab, setTab]         = useState("pending");
  const [now, setNow]         = useState(dayjs());

  /* live ticker */
  useEffect(() => {
    const id = setInterval(() => setNow(dayjs()), 1000);
    return () => clearInterval(id);
  }, []);

  /* fetch leads */
  const load = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await API.get("/api/leads/?filter=all");
      const enriched = data.leads.map((lead) => ({
        ...lead,
        // pending unless status is approved OR sent
        isPending: !["approved", "sent"].includes(lead.message_status),
      }));
      const future = enriched
        .filter((l) => l.next_ai_send_at && !overdue(l.next_ai_send_at))
        .sort((a, b) => new Date(a.next_ai_send_at) - new Date(b.next_ai_send_at));
      setNext(future[0]?.next_ai_send_at ?? null);
      setRows(enriched);
    } catch (err) {
      console.error(err);
      toast.error("Failed loading leads.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, [load]);

  /* helper for optimistic UI */
  const backendCall = async (url, onSuccess) => {
    try {
      onSuccess();
      await API({ url, method: HTTP_METHOD, credentials: "include" });
    } catch {
      toast.error("Server error; list reloaded.");
      load();
    }
  };

  /* actions */
  const approveMsg  = (id) => backendCall(`/api/approve-message/${id}/`, () =>
    setRows((p) => p.map((r) =>
      r.id === id ? { ...r, isPending: false, message_status: "approved" } : r
    ))
  );

  const approveSend = (id) => backendCall(`/api/approve-send/${id}/`, () =>
    setRows((p) => p.filter((r) => r.id !== id))
  );

  const sendNow     = (id) => backendCall(`/api/send-now/${id}/`, () =>
    setRows((p) => p.filter((r) => r.id !== id))
  );

  const skipMsg     = (id) => backendCall(`/api/skip-message/${id}/`, () =>
    setRows((p) => p.map((r) =>
      r.id === id
        ? { ...r, isPending: false, next_ai_send_at: dayjs(r.next_ai_send_at).add(1, "day").toISOString() }
        : r
    ))
  );

  const regenDraft  = (id) => backendCall(`/api/regenerate-message/${id}/`, () => {});

  const visible = rows.filter((r) => (tab === "pending" ? r.isPending : !r.isPending));

  /* UI */
  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold">AI Message Queue</h1>

      {nextSend && (
        <p className="text-sm text-gray-600">
          Next AI message in {dayjs(nextSend).from(now, true)} ({absFmt(nextSend)})
        </p>
      )}

      {/* tabs */}
      <div className="flex space-x-2 border-b mt-2">
        {[
          { id: "pending",  label: `Pending Approval (${rows.filter((r) => r.isPending).length})` },
          { id: "approved", label: `Approved (${rows.filter((r) => !r.isPending).length})` },
        ].map((t) => (
          <button
            key={t.id}
            className={`px-4 py-1.5 text-sm border-b-2 transition-colors ${
              tab === t.id ? "border-blue-600 font-medium" : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => setTab(t.id)}
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
          {visible.map((lead) => (
            <div key={lead.id} className="border rounded-lg p-4 shadow-sm hover:shadow transition">
              <header className="flex items-center justify-between mb-2">
                <div>
                  <span className="font-medium">{lead.name}</span>{" "}
                  {lead.next_ai_send_at && (
                    <span
                      className={`text-xs ${
                        overdue(lead.next_ai_send_at) ? "text-red-600 font-semibold" : "text-gray-500"
                      }`}
                    >
                      • {diffFmt(now, lead.next_ai_send_at)}
                    </span>
                  )}
                </div>

                {tab === "pending" ? (
                  <div className="space-x-2">
                    <button className="px-3 py-1 text-sm rounded bg-green-600 text-white hover:bg-green-700"
                            onClick={() => approveMsg(lead.id)}>
                      Approve
                    </button>
                    <button className="px-3 py-1 text-sm rounded bg-indigo-600 text-white hover:bg-indigo-700"
                            onClick={() => approveSend(lead.id)}>
                      Approve&nbsp;&amp;&nbsp;Send Now
                    </button>
                    <button className="px-3 py-1 text-sm rounded bg-yellow-500 text-white hover:bg-yellow-600"
                            onClick={() => skipMsg(lead.id)}>
                      Skip 1 day
                    </button>
                    <button className="px-3 py-1 text-sm rounded bg-blue-600 text-white hover:bg-blue-700"
                            onClick={() => regenDraft(lead.id)}>
                      Regenerate
                    </button>
                  </div>
                ) : (
                  <button className="px-3 py-1 text-sm rounded bg-indigo-600 text-white hover:bg-indigo-700"
                          onClick={() => sendNow(lead.id)}>
                    Send Now
                  </button>
                )}
              </header>

              <pre className="whitespace-pre-wrap text-sm leading-5">
                {lead.ai_message || "No draft yet."}
              </pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
