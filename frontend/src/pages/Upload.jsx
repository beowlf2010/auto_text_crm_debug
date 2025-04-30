// ✅ LOCKED: 2025-04-23 – API_BASE fixed for port 80 local dev

import React, { useState, useRef, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const API_BASE =
  process.env.REACT_APP_API_URL ||
  (window.location.hostname === "localhost"
    ? "http://localhost"
    : "http://web");

const Upload = () => {
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const onDrop = useCallback((accepted) => {
    if (accepted.length) {
      setFile(accepted[0]);
      toast.info(`📄 Selected: ${accepted[0].name}`);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "text/csv": [".csv"] },
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) {
      toast.warn("Please select a CSV file first.");
      return;
    }

    const formData = new FormData();
    formData.append("csv_file", file);

    try {
      await axios.post(`${API_BASE}/api/upload-leads/`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
        maxRedirects: 0,
        validateStatus: (status) => status >= 200 && status < 400,
      });

      toast.success("✅ Upload successful!");
      setFile(null);
    } catch (err) {
      console.error("Upload error:", err);
      toast.error("❌ Upload failed. Check CSV and try again.");
    }
  };

  return (
    <div className="p-6 space-y-6">
      <ToastContainer position="bottom-right" autoClose={3000} />

      <h1 className="text-2xl font-bold">📤 Upload Leads</h1>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
          isDragActive ? "border-blue-600 bg-blue-50" : "border-gray-300"
        }`}
      >
        <input {...getInputProps()} />
        <p className="text-sm">
          {isDragActive
            ? "Drop the CSV here…"
            : file
            ? `📄 Ready: ${file.name}`
            : "Drag & drop CSV here, or click to browse"}
        </p>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".csv"
        className="hidden"
        onChange={(e) => {
          if (e.target.files.length) {
            setFile(e.target.files[0]);
            toast.info(`📄 Selected: ${e.target.files[0].name}`);
          }
        }}
      />

      <button
        onClick={handleUpload}
        className={`bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 ${
          !file ? "opacity-50 cursor-not-allowed" : ""
        }`}
        disabled={!file}
      >
        Upload
      </button>
    </div>
  );
};

export default Upload;
