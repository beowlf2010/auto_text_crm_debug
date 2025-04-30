// frontend/src/pages/SettingsPage.jsx
import React, { useState } from "react";

/**
 * SettingsPage
 * ─────────────
 * • Placeholder section for dealership configuration.
 * • Add tabs or accordions as new settings grow (SMTP, Twilio, lead scoring, etc.).
 */
export default function SettingsPage() {
  // Example of something you might persist later
  const [dealerName, setDealerName] = useState("");

  return (
    <div className="mx-auto max-w-3xl p-6">
      <h1 className="mb-6 text-2xl font-bold">⚙️ Settings</h1>

      {/* Dealer profile (placeholder) */}
      <section className="rounded-lg border bg-white p-4 shadow-sm">
        <h2 className="mb-2 text-lg font-semibold">Dealer Profile</h2>

        <label className="block text-sm font-medium text-gray-700">
          Dealership Name
          <input
            type="text"
            className="mt-1 w-full rounded-md border px-3 py-2"
            value={dealerName}
            onChange={(e) => setDealerName(e.target.value)}
            placeholder="e.g. Twin Bridges Auto"
          />
        </label>

        <p className="mt-4 text-xs text-gray-500">
          (More settings coming soon&mdash;SMTP credentials, AI prompt tuning,
          etc.)
        </p>
      </section>
    </div>
  );
}
