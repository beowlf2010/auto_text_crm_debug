// frontend/src/components/StatCards.js
import React from "react";
import PropTypes from "prop-types";

export default function StatCards({ leads = [], messages = [] }) {
  const totalLeads = leads.length;
  const messagedCount = messages.length;
  const successful = messages.filter((m) => !m.error)?.length || 0;
  const failed = messagedCount - successful;

  return (
    <div className="my-6 grid gap-4 grid-cols-2 md:grid-cols-4">
      <Card color="blue" value={totalLeads} label="Total Leads" />
      <Card color="green" value={messagedCount} label="Messages Sent" />
      <Card color="yellow" value={successful} label="Successful" />
      <Card color="red" value={failed} label="Failed" />
    </div>
  );
}

function Card({ color, value, label }) {
  return (
    <div
      className={`rounded-xl bg-${color}-100 text-${color}-900 p-4 shadow text-center`}
    >
      <div className="text-xl font-bold">{value}</div>
      <div>{label}</div>
    </div>
  );
}

StatCards.propTypes = {
  leads: PropTypes.array,
  messages: PropTypes.array,
};

Card.propTypes = {
  color: PropTypes.string.isRequired,
  value: PropTypes.number.isRequired,
  label: PropTypes.string.isRequired,
};
