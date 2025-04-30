import React from "react";
import Papa from "papaparse";
import axios from "axios";

/**
 * CSV uploader + lead normaliser.
 *
 * Props
 * ─────
 * onDataLoaded(leads[])  – optional callback with the parsed leads array
 */
export default function Dropzone({ onDataLoaded }) {
  const API = process.env.REACT_APP_API_URL || ""; // fallback to same‑origin

  /* ------------------------------------------------------------ */
  /*  Upload handler                                               */
  /* ------------------------------------------------------------ */
  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      transformHeader: (h) => h.toLowerCase(),
      complete: ({ data }) => processRows(data),
    });
  };

  /* ------------------------------------------------------------ */
  /*  Normalise + POST to backend                                 */
  /* ------------------------------------------------------------ */
  const processRows = async (rows) => {
    // map → dashboard Lead model field names
    const leads = rows
      .map((row) => ({
        firstname: row.firstname || "",
        lastname: row.lastname || "",
        email: row.email || "",
        cellphone: row.cellphone || row.dayphone || "",
        VehicleYear: row.vehicleyear || "",
        VehicleMake: row.vehiclemake || "",
        VehicleModel: row.vehiclemodel || "",
        SalesPersonFirstName: row.salespersonfirstname || "",
        ai_message: `Hey ${row.firstname}, are you still interested in the ${row.vehicleyear} ${row.vehiclemake} ${row.vehiclemodel}? Let’s make it happen! 🚗💨`,
      }))
      .filter((l) => l.cellphone); // keep rows with a phone #

    if (leads.length === 0) {
      return alert("❌ Upload failed. No valid leads found.");
    }

    // lift up to parent if requested
    if (onDataLoaded) onDataLoaded(leads);

    /* ---- POST to Django REST endpoint ------------------------ */
    try {
      await axios.post(`${API}/api/upload-leads/`, { leads });
      alert(`✅ ${leads.length} leads uploaded successfully!`);
    } catch (err) {
      console.error(err);
      alert("❌ Upload failed. Check server log or CSV format.");
    }
  };

  /* ------------------------------------------------------------ */
  /*  Render                                                      */
  /* ------------------------------------------------------------ */
  return (
    <div className="mt-6 rounded-xl bg-white p-6 shadow-md">
      <h2 className="mb-4 text-lg font-semibold">📤 Upload Leads</h2>
      <input
        type="file"
        accept=".csv"
        onChange={handleFileUpload}
        className="mb-4"
      />
    </div>
  );
}
