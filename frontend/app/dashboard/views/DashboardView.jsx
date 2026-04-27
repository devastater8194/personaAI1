"use client";

import { useState, useEffect } from "react";

export default function DashboardView({ user }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const abortController = new AbortController();
    
    async function fetchStats() {
      try {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const res = await fetch(`${API_URL}/api/stats/${user.id}`, { signal: abortController.signal });
        const data = await res.json();
        setStats(data);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error("Failed to fetch stats:", err);
        }
      } finally {
        setLoading(false);
      }
    }
    if (user?.id) fetchStats();
    
    return () => abortController.abort();
  }, [user.id]);

  const firstName = user?.user_metadata?.full_name?.split(' ')[0] || 'there';
  const pendingCount = stats?.pending_count || 0;

  return (
    <>
      <div className="mb-8">
        <h2 className="text-2xl font-heading font-bold text-foreground mb-2">
          Heyy, {firstName} 
        </h2>
        <p className="text-(--color-text-secondary)">
          Here's your content overview. {pendingCount > 0 ? `${pendingCount} posts need your approval.` : 'You are all caught up.'}
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-(--color-accent-primary)"></div>
        </div>
      ) : (
      <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="glass-stat border border-(--color-border) rounded-xl p-5 shadow-lg">
          <div className="text-[11px] text-(--color-text-muted) uppercase tracking-widest mb-2 font-semibold">Total Drafts</div>
          <div className="text-3xl font-heading font-bold text-foreground">{stats?.total_drafts || 0}</div>
          <div className="text-xs text-(--color-text-muted) mt-1">Generated drafts</div>
        </div>
        <div className="glass-stat border border-(--color-border) rounded-xl p-5 shadow-lg">
          <div className="text-[11px] text-(--color-text-muted) uppercase tracking-widest mb-2 font-semibold">Pending approval</div>
          <div className="text-3xl font-heading font-bold text-foreground">{stats?.pending_count || 0}</div>
          <div className="text-xs mt-1">
            <button onClick={() => window.location.hash = 'review'} className="text-(--color-accent-primary) hover:underline">Review now &rarr;</button>
          </div>
        </div>
        <div className="glass-stat border border-(--color-border) rounded-xl p-5 shadow-lg">
          <div className="text-[11px] text-(--color-text-muted) uppercase tracking-widest mb-2 font-semibold">Scheduled</div>
          <div className="text-3xl font-heading font-bold text-foreground">{stats?.scheduled_count || 0}</div>
          <div className="text-xs text-(--color-text-muted) mt-1 truncate">
            {stats?.next_scheduled ? `Next: ${new Date(stats.next_scheduled.scheduled_for).toLocaleDateString()}` : 'No upcoming posts'}
          </div>
        </div>
        <div className="glass-stat border border-(--color-border) rounded-xl p-5 shadow-lg">
          <div className="text-[11px] text-(--color-text-muted) uppercase tracking-widest mb-2 font-semibold">Trending topics</div>
          <div className="text-3xl font-heading font-bold text-foreground">{stats?.trends_count || 0}</div>
          <div className="text-xs mt-1">
             <button onClick={() => window.location.hash = 'trends'} className="text-(--color-accent-primary) hover:underline">View trends &rarr;</button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Backend connection info */}
        {/* <div className="lg:col-span-2 space-y-6">
          <div className="glass-card border border-(--color-border) rounded-xl p-6 shadow-lg">
             <div className="flex justify-between items-center mb-4">
                 <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">FastAPI Backend Status</h3>
                 <span className="flex items-center gap-2 text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">
                     <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span> Connected
                 </span>
             </div>
             
             <div className="text-sm text-(--color-text-secondary) leading-relaxed mb-4">
                 Your Persona AI backend is fully operational and securely connected to your frontend dashboard.
             </div>

             <div className="grid grid-cols-2 gap-4">
                 <div className="border border-(--color-border) rounded-lg p-3 bg-(--color-bg-primary)/20">
                     <div className="text-xs text-(--color-text-muted) mb-1">Database</div>
                     <div className="text-[11px] text-foreground">Supabase (pgvector) connected</div>
                 </div>
                 <div className="border border-(--color-border) rounded-lg p-3 bg-(--color-bg-primary)/20">
                     <div className="text-xs text-(--color-text-muted) mb-1">LLM Engine</div>
                     <div className="text-[11px] text-foreground">OpenAI GPT-4o ready</div>
                 </div>
             </div>
          </div>
        </div> */}

        <div className="space-y-6">
          <div className="glass-card border border-(--color-border) rounded-xl p-6 shadow-lg">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-4">Quick Actions</h3>
            <div className="space-y-3">
               <button onClick={() => window.location.hash = 'identity'} className="w-full text-left bg-(--color-bg-primary)/20 hover:bg-(--color-bg-primary)/40 border border-(--color-border) transition px-4 py-3 rounded-lg text-sm text-gray-600 flex justify-between items-center group">
                 Update Identity Profile <span className="text-(--color-accent-primary) opacity-0 group-hover:opacity-100 transition-opacity">&rarr;</span>
               </button>
               <button onClick={() => window.location.hash = 'generate'} className="w-full text-left bg-(--color-bg-primary)/20 hover:bg-(--color-bg-primary)/40 border border-(--color-border) transition px-4 py-3 rounded-lg text-sm text-gray-600 flex justify-between items-center group">
                 Generate Content <span className="text-(--color-accent-primary) opacity-0 group-hover:opacity-100 transition-opacity">&rarr;</span>
               </button>
               <button onClick={() => window.location.hash = 'schedule'} className="w-full text-left bg-(--color-bg-primary)/20 hover:bg-(--color-bg-primary)/40 border border-(--color-border) transition px-4 py-3 rounded-lg text-sm text-gray-600 flex justify-between items-center group">
                 View Schedule <span className="text-(--color-accent-primary) opacity-0 group-hover:opacity-100 transition-opacity">&rarr;</span>
               </button>
            </div>
          </div>
        </div>
      </div>
      </>
      )}
    </>
  );
}
