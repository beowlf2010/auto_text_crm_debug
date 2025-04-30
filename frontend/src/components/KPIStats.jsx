// C:\Projects\auto_text_crm_dockerized_clean\frontend\src\components\KPIStats.jsx
import React, { useEffect, useState } from "react";
import axios from "axios";

const KPIStats = () => {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    axios
      .get("/api/kpi-summary/")
      .then((res) => setStats(res.data))
      .catch((err) => console.error("Failed to fetch KPI summary", err));
  }, []);

  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 bg-gray-50 border p-4 rounded mb-4 text-sm text-gray-700">
      <div>
        <span className="font-bold">🔥 Hot Leads:</span>
        <br />
        {stats.hot_leads ?? "—"}
      </div>
      <div>
        <span className="font-bold">📈 Avg Score:</span>
        <br />
        {stats.avg_score ?? "—"}
      </div>
    </div>
  );
};

export default KPIStats;
