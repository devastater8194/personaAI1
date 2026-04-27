// "use client";

// import { useState, useEffect, useCallback } from "react";
// import { createClient } from "../../lib/supabase";

// export default function ReviewView({ user }) {
//   const supabase = createClient();
//   const [drafts, setDrafts] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [stats, setStats] = useState(null);

//   const fetchDrafts = useCallback(async () => {
//     const { data } = await supabase
//       .from('content_drafts')
//       .select('*')
//       .eq('user_id', user.id)
//       .eq('status', 'draft')
//       .order('created_at', { ascending: false });

//     if (data) setDrafts(data);
//     setLoading(false);
//   }, [user.id, supabase]);

//   useEffect(() => {
//     fetchDrafts();
//   }, [fetchDrafts]);

//   useEffect(() => {
//     async function fetchStats() {
//       try {
//         const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
//         const res = await fetch(`${API_URL}/api/stats/${user.id}`);
//         const data = await res.json();
//         setStats(data);
//       } catch (err) {
//         console.error("Failed to fetch stats:", err);
//       }
//     }
//     if (user?.id) fetchStats();
//   }, [user]);

//   const handleApprove = async (id) => {
//     await supabase.from('content_drafts').update({ status: 'approved' }).eq('id', id);
//     setDrafts(drafts.filter(d => d.id !== id));
//     // Optionally refresh stats
//   };

//   const handleDelete = async (id) => {
//     await supabase.from('content_drafts').delete().eq('id', id);
//     setDrafts(drafts.filter(d => d.id !== id));
//   };

//   return (
//     <>
//       <div className="mb-8">
//         <h2 className="text-2xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-primary)] mb-2">
//           Phase 3 — Review + Approval
//         </h2>
//         <p className="text-[var(--color-text-secondary)]">Edit, approve, or reject drafts before they hit the auto-scheduler.</p>
//       </div>

//       <div className="grid grid-cols-4 gap-4 mb-8">
//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-4 shadow-lg backdrop-blur-md bg-opacity-80">
//           <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest font-semibold">Pending</div>
//           <div className="text-2xl font-[family-name:var(--font-heading)] font-bold text-amber-500 mt-1">{drafts.length}</div>
//         </div>
//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-4 shadow-lg backdrop-blur-md bg-opacity-80">
//           <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest font-semibold">Approved</div>
//           <div className="text-2xl font-[family-name:var(--font-heading)] font-bold text-emerald-500 mt-1">{stats?.approved_count || 0}</div>
//         </div>
//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-4 shadow-lg backdrop-blur-md bg-opacity-80">
//           <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest font-semibold">Scheduled</div>
//           <div className="text-2xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-primary)] mt-1">{stats?.scheduled_count || 0}</div>
//         </div>
//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-4 shadow-lg backdrop-blur-md bg-opacity-80">
//           <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest font-semibold">Posted</div>
//           <div className="text-2xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-muted)] mt-1">{stats?.posted_count || 0}</div>
//         </div>
//       </div>

//       {loading ? (
//         <div className="text-center text-[var(--color-text-muted)] mt-20">Loading pending drafts...</div>
//       ) : drafts.length === 0 ? (
//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] border-dashed rounded-xl p-16 text-center flex flex-col items-center">
//           <div className="w-16 h-16 bg-emerald-500/10 text-emerald-500 rounded-full flex items-center justify-center text-2xl mb-4">✓</div>
//           <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-1">All caught up</h3>
//           <p className="text-sm text-[var(--color-text-muted)] mb-6">You have no posts pending review.</p>
//           <button onClick={() => window.location.hash = 'generate'} className="bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] text-[var(--color-text-primary)] text-sm font-medium px-4 py-2 rounded-lg transition-colors border border-[var(--color-border)]">
//             Generate more content &rarr;
//           </button>
//         </div>
//       ) : (
//         <div className="space-y-6">
//           {drafts.map(draft => (
//              <div key={draft.id} className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-6">
//                <div className="flex justify-between items-center mb-4">
//                  <div className="flex items-center gap-3">
//                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
//                      draft.platform === 'linkedin' ? 'bg-blue-500/20 text-blue-400' :
//                      draft.platform === 'twitter' ? 'bg-gray-500/20 text-gray-300' :
//                      'bg-pink-500/20 text-pink-400'
//                    }`}>
//                      {draft.platform}
//                    </span>
//                    <span className="text-[10px] text-[var(--color-text-muted)]">Topic: {draft.topic}</span>
//                  </div>
//                </div>

//                <div contentEditable spellCheck="false" suppressContentEditableWarning className="bg-[var(--color-bg-card)] rounded-lg p-4 text-sm text-gray-200 whitespace-pre-wrap leading-relaxed border border-[var(--color-border)] max-h-64 overflow-y-auto mb-4 focus:outline-none focus:border-[var(--color-accent-primary)]">
//                  {draft.content}
//                </div>

