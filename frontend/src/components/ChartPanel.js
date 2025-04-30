import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

// Demo dataset — replace with live KPI data when ready
const data = [
  { name: "Mon", texts: 12 },
  { name: "Tue", texts: 18 },
  { name: "Wed", texts: 9 },
  { name: "Thu", texts: 15 },
  { name: "Fri", texts: 21 },
  { name: "Sat", texts: 7 },
  { name: "Sun", texts: 4 },
];

const ChartPanel = () => (
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

export default ChartPanel;
