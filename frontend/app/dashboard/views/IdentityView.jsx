// "use client";

// import { useState, useEffect } from "react";
// import { createClient } from "../../lib/supabase";

// export default function IdentityView({ user }) {
//   const supabase = createClient();
//   const [loading, setLoading] = useState(false);
//   const [saving, setSaving] = useState(false);
//   const [message, setMessage] = useState({ text: "", type: "" });

//   const [profile, setProfile] = useState({
//     name: user?.user_metadata?.full_name || "",
//     age: "",
//     domain: "",
//     role: "",
//     qualification: "",
//     journey: "",
//     interests: "",
//     hobbies: "",
//     achievements: "",
//     tones: []
//   });

//   const availableTones = ["Analytical", "Bold", "Witty", "Formal", "Conversational", "Inspirational", "Technical", "Storytelling"];

//   useEffect(() => {
//     async function fetchProfile() {
//       setLoading(true);
//       const { data, error } = await supabase
//         .from('identities')
//         .select('*')
//         .eq('user_id', user.id)
//         .single();

//       if (data) {
//         setProfile({
//           name: data.name || profile.name,
//           age: data.age || "",
//           domain: data.domain || "",
//           role: data.role || "",
//           qualification: data.qualification || "",
//           journey: data.journey || "",
//           interests: data.interests || "",
//           hobbies: data.hobbies || "",
//           achievements: data.achievements || "",
//           tones: data.tones || []
//         });
//       }
//       setLoading(false);
//     }
//     fetchProfile();
//   }, [user.id, supabase, profile.name]);

//   const handleChange = (e) => {
//     setProfile({ ...profile, [e.target.name]: e.target.value });
//   };

//   const toggleTone = (tone) => {
//     if (profile.tones.includes(tone)) {
//       setProfile({ ...profile, tones: profile.tones.filter(t => t !== tone) });
//     } else {
//       setProfile({ ...profile, tones: [...profile.tones, tone] });
//     }
//   };

//   const handleSave = async () => {
//     setSaving(true);
//     setMessage({ text: "Saving and vectorizing profile...", type: "info" });

//     try {
//       const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
//       const response = await fetch(`${API_URL}/api/identity/save`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           user_id: user.id,
//           ...profile
//         })
//       });

//       const data = await response.json();

//       if (response.ok) {
//         setMessage({ text: "✓ Identity successfully vectorized and saved!", type: "success" });
//       } else {
//         setMessage({ text: data.detail || "Failed to save identity", type: "error" });
//       }
//     } catch (error) {
//       setMessage({ text: "Network error: Make sure FastAPI backend is running on :8000", type: "error" });
//     } finally {
//       setSaving(false);
//       setTimeout(() => setMessage({ text: "", type: "" }), 5000);
//     }
//   };

//   if (loading) return <div>Loading profile...</div>;

//   return (
//     <>
//       <div className="mb-8">
//         <h2 className="text-2xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-primary)] mb-2">
//           Phase 1 — Identity Setup
//         </h2>
//         <p className="text-[var(--color-text-secondary)]">Your profile is vectorized into Supabase pgvector. Every post is generated from this core knowledge.</p>
//       </div>

//       {message.text && (
//         <div className={`p-4 rounded-xl mb-6 text-sm flex items-center gap-3 ${
//           message.type === 'success' ? 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-400' :
//           message.type === 'error' ? 'bg-rose-500/10 border border-rose-500/20 text-rose-400' :
//           'bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/10 border border-[var(--color-accent-primary)]/20 text-[var(--color-accent-primary)]'
//         }`}>
//           {message.text}
//         </div>
//       )}

//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-6">
//           <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Personal Info</h3>

//           <div className="space-y-4">
//             <div>
//               <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Full Name</label>
//               <input type="text" name="name" value={profile.name} onChange={handleChange} className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
//             </div>

//             <div className="grid grid-cols-2 gap-4">
//               <div>
//                 <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Age</label>
//                 <input type="number" name="age" value={profile.age} onChange={handleChange} className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
//               </div>
//               <div>
//                 <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Location / Timezone</label>
//                 <input type="text" className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
//               </div>
//             </div>

