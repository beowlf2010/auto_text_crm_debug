import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Mon', messages: 20 },
  { name: 'Tue', messages: 45 },
  { name: 'Wed', messages: 30 },
  { name: 'Thu', messages: 60 },
  { name: 'Fri', messages: 40 },
  { name: 'Sat', messages: 18 },
  { name: 'Sun', messages: 35 },
];

export default function ChartPanel() {
  return (
    <div className="bg-white p-6 rounded-2xl shadow">
      <h3 className="text-lg font-semibold mb-4">📊 Weekly Text Volume</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="messages" fill="#4f46e5" radius={[6, 6, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