//                <div className="flex gap-2">
//                  <button onClick={() => handleApprove(draft.id)} className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-medium px-4 py-2 rounded-lg transition-colors border border-emerald-500/20 flex-1">
//                    ✓ Approve & Queue for Schedule
//                  </button>
//                  <button onClick={() => handleDelete(draft.id)} className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-medium px-4 py-2 rounded-lg transition-colors border border-rose-500/20">
//                    ✗ Delete
//                  </button>
//                </div>
//              </div>
//           ))}
//         </div>
//       )}
//     </>
//   );
// }
"use client";

import { useState, useEffect, useCallback } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReviewView({ user }) {
  const [drafts, setDrafts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState(null);

  // ── Fetch drafts via backend API (bypasses RLS via service role) ──
  const fetchDrafts = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/generate/drafts/${user.id}?status=draft`);
      const data = await res.json();
      setDrafts(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to fetch drafts:", err);
      setDrafts([]);
    } finally {
      setLoading(false);
    }
  }, [user.id]);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats/${user.id}`);
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error("Failed to fetch stats:", err);
    }
  }, [user.id]);

  useEffect(() => {
    fetchDrafts();
    fetchStats();
  }, [fetchDrafts, fetchStats]);

  // ── Approve via backend PATCH (service role, no RLS issue) ──
  const handleApprove = async (id) => {
    try {
      await fetch(`${API_URL}/api/generate/approve/${id}`, { method: "PATCH" });
      setDrafts(prev => prev.filter(d => d.id !== id));
      fetchStats(); // refresh counters
    } catch (err) {
      console.error("Approve failed:", err);
    }
  };

  // ── Delete via backend DELETE ──
  const handleDelete = async (id) => {
    try {
      await fetch(`${API_URL}/api/generate/draft/${id}`, { method: "DELETE" });
      setDrafts(prev => prev.filter(d => d.id !== id));
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  return (
    <>
      <div className="mb-8">
        <h2 className="text-2xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-primary)] mb-2">
          Phase 3 — Review + Approval
        </h2>
        <p className="text-[var(--color-text-secondary)]">Edit, approve, or reject drafts before they hit the auto-scheduler.</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        {[
          { label: "Pending", value: drafts.length, color: "text-amber-500" },
          { label: "Approved", value: stats?.approved_count || 0, color: "text-emerald-500" },
          { label: "Scheduled", value: stats?.scheduled_count || 0, color: "text-[var(--color-text-primary)]" },
          { label: "Posted", value: stats?.posted_count || 0, color: "text-[var(--color-text-muted)]" },
        ].map(s => (
          <div key={s.label} className="glass-stat border border-[var(--color-border)] rounded-xl p-4">
            <div className="text-[10px] text-[var(--color-text-muted)] uppercase tracking-widest font-semibold">{s.label}</div>
            <div className={`text-2xl font-[family-name:var(--font-heading)] font-bold mt-1 ${s.color}`}>
              {s.value}
            </div>
          </div>
        ))}
      </div>

      {loading ? (
        <div className="text-center text-[var(--color-text-muted)] mt-20">Loading pending drafts…</div>
      ) : drafts.length === 0 ? (
        <div className="glass-card border border-[var(--color-border)] border-dashed rounded-xl p-16 text-center flex flex-col items-center">
          <div className="w-16 h-16 bg-emerald-500/10 text-emerald-500 rounded-full flex items-center justify-center text-2xl mb-4">✓</div>
          <h3 className="text-lg font-bold text-[var(--color-text-primary)] mb-1">All caught up</h3>
          <p className="text-sm text-[var(--color-text-muted)] mb-6">You have no posts pending review.</p>
          <button
            onClick={() => window.location.hash = "generate"}
            className="bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] text-[var(--color-text-primary)] text-sm font-medium px-4 py-2 rounded-lg transition-colors border border-[var(--color-border)]"
          >
            Generate more content →
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {drafts.map(draft => (
            <div key={draft.id} className="glass-card border border-[var(--color-border)] rounded-xl p-6">
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${draft.platform === "linkedin" ? "bg-blue-500/20 text-blue-400" :
                      draft.platform === "twitter" ? "bg-gray-500/20 text-gray-300" :
                        "bg-pink-500/20 text-pink-400"
                    }`}>
                    {draft.platform}
                  </span>
                  <span className="text-[10px] text-[var(--color-text-muted)]">Topic: {draft.topic}</span>
                </div>
                <span className="text-[10px] text-gray-600">
                  {new Date(draft.created_at).toLocaleDateString()}
                </span>
              </div>

              <div
                contentEditable
                spellCheck="false"
                suppressContentEditableWarning
                className="bg-[var(--color-bg-card)] rounded-lg p-4 text-sm text-gray-200 whitespace-pre-wrap leading-relaxed border border-[var(--color-border)] max-h-64 overflow-y-auto mb-4 focus:outline-none focus:border-[var(--color-accent-primary)]"
              >
                {draft.content}
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleApprove(draft.id)}
                  className="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-medium px-4 py-2 rounded-lg transition-colors border border-emerald-500/20 flex-1"
                >
                  ✓ Approve & Queue for Schedule
                </button>
                <button
                  onClick={() => handleDelete(draft.id)}
                  className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 text-xs font-medium px-4 py-2 rounded-lg transition-colors border border-rose-500/20"
                >
                  ✗ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}