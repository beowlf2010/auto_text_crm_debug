// frontend/src/components/Layout.jsx
import React from "react";
import { NavLink, useLocation } from "react-router-dom";

/* sidebar links */
const links = [
  { to: "/dashboard",    label: "Dashboard", icon: "🏠" },
  { to: "/leads",        label: "Leads",     icon: "👤" },
  { to: "/upload",       label: "Upload",    icon: "⬆️" },
  { to: "/smart-inbox",  label: "Inbox",     icon: "📥" },
  // NOTE: keep path “/auto-texting”, but show label “Auto Text”
  { to: "/auto-texting", label: "Auto Text", icon: "🤖" },
  { to: "/settings",     label: "Settings",  icon: "⚙️" },
];

function Sidebar() {
  const { pathname } = useLocation();
  return (
    <nav className="w-48 shrink-0 bg-slate-900 text-white">
      <h2 className="p-4 font-bold text-xl">🚗 Auto Text CRM</h2>

      <ul className="space-y-1">
        {links.map(({ to, label, icon }) => (
          <li key={to}>
            <NavLink
              to={to}
              className={({ isActive }) =>
                `block px-4 py-2 hover:bg-slate-700 ${
                  isActive || pathname === to ? "bg-slate-800" : ""
                }`
              }
            >
              <span className="mr-2">{icon}</span>
              {label}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

export default function Layout({ children }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-gray-50">{children}</main>
    </div>
  );
}
