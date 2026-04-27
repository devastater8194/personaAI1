"use client";

import { useState, useEffect } from "react";
import { createClient } from "../lib/supabase";

// Import extracted view components
import DashboardView from "./views/DashboardView";
import IdentityView from "./views/IdentityView";
import TrendsView from "./views/TrendsView";
import GenerateView from "./views/GenerateView";
import ReviewView from "./views/ReviewView";
import ScheduleView from "./views/ScheduleView";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [user, setUser] = useState(null);
  const supabase = createClient();

  useEffect(() => {
    supabase.auth.getUser().then(({ data: { user } }) => {
      setUser(user);
    });

    const handleHash = () => {
      const hash = window.location.hash.replace("#", "");
      if (hash) {
        setActiveTab(hash);
      }
    };

    handleHash();
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, [supabase]);

  if (!user) return null;

  return (
    <div className="animate-[fadeUp_0.3s_ease_both] w-full max-w-6xl mx-auto pb-20">
      {activeTab === "dashboard" && <DashboardView user={user} />}
      {activeTab === "identity" && <IdentityView user={user} />}
      {activeTab === "trends" && <TrendsView user={user} />}
      {activeTab === "generate" && <GenerateView user={user} />}
      {activeTab === "review" && <ReviewView user={user} />}
      {activeTab === "schedule" && <ScheduleView user={user} />}
      {activeTab === "notifications" && (
        <div className="text-[var(--color-text-secondary)] text-center mt-20">Notifications center coming soon!</div>
      )}
    </div>
  );
}
