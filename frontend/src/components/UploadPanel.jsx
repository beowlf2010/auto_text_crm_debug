// frontend/src/components/UploadPanel.jsx
import React, { useState } from "react";
import axios from "axios";

export default function UploadPanel({ onUploadComplete }) {
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const API = process.env.REACT_APP_API_URL || ""; // fallback to same origin

  const handleUpload = async () => {
    if (!file) {
      alert("Please choose a CSV file first ⬆️");
      return;
    }
    setBusy(true);

    try {
      const form = new FormData();
      form.append("file", file, file.name);

      const { data } = await axios.post(`${API}/api/upload-leads/`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert(`✅ ${data.imported} leads imported, ${data.skipped} skipped.`);
      onUploadComplete?.();
    } catch (err) {
      console.error("Upload error:", err);
      alert(
        err.response?.data?.detail || "❌ Upload failed. Check console for details."
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mb-6 rounded-xl bg-white p-4 shadow">
      <h2 className="mb-4 text-xl font-semibold">⬆️ Upload Leads (CSV)</h2>

      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0] ?? null)}
        className="mb-4 block"
      />

      <button
        onClick={handleUpload}
        disabled={busy}
        className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
      >
        {busy ? "Uploading…" : "Upload CSV"}
      </button>
    </div>
  );
}
