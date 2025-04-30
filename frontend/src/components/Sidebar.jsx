// src/components/Sidebar.jsx
import React from "react";
import {
  Home,
  Upload,
  MessageSquare,
  Users,
  Settings,
  Inbox,
} from "lucide-react";
import { NavLink } from "react-router-dom";

const Sidebar = () => {
  const navItems = [
    { name: "Dashboard", icon: <Home size={20} />, path: "/" },
    { name: "Leads", icon: <Users size={20} />, path: "/leads" },
    { name: "Upload", icon: <Upload size={20} />, path: "/upload" },
    { name: "Inbox", icon: <Inbox size={20} />, path: "/inbox" },
    { name: "Auto Texting", icon: <MessageSquare size={20} />, path: "/auto-texting" },
    { name: "Settings", icon: <Settings size={20} />, path: "/settings" },
  ];

  return (
    <div className="fixed top-0 left-0 h-screen w-64 bg-gray-800 text-white shadow-lg">
      <div className="border-b border-gray-700 p-4 text-xl font-bold">
        🚗 Auto Text CRM
      </div>
      <ul className="mt-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 p-3 rounded transition duration-200 ${
                isActive
                  ? "bg-blue-600 text-white"
                  : "text-gray-200 hover:bg-gray-700"
              }`
            }
          >
            {item.icon}
            {item.name}
          </NavLink>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;
