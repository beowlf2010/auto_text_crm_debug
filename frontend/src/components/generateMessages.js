// frontend/src/components/generateMessages.js
import React, { useState } from "react";
import axios from "axios";

export default function GenerateMessages({ lead, onMessageGenerated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState("");

  const API = process.env.REACT_APP_API_URL || ""; // same‑origin fallback

  const handleGenerate = async () => {
    if (!lead?.id) return;

    setLoading(true);
    setError(null);

    try {
      const { data } = await axios.post(
        `${API}/api/generate-ai-message/`,
        { lead_id: lead.id }
      );

      setMessage(data.message);
      if (onMessageGenerated) onMessageGenerated(data.message);
    } catch (err) {
      console.error(err);
      setError("❌ Failed to generate message");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rounded-lg bg-gray-100 p-4">
      <button
        onClick={handleGenerate}
        disabled={loading || !lead?.id}
        className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Generating…" : "✨ Generate AI Message"}
      </button>

      {error && <p className="mt-2 text-red-500">{error}</p>}

      {message && (
        <div className="mt-4">
          <label className="font-semibold">Generated Message:</label>
          <textarea
            className="mt-2 w-full rounded border p-2"
            rows={5}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
        </div>
      )}
    </div>
  );
}
