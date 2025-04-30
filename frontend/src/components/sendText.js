// utils/sendText.js
import axios from "axios";

/**
 * Send an SMS (or in‑app text) via your Django endpoint.
 *
 * @param {number} leadId   – dashboard_lead PK
 * @param {string} content  – message body
 * @param {string} source   – "Manual" | "AI" (default "Manual")
 * @returns  {Promise<{success: boolean, id?: number, error?: string}>}
 */
export default async function sendText(leadId, content, source = "Manual") {
  const API = process.env.REACT_APP_API_URL || ""; // same‑origin fallback

  try {
    const { data } = await axios.post(`${API}/api/send-message/`, {
      lead_id: leadId,
      content,
      source,
    });
    return { success: true, id: data.id };
  } catch (err) {
    console.error("SMS send error:", err);
    return {
      success: false,
      error: err.response?.data?.detail || err.message,
    };
  }
}