//             <div>
//               <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Primary Domain (Important)</label>
//               <input type="text" name="domain" value={profile.domain} onChange={handleChange} placeholder="e.g. AI / Machine Learning / Startups" className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
//             </div>
//           </div>
//         </div>

//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-6">
//           <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Professional Journey</h3>

//           <div className="space-y-4">
//              <div>
//               <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Current Role</label>
//               <input type="text" name="role" value={profile.role} onChange={handleChange} placeholder="Founder / Engineer / Creator" className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
//             </div>
//             <div>
//               <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Life Journey / Milestones (Affects storytelling)</label>
//               <textarea name="journey" value={profile.journey} onChange={handleChange} rows={4} placeholder="Summarize key milestones in your life..." className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors resize-none"></textarea>
//             </div>
//           </div>
//         </div>

//         <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-6 lg:col-span-2">
//           <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Voice & Tone Calibration</h3>

//           <div className="mb-5">
//             <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-3">Select your posting tones</label>
//             <div className="flex flex-wrap gap-2">
//               {availableTones.map(tone => (
//                 <button
//                   key={tone}
//                   onClick={() => toggleTone(tone)}
//                   className={`px-3 py-1.5 rounded-full text-xs transition-colors border ${
//                     profile.tones.includes(tone)
//                       ? "bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/20 border-[var(--color-accent-primary)]/50 text-[var(--color-accent-primary)]"
//                       : "bg-[var(--color-bg-card)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-secondary)]"
//                   }`}
//                 >
//                   {tone}
//                 </button>
//               ))}
//             </div>
//           </div>

//           <div className="flex justify-end pt-4 border-t border-[var(--color-border)] mt-6">
//             <button
//               onClick={handleSave}
//               disabled={saving}
//               className="bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] disabled:opacity-50 text-[var(--color-text-primary)] font-medium px-6 py-2.5 rounded-xl transition-colors shadow-[0_0_15px_rgba(79,70,229,0.2)]"
//             >
//               {saving ? "Vectorizing..." : "Save Identity to pgvector"}
//             </button>
//           </div>
//         </div>
//       </div>
//     </>
//   );
// }
"use client";

import { useState, useEffect } from "react";
import { createClient } from "../../lib/supabase";

