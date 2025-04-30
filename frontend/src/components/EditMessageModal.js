// components/EditMessageModal.js
import React from "react";

export default function EditMessageModal({
  lead,
  editedMessage,
  setEditedMessage,
  onCancel,
  onSend,
}) {
  if (!lead) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-lg">
        <h2 className="mb-4 text-lg font-bold">
          ✏️ Edit Message for {lead.firstname} {lead.lastname}
        </h2>

        <textarea
          className="mb-4 h-40 w-full rounded border border-gray-300 p-2"
          value={editedMessage}
          onChange={(e) => setEditedMessage(e.target.value)}
        />

        <div className="flex justify-end gap-3">
          <button
            className="rounded bg-gray-300 px-4 py-2 text-gray-800 hover:bg-gray-400"
            onClick={onCancel}
          >
            Cancel
          </button>
          <button
            className="rounded bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
            onClick={onSend}
          >
            Send Text
          </button>
        </div>
      </div>
    </div>
  );
}
