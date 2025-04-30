// frontend/src/pages/LeadsPage.jsx
import React from "react";
import LeadDetail from "../components/LeadDetail"; // ← adjust path if needed

/**
 * Wrapper so React‑Router can lazy‑load the detail view.
 * If you keep this file here, ensure the import points to the
 * actual component (usually ../components or ./components).
 */
export default function LeadsPage() {
  return <LeadDetail />;
}
