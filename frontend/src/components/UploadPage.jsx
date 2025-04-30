// frontend/src/pages/UploadPage.jsx
import React, { useState } from "react";
import axios from "axios";
import Dropzone from "../components/Dropzone";

export default function UploadPage() {
  const API = process.env.REACT_APP_API_URL || ""; // same‑origin fallback
  const [status, setStatus] = useState(null); // "success" | "error" | null
  const [message, setMessage] = useState("");

  /** Handle CSV file selected in <Dropzone> */
  const handleUpload = async (file) => {
    const form = new FormData();
    form.append("file", file, file.name);

    setStatus(null);
    setMessage("Uploading…");

    try {
      const { data } = await axios.post(`${API}/api/upload-leads/`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setStatus("success");
      setMessage(`✅ ${data.imported} leads imported, ${data.skipped} skipped.`);
    } catch (err) {
      console.error(err);
      setStatus("error");
      setMessage(
        err.response?.data?.detail || "❌ Upload failed. Check console."
      );
    }
  };

  return (
    <div className="mx-auto max-w-2xl p-6">
      <h1 className="mb-6 text-2xl font-bold">📤 Upload CSV</h1>

      <Dropzone onFileAccepted={handleUpload} accept=".csv" />

      {status && (
        <p
          className={`mt-4 rounded p-2 text-sm ${
            status === "success"
              ? "bg-green-100 text-green-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {message}
        </p>
      )}
    </div>
  );
}
