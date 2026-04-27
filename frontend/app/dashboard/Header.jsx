"use client";

import { useState, useEffect } from "react";
import { LogOut, Sun } from "lucide-react";
import { createClient } from "../lib/supabase";
import { useRouter } from "next/navigation";

export default function Header({ user }) {
  const router = useRouter();
  const supabase = createClient();
  const [title, setTitle] = useState("Dashboard");
  const [subtitle, setSubtitle] = useState("Identity-first content engine");
  const [isBackendUp, setIsBackendUp] = useState(false);

  // Sync title with hash
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace("#", "") || "dashboard";
      const titles = {
        "dashboard": { t: "Dashboard", s: "Overview of your content engine" },
        "identity": { t: "Phase 1 - Identity", s: "Vectorized profile and voice context" },
        "trends": { t: "Phase 2 - Trends", s: "Real-time niche topic detection" },
        "generate": { t: "Phase 2 - Generate", s: "AI content generation engine" },
        "review": { t: "Phase 3 - Review", s: "Approve or edit generated drafts" },
        "schedule": { t: "Phase 4 - Schedule", s: "Auto-posted content calendar" },
        "notifications": { t: "Notifications", s: "System alerts and trend pings" },
      };
      
      if (titles[hash]) {
        setTitle(titles[hash].t);
        setSubtitle(titles[hash].s);
      }
    };

    handleHashChange();
    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  useEffect(() => {
    const checkBackend = async () => {
        try {
            const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
            const res = await fetch(`${API_URL}/health`);
            if (res.ok) setIsBackendUp(true);
        } catch(e) {
            setIsBackendUp(false);
        }
    };
    checkBackend();
  }, []);

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  return (
    <header className="h-16 px-8 flex items-center justify-between border-b border-[var(--color-border)] bg-[var(--color-bg-primary)]/60 backdrop-blur-md sticky top-0 z-30">
      <div>
        <h1 className="font-[family-name:var(--font-heading)] font-semibold text-lg text-[var(--color-text-primary)]">
          {title}
        </h1>
        <p className="text-xs text-[var(--color-text-secondary)]">{subtitle}</p>
      </div>

      <div className="flex items-center gap-4">
        {isBackendUp ? (
          <div className="hidden sm:flex items-center gap-2 text-xs text-emerald-400 bg-emerald-400/10 px-3 py-1.5 rounded-full border border-emerald-400/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            Backend Connected
          </div>
        ) : (
          <div className="hidden sm:flex items-center gap-2 text-xs text-rose-400 bg-rose-400/10 px-3 py-1.5 rounded-full border border-rose-400/20">
             <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span>
             Backend Disconnected
          </div>
        )}

        <button 
          onClick={() => window.location.hash = 'generate'}
          className="bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] text-[var(--color-text-primary)] text-sm font-medium px-4 py-1.5 rounded-lg transition-colors shadow-lg"
        >
          + Generate
        </button>

        <button 
          onClick={handleSignOut}
          className="p-1.5 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] transition-colors"
          title="Sign Out"
        >
          <LogOut size={18} />
        </button>
      </div>
    </header>
  );
}
