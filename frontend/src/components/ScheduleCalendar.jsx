// frontend/src/components/ScheduleCalendar.jsx
import React, { useEffect, useState, useMemo } from 'react';
import Calendar from 'react-calendar';
import 'react-calendar/dist/Calendar.css';
import axios from 'axios';

const ScheduleCalendar = () => {
  const [value, setValue] = useState(new Date());
  const [events, setEvents] = useState([]);
  const API = process.env.REACT_APP_API_URL || "";

  useEffect(() => {
    axios.get(`${API}/api/schedule-calendar/`)
      .then(res => setEvents(res.data))
      .catch(err => console.error('Calendar fetch failed', err));
  }, [API]);

  const formatDate = (date) => date.toISOString().split('T')[0];

  const leadsForSelectedDate = useMemo(() => {
    const dateStr = formatDate(value);
    return events.filter(event =>
      event.next_ai_send_at?.startsWith(dateStr)
    );
  }, [events, value]);

  return (
    <div className="bg-white shadow p-4 rounded mt-6">
      <h2 className="text-lg font-bold mb-2">📅 Scheduled Follow-Ups</h2>
      <Calendar value={value} onChange={setValue} />

      <div className="mt-4">
        <h3 className="text-sm font-semibold">
          Messages on {formatDate(value)}:
        </h3>
        <ul className="text-xs mt-2 text-gray-700 space-y-1">
          {leadsForSelectedDate.length > 0 ? (
            leadsForSelectedDate.map((e, i) => (
              <li key={i}>
                📨 {e.lead || "Unknown"} ({e.phone || "no phone"}) – {e.vehicle || "no vehicle"}
              </li>
            ))
          ) : (
            <li>No scheduled messages.</li>
          )}
        </ul>
      </div>
    </div>
  );
};

export default ScheduleCalendar;