export default function IdentityView({ user }) {
  const supabase = createClient();
  const [loading, setLoading] = useState(true);  // true by default — skeleton shows first
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ text: "", type: "" });
  const [contentPlan, setContentPlan] = useState([]);
  const [showPlanModal, setShowPlanModal] = useState(false);
  const [schedulingAll, setSchedulingAll] = useState(false);
  const [isExisting, setIsExisting] = useState(false); // tracks if identity already exists in DB

  const [profile, setProfile] = useState({
    name: user?.user_metadata?.full_name || "",
    age: "",
    domain: "",
    role: "",
    qualification: "",
    journey: "",
    interests: "",
    hobbies: "",
    achievements: "",
    tones: [],
    // Content Preferences
    content_types: [],
    posting_frequency: "",
    preferred_post_length: "",
    content_language: "English",
  });

  const availableTones = [
    "Analytical", "Bold", "Witty", "Formal",
    "Conversational", "Inspirational", "Technical", "Storytelling",
  ];

  const availableContentTypes = [
    "Educational", "Behind-the-scenes", "Promotional", "Storytelling",
    "Tips & Tricks", "Carousel", "Poll", "Meme",
  ];

  const postingFrequencyOptions = [
    { value: "", label: "Select frequency…" },
    { value: "daily", label: "Daily" },
    { value: "3x_per_week", label: "3× per week" },
    { value: "weekly", label: "Weekly" },
  ];

  const postLengthOptions = [
    { value: "", label: "Select length…" },
    { value: "short", label: "Short (< 100 words)" },
    { value: "medium", label: "Medium" },
    { value: "long", label: "Long-form" },
  ];

  // ── Helper: get the current Supabase session access token ──
  const getAccessToken = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  };

  // ── Fetch existing profile on mount via authenticated API ──
  useEffect(() => {
    async function fetchProfile() {
      setLoading(true);
      try {
        const token = await getAccessToken();
        if (!token) { setLoading(false); return; }

        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        const resp = await fetch(`${API_URL}/api/identity/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (resp.ok) {
          const data = await resp.json();
          if (data) {
            setIsExisting(true);
            setProfile({
              name: data.name || user?.user_metadata?.full_name || "",
              age: data.age || "",
              domain: data.domain || "",
              role: data.role || "",
              qualification: data.qualification || "",
              journey: data.journey || "",
              interests: data.interests || "",
              hobbies: data.hobbies || "",
              achievements: data.achievements || "",
              tones: data.tones || [],
              content_types: data.content_types || [],
              posting_frequency: data.posting_frequency || "",
              preferred_post_length: data.preferred_post_length || "",
              content_language: data.content_language || "English",
            });
          }
        }
      } catch (err) {
        console.error("Failed to fetch identity:", err);
      }
      setLoading(false);
    }

    if (user?.id) fetchProfile();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user.id]);

  const handleChange = e =>
    setProfile(prev => ({ ...prev, [e.target.name]: e.target.value }));

  const toggleTone = tone =>
    setProfile(prev => ({
      ...prev,
      tones: prev.tones.includes(tone)
        ? prev.tones.filter(t => t !== tone)
        : [...prev.tones, tone],
    }));

  const toggleContentType = type =>
    setProfile(prev => ({
      ...prev,
      content_types: prev.content_types.includes(type)
        ? prev.content_types.filter(t => t !== type)
        : [...prev.content_types, type],
    }));

  const handleSave = async () => {
    setSaving(true);
    setMessage({
      text: isExisting ? "Updating identity…" : "Saving and vectorizing profile…",
      type: "info",
    });

    try {
      const token = await getAccessToken();
      if (!token) {
        setMessage({ text: "Session expired — please log in again", type: "error" });
        setSaving(false);
        return;
      }

      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_URL}/api/identity/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(profile),  // user_id comes from JWT, not body
      });

      const data = await response.json();

      if (response.ok) {
        if (data.is_first_save && data.content_plan?.length > 0) {
          // First-time save — show the content plan modal
          setContentPlan(data.content_plan);
          setShowPlanModal(true);
          setMessage({ text: "✓ Identity saved! Your 3-day content plan is ready.", type: "success" });
        } else {
          // Update — just show a toast, no content plan re-generation
          setMessage({ text: "✓ Identity updated!", type: "success" });
        }
        setIsExisting(true);
      } else if (response.status === 401) {
        setMessage({ text: "Session expired — please log in again", type: "error" });
      } else {
        setMessage({ text: data.detail || "Failed to save identity", type: "error" });
      }
    } catch {
      setMessage({ text: "Network error — make sure FastAPI backend is running on :8000", type: "error" });
    } finally {
      setSaving(false);
      setTimeout(() => setMessage({ text: "", type: "" }), 8000);
    }
  };

  // ── Content Plan actions ────────────────────────────────────────────────
  const handleApproveDraft = async (draftId) => {
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const resp = await fetch(`${API_URL}/api/generate/approve/${draftId}`, { method: "PATCH" });
      if (resp.ok) {
        setContentPlan(prev =>
          prev.map(d => d.draft_id === draftId ? { ...d, status: "approved" } : d)
        );
      }
    } catch (err) {
      console.error("Failed to approve draft:", err);
    }
  };

  const handleScheduleAll = async () => {
    const approvedIds = contentPlan.filter(d => d.status === "approved").map(d => d.draft_id);
    if (approvedIds.length === 0) return;

    setSchedulingAll(true);
    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const resp = await fetch(`${API_URL}/api/schedule/week-plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: user.id, approved_draft_ids: approvedIds }),
      });
      if (resp.ok) {
        setContentPlan(prev =>
          prev.map(d => approvedIds.includes(d.draft_id) ? { ...d, status: "scheduled" } : d)
        );
        setMessage({ text: `✓ ${approvedIds.length} posts scheduled!`, type: "success" });
        setTimeout(() => setMessage({ text: "", type: "" }), 5000);
      }
    } catch (err) {
      console.error("Failed to schedule:", err);
    } finally {
      setSchedulingAll(false);
    }
  };

  const handleEditDraft = (draftId) => {
    // Navigate to the review/edit view with the draft pre-selected
    window.location.hash = "review";
  };

  if (loading) return (
    <div className="animate-pulse space-y-6">
      <div>
        <div className="h-7 w-64 bg-[var(--color-bg-card)] rounded-lg mb-2" />
        <div className="h-4 w-96 bg-[var(--color-bg-card)] rounded-lg" />
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[1, 2].map(i => (
          <div key={i} className="glass-card border border-[var(--color-border)] rounded-xl p-6 space-y-4">
            <div className="h-4 w-32 bg-[var(--color-bg-card)] rounded" />
            <div className="space-y-3">
              <div className="h-9 bg-[var(--color-bg-card)] rounded-lg" />
              <div className="grid grid-cols-2 gap-4">
                <div className="h-9 bg-[var(--color-bg-card)] rounded-lg" />
                <div className="h-9 bg-[var(--color-bg-card)] rounded-lg" />
              </div>
              <div className="h-9 bg-[var(--color-bg-card)] rounded-lg" />
            </div>
          </div>
        ))}
      </div>
      <div className="glass-card border border-[var(--color-border)] rounded-xl p-6">
        <div className="h-4 w-48 bg-[var(--color-bg-card)] rounded mb-4" />
        <div className="flex gap-2">
          {[1,2,3,4,5].map(i => <div key={i} className="h-7 w-20 bg-[var(--color-bg-card)] rounded-full" />)}
        </div>
      </div>
    </div>
  );

  return (
    <>
      <div className="mb-8">
        <h2 className="text-2xl font-[family-name:var(--font-heading)] font-bold text-[var(--color-text-primary)] mb-2">
          Phase 1 — Identity Setup
        </h2>
        <p className="text-[var(--color-text-secondary)]">
          Your profile is vectorized into Supabase pgvector. Every post is generated from this core knowledge.
        </p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-xl mb-6 text-sm flex items-center gap-3 ${message.type === "success" ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400" :
            message.type === "error" ? "bg-rose-500/10 border border-rose-500/20 text-rose-400" :
              "bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/10 border border-[var(--color-accent-primary)]/20 text-[var(--color-accent-primary)]"
          }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Personal Info */}
        <div className="glass-card border border-[var(--color-border)] rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Personal Info</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Full Name</label>
              <input type="text" name="name" value={profile.name} onChange={handleChange}
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Age</label>
                <input type="number" name="age" value={profile.age} onChange={handleChange}
                  className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Qualification</label>
                <input type="text" name="qualification" value={profile.qualification} onChange={handleChange}
                  className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
              </div>
            </div>
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Primary Domain</label>
              <input type="text" name="domain" value={profile.domain} onChange={handleChange}
                placeholder="e.g. AI / Machine Learning / Startups"
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Interests</label>
              <input type="text" name="interests" value={profile.interests} onChange={handleChange}
                placeholder="e.g. AI safety, indie hacking, photography"
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Hobbies</label>
              <input type="text" name="hobbies" value={profile.hobbies} onChange={handleChange}
                placeholder="e.g. chess, running, reading"
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
            </div>
          </div>
        </div>

        {/* Professional Journey */}
        <div className="glass-card border border-[var(--color-border)] rounded-xl p-6">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Professional Journey</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Current Role</label>
              <input type="text" name="role" value={profile.role} onChange={handleChange}
                placeholder="Founder / Engineer / Creator"
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors" />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Life Journey / Milestones</label>
              <textarea name="journey" value={profile.journey} onChange={handleChange} rows={4}
                placeholder="Summarize key milestones in your life…"
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors resize-none" />
            </div>
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">Achievements</label>
              <textarea name="achievements" value={profile.achievements} onChange={handleChange} rows={3}
                placeholder="Awards, milestones, proud moments…"
                className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors resize-none" />
            </div>
          </div>
        </div>

        {/* Tone calibration */}
        <div className="bg-[var(--color-brown)] border border-[var(--color-border)] rounded-xl p-6 lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Voice & Tone Calibration</h3>
          <div className="mb-5">
            <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-3">
              Select your posting tones
            </label>
            <div className="flex flex-wrap gap-2">
              {availableTones.map(tone => (
                <button key={tone} onClick={() => toggleTone(tone)}
                  className={`px-3 py-1.5 rounded-full text-xs transition-colors border ${profile.tones.includes(tone)
                      ? "bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/20 border-[var(--color-accent-primary)]/50 text-[var(--color-accent-primary)]"
                      : "bg-[var(--color-bg-card)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-secondary)]"
                    }`}
                >
                  {tone}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Content Preferences */}
        <div className="glass-card border border-[var(--color-border)] rounded-xl p-6 lg:col-span-2">
          <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Content Preferences</h3>
          <div className="space-y-6">
            {/* Content Types — multi-select pills */}
            <div>
              <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-3">
                Content Types
              </label>
              <div className="flex flex-wrap gap-2">
                {availableContentTypes.map(type => (
                  <button key={type} onClick={() => toggleContentType(type)}
                    className={`px-3 py-1.5 rounded-full text-xs transition-colors border ${profile.content_types.includes(type)
                        ? "bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/20 border-[var(--color-accent-primary)]/50 text-[var(--color-accent-primary)]"
                        : "bg-[var(--color-bg-card)] border-[var(--color-border)] text-[var(--color-text-secondary)] hover:border-[var(--color-border-secondary)]"
                      }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Posting Frequency */}
              <div>
                <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                  Posting Frequency
                </label>
                <select
                  name="posting_frequency"
                  value={profile.posting_frequency}
                  onChange={handleChange}
                  className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors appearance-none cursor-pointer"
                >
                  {postingFrequencyOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              {/* Preferred Post Length */}
              <div>
                <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                  Preferred Post Length
                </label>
                <select
                  name="preferred_post_length"
                  value={profile.preferred_post_length}
                  onChange={handleChange}
                  className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors appearance-none cursor-pointer"
                >
                  {postLengthOptions.map(opt => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              </div>

              {/* Content Language */}
              <div>
                <label className="block text-[11px] font-medium text-[var(--color-text-muted)] uppercase tracking-wider mb-1">
                  Content Language
                </label>
                <input
                  type="text"
                  name="content_language"
                  value={profile.content_language}
                  onChange={handleChange}
                  placeholder="English"
                  className="w-full bg-[var(--color-bg-card)] border border-[var(--color-border)] rounded-lg px-3 py-2 text-sm text-[var(--color-text-primary)] focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t border-[var(--color-border)] mt-6">
            <button onClick={handleSave} disabled={saving}
              className="bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] disabled:opacity-50 text-[var(--color-text-primary)] font-medium px-6 py-2.5 rounded-xl transition-colors shadow-[0_0_15px_rgba(79,70,229,0.2)]"
            >
              {saving ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-[var(--color-text-primary)] inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {isExisting ? "Updating…" : "Generating plan…"}
                </>
              ) : isExisting ? "Update Identity" : "Save & Generate Content Plan"}
            </button>
          </div>
        </div>
      </div>

      {/* ── Content Plan Modal ───────────────────────────────────────── */}
      {showPlanModal && contentPlan.length > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          {/* Backdrop */}
          <div className="absolute inset-0 bg-[var(--color-bg-primary)]/70 backdrop-blur-sm" onClick={() => setShowPlanModal(false)} />

          {/* Modal */}
          <div className="relative bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-2xl w-full max-w-3xl max-h-[85vh] overflow-hidden shadow-2xl shadow-indigo-500/10">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--color-border)]">
              <div>
                <h3 className="text-lg font-bold text-[var(--color-text-primary)]">Your 3-Day Content Plan</h3>
                <p className="text-xs text-[var(--color-text-muted)] mt-0.5">Review, approve, and schedule your generated drafts</p>
              </div>
              <button onClick={() => setShowPlanModal(false)}
                className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] transition-colors p-1 rounded-lg hover:bg-[var(--color-bg-card)]"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
              </button>
            </div>

            {/* Body */}
            <div className="overflow-y-auto px-6 py-4 space-y-4" style={{ maxHeight: "calc(85vh - 140px)" }}>
              {contentPlan.map((draft, idx) => {
                const isApproved = draft.status === "approved";
                const isScheduled = draft.status === "scheduled";
                const scheduledDate = draft.scheduled_at ? new Date(draft.scheduled_at) : null;

                return (
                  <div key={draft.draft_id || idx}
                    className={`glass-card border rounded-xl p-5 transition-all ${
                      isScheduled ? "border-emerald-500/30 bg-emerald-500/5" :
                      isApproved ? "border-[var(--color-accent-primary)]/30 bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/5" :
                      "border-[var(--color-border)] hover:border-[var(--color-border)]"
                    }`}
                  >
                    {/* Day header */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <span className="flex items-center justify-center w-8 h-8 rounded-lg bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/20 text-[var(--color-accent-primary)] text-sm font-bold">
                          {draft.day || idx + 1}
                        </span>
                        <div>
                          <h4 className="text-sm font-semibold text-[var(--color-text-primary)]">{draft.topic}</h4>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--color-bg-card)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
                              {draft.content_type}
                            </span>
                            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--color-bg-card)] text-[var(--color-text-secondary)] border border-[var(--color-border)]">
                              {draft.platform}
                            </span>
                            {scheduledDate && (
                              <span className="text-[10px] text-[var(--color-text-muted)]">
                                {scheduledDate.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" })} at 9:00 AM
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* Status badge */}
                      {isScheduled ? (
                        <span className="text-[10px] px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-medium">
                          ✓ Scheduled
                        </span>
                      ) : isApproved ? (
                        <span className="text-[10px] px-2.5 py-1 rounded-full bg-[var(--color-accent-primary)] text-[var(--color-text-primary)]/20 text-[var(--color-accent-primary)] border border-[var(--color-accent-primary)]/30 font-medium">
                          ✓ Approved
                        </span>
                      ) : (
                        <span className="text-[10px] px-2.5 py-1 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/30 font-medium">
                          Pending
                        </span>
                      )}
                    </div>

                    {/* Caption preview */}
                    <p className="text-sm text-gray-300 leading-relaxed mb-3 line-clamp-4">
                      {draft.caption}
                    </p>

                    {/* Hashtags */}
                    {draft.hashtags && draft.hashtags.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 mb-3">
                        {draft.hashtags.map((tag, i) => (
                          <span key={i} className="text-[10px] text-[var(--color-accent-primary)]/70">#{tag}</span>
                        ))}
                      </div>
                    )}

                    {/* Actions */}
                    {!isScheduled && (
                      <div className="flex items-center gap-2 pt-3 border-t border-[var(--color-border)]">
                        {!isApproved && (
                          <button
                            onClick={() => handleApproveDraft(draft.draft_id)}
                            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] text-[var(--color-text-primary)] transition-colors"
                          >
                            Approve
                          </button>
                        )}
                        <button
                          onClick={() => handleEditDraft(draft.draft_id)}
                          className="px-3 py-1.5 text-xs font-medium rounded-lg bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] text-gray-300 transition-colors border border-[var(--color-border)]"
                        >
                          Edit
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-[var(--color-border)] bg-[var(--color-bg-primary)]">
              <p className="text-xs text-[var(--color-text-muted)]">
                {contentPlan.filter(d => d.status === "approved").length} of {contentPlan.length} approved
              </p>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setShowPlanModal(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg bg-[var(--color-bg-card)] hover:bg-[var(--color-bg-card)] text-gray-300 transition-colors border border-[var(--color-border)]"
                >
                  Close
                </button>
                <button
                  onClick={handleScheduleAll}
                  disabled={schedulingAll || contentPlan.filter(d => d.status === "approved").length === 0}
                  className="px-4 py-2 text-xs font-medium rounded-xl bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] hover:bg-[var(--color-accent-primary)] text-[var(--color-text-primary)] disabled:opacity-40 disabled:cursor-not-allowed text-[var(--color-text-primary)] transition-colors shadow-[0_0_15px_rgba(79,70,229,0.2)]"
                >
                  {schedulingAll ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-1.5 h-3 w-3 text-[var(--color-text-primary)] inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Scheduling…
                    </>
                  ) : (
                    `Schedule All Approved (${contentPlan.filter(d => d.status === "approved").length})`
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
