// frontend/src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

/* ------------------------------------------------------------------ */
/*  UploadPanel                                                       */
/* ------------------------------------------------------------------ */

const UploadPanel = ({ onRefreshLeads }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [leads, setLeads] = useState([]);
  const [loadingLeadId, setLoadingLeadId] = useState(null);
  const [aiMessages, setAiMessages] = useState({});

  const API = process.env.REACT_APP_API_URL || "";

  // initial fetch
  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    const { data } = await axios.get(`${API}/api/leads/`);
    setLeads(data);
    if (onRefreshLeads) onRefreshLeads(data);
  };

  const handleFileChange = (e) => setSelectedFile(e.target.files[0]);

  const handleUpload = async () => {
    if (!selectedFile) {
      alert("Please select a CSV first."); return;
    }
    const formData = new FormData();
    formData.append("file", selectedFile);

    const { data } = await axios.post(`${API}/upload-leads/`, formData);
    if (data.success) {
      alert(`✅ ${data.created} leads imported`);
      setSelectedFile(null);
      fetchLeads();
    } else {
      alert(`❌ ${data.error}`);
    }
  };

  const generateAi = async (id) => {
    setLoadingLeadId(id);
    try {
      const { data } = await axios.post(`${API}/api/generate-ai-message/`, {
        lead_id: id,
      });
      setAiMessages((prev) => ({ ...prev, [id]: data.message }));
      fetchLeads();
    } finally {
      setLoadingLeadId(null);
    }
  };

  const sendMessage = async (id) => {
    const lead = leads.find((l) => l.id === id);
    const message = lead?.ai_message || aiMessages[id];
    if (!message) return alert("⚠️ Generate a message first.");

    await axios.post(`${API}/api/send-message/`, {
      lead_id: id,
      content: message,
    });
    alert("✅ Sent");
    fetchLeads();
  };

  return (
    <div className="space-y-6">
      {/* CSV uploader */}
      <div className="rounded-xl bg-white p-4 shadow">
        <h2 className="mb-4 text-xl font-semibold">⬆️ Upload Leads</h2>
        <input type="file" onChange={handleFileChange} className="mb-4" />
        <button
          onClick={handleUpload}
          className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          Upload CSV
        </button>
      </div>

      {/* Lead list */}
      <div className="rounded-xl bg-white p-4 shadow">
        <h2 className="mb-4 text-xl font-semibold">📋 Lead List</h2>
        {leads.length === 0 ? (
          <p>No leads yet.</p>
        ) : (
          <ul className="space-y-4">
            {leads.map((lead) => (
              <li key={lead.id} className="border-b pb-4">
                <div className="flex justify-between">
                  <div>
                    <p className="text-lg font-semibold">{lead.name}</p>
                    <p className="text-sm text-gray-600">📞 {lead.cellphone}</p>
                    {lead.ai_message && (
                      <p className="mt-1 text-green-700">💬 {lead.ai_message}</p>
                    )}
                  </div>
                  <div className="flex flex-col space-y-2">
                    <button
                      onClick={() => generateAi(lead.id)}
                      disabled={loadingLeadId === lead.id}
                      className="rounded bg-blue-500 px-3 py-1 text-white hover:bg-blue-600 disabled:opacity-50"
                    >
                      {loadingLeadId === lead.id ? "Generating…" : "Generate AI"}
                    </button>
                    {(lead.ai_message || aiMessages[lead.id]) && (
                      <button
                        onClick={() => sendMessage(lead.id)}
                        className="rounded bg-green-600 px-3 py-1 text-white hover:bg-green-700"
                      >
                        Send
                      </button>
                    )}
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

/* ------------------------------------------------------------------ */
/*  ChartPanel (weekly texts)                                         */
/* ------------------------------------------------------------------ */

const ChartPanel = ({ data }) => (
  <div className="rounded-2xl border bg-white p-6 shadow">
    <h2 className="mb-4 text-lg font-semibold">Texts Sent This Week</h2>
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <XAxis dataKey="name" />
        <YAxis allowDecimals={false} />
        <Tooltip />
        <Bar dataKey="texts" fill="#4f46e5" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  </div>
);

/* ------------------------------------------------------------------ */
/*  Dashboard – wraps everything                                      */
/* ------------------------------------------------------------------ */

const Dashboard = () => {
  const [kpiData, setKpiData] = useState([]);
  const API = process.env.REACT_APP_API_URL || "";

  useEffect(() => {
    const fetchKpi = async () => {
      const { data } = await axios.get(`${API}/api/kpi-summary/`);
      // expect { weekly_texts: [{name:'Mon', texts:12}, …] }
      setKpiData(data.weekly_texts || []);
    };
    fetchKpi();
  }, []);

  return (
    <div className="space-y-8 p-6">
      {/* KPI Row */}
      <ChartPanel data={kpiData} />

      {/* Upload & lead management */}
      <UploadPanel />
    </div>
  );
};

export default Dashboard;
