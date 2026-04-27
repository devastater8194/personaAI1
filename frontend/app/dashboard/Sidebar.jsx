"use client";

import { useState } from "react";
import { Home, User, Lightbulb, PenTool, CheckSquare, Calendar, Bell } from "lucide-react";

export default function Sidebar({ user }) {
  const [active, setActive] = useState("dashboard");

  const menuItems = [
    { id: "dashboard", label: "Dashboard", icon: <Home size={18} /> },
    { id: "identity", label: "Phase 1 · Identity", icon: <User size={18} /> },
    { id: "trends", label: "Phase 2 · Trends", icon: <Lightbulb size={18} />, badge: 5 },
    { id: "generate", label: "Phase 2 · Generate", icon: <PenTool size={18} /> },
    { id: "review", label: "Phase 3 · Review", icon: <CheckSquare size={18} />, badge: 3 },
    { id: "schedule", label: "Phase 4 · Schedule", icon: <Calendar size={18} /> },
  ];

  const systemItems = [
    { id: "notifications", label: "Notifications", icon: <Bell size={18} />, badge: 2 },
  ];

  // Using hashes for navigation in the SPA dashboard page
  const handleNav = (id) => {
    setActive(id);
    window.location.hash = id;
  };

  // Wait for component to mount to read hash (in a real app we'd sync this with Next.js router)
  useState(() => {
    if (typeof window !== "undefined" && window.location.hash) {
      setActive(window.location.hash.replace("#", ""));
    }
  });

  return (
    <aside className="w-64 min-w-[16rem] h-full bg-[var(--color-bg-sidebar)] border-r border-[var(--color-border)] flex flex-col hidden md:flex">
      <div className="p-6 border-b border-[var(--color-border)]">
        <div className="font-[family-name:var(--font-heading)] text-xl font-bold tracking-tight">
          Persona<span className="text-[var(--color-accent-primary)]">AI</span>
        </div>
        <div className="text-[11px] text-[var(--color-text-muted)] uppercase tracking-widest mt-1">Content OS v1.0</div>
      </div>

      <div className="p-4 flex-1 overflow-y-auto overflow-x-hidden space-y-6">
        <div>
          <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest px-3 mb-2 font-semibold">Workflow</div>
          <ul>
            {menuItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => handleNav(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm transition-colors ${
                    active === item.id
                      ? "bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/10 text-[var(--color-accent-primary)] font-medium relative"
                      : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-card)] hover:text-[var(--color-text-primary)]"
                  }`}
                >
                  {active === item.id && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-3/5 bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] rounded-r-full" />
                  )}
                  <div className="flex items-center gap-3">
                    {item.icon}
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="bg-rose-500 text-[var(--color-text-primary)] text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
                      {item.badge}
                    </span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest px-3 mb-2 font-semibold">System</div>
          <ul>
            {systemItems.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => handleNav(item.id)}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-sm transition-colors ${
                    active === item.id
                      ? "bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/10 text-[var(--color-accent-primary)] font-medium relative"
                      : "text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-card)] hover:text-[var(--color-text-primary)]"
                  }`}
                >
                  {active === item.id && (
                    <div className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-3/5 bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] rounded-r-full" />
                  )}
                  <div className="flex items-center gap-3">
                    {item.icon}
                    <span>{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="bg-emerald-500 text-[var(--color-text-primary)] text-[10px] font-bold px-1.5 py-0.5 rounded-full min-w-[20px] text-center">
                      {item.badge}
                    </span>
                  )}
                </button>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="p-4 border-t border-[var(--color-border)]">
        <div className="flex items-center gap-3 p-2 rounded-xl bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] cursor-pointer transition-colors">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center font-bold text-[var(--color-text-primary)] text-xs">
            {user?.email?.charAt(0).toUpperCase() || "U"}
          </div>
          <div className="overflow-hidden flex-1">
            <div className="text-sm font-medium text-[var(--color-text-primary)] truncate">
              {user?.user_metadata?.full_name || "User"}
            </div>
            <div className="text-[11px] text-[var(--color-text-muted)] truncate">{user?.email}</div>
          </div>
        </div>
      </div>
    </aside>
  );
}
