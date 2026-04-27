// "use client";

// import { useState, useEffect } from "react";

// export default function GenerateView({ user }) {
//   const [topic, setTopic] = useState("");
//   const [loading, setLoading] = useState(false);
//   const [results, setResults] = useState([]);

//   const platforms = [
//     { id: "linkedin", label: "LinkedIn Post", selected: true },
//     { id: "twitter", label: "X Thread", selected: true },
//     { id: "instagram", label: "IG Carousel", selected: true }
//   ];

//   useEffect(() => {
//     // Check if passed from Trends
//     const prefill = sessionStorage.getItem("prefill_topic");
//     if (prefill) {
//       setTopic(prefill);
//       sessionStorage.removeItem("prefill_topic");
//     }
//   }, []);

//   const handleGenerate = async () => {
//     if (!topic) return;
//     setLoading(true);
//     try {
//       const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
//       const res = await fetch(`${API_URL}/api/generate/`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({
//           user_id: user.id,
//           topic: topic,
//           platform: "all",
//           content_type: "post"
//         })
//       });
//       const data = await res.json();
//       setResults(data);
//     } catch (e) {
//       console.error(e);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <>
//       <div className="mb-8">
//         <h2 className="text-2xl font-heading font-bold text-foreground mb-2">
//           Phase 2B — Generation Core
//         </h2>
//         <p className="text-(--color-text-secondary)">GPT-4o generation with identity context injection.</p>
//       </div>

//       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
//         <div className="lg:col-span-1 space-y-6">
//           <div className="bg-[var(--color-brown)] border border-(--color-border) rounded-xl p-6">
//             <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">Generator Settings</h3>

//             <div className="space-y-5">
//               <div>
//                 <label className="block text-[11px] font-medium text-(--color-text-muted) uppercase tracking-wider mb-2">Topic or Idea</label>
//                 <textarea 
//                   value={topic}
//                   onChange={e => setTopic(e.target.value)}
//                   rows={3}
//                   className="w-full bg-[var(--color-bg-card)] border border-(--color-border) rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors resize-none"
//                   placeholder="What do you want to talk about?"
//                 ></textarea>
//               </div>

//               <div>
//                 <label className="block text-[11px] font-medium text-(--color-text-muted) uppercase tracking-wider mb-2">Platforms</label>
//                 <div className="flex flex-wrap gap-2">
//                   {platforms.map(p => (
//                     <div key={p.id} className="px-3 py-1.5 rounded-lg text-[11px] font-medium bg-[var(--color-accent-primary)] text-foreground/20 text-[var(--color-accent-primary)] border border-[var(--color-accent-primary)]/30">
//                       {p.label}
//                     </div>
//                   ))}
//                 </div>
//               </div>

//               <div>
//                 <label className="block text-[11px] font-medium text-(--color-text-muted) uppercase tracking-wider mb-2">Model</label>
//                 <select className="w-full bg-[var(--color-bg-card)] border border-(--color-border) rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-[var(--color-accent-primary)] transition-colors">
//                   <option>OpenAI — gpt-4o-mini</option>
//                 </select>
//               </div>

//               <button 
//                 onClick={handleGenerate}
//                 disabled={loading || !topic}
//                 className="w-full bg-[var(--color-accent-primary)] text-foreground hover:bg-[var(--color-accent-primary)] text-foreground disabled:opacity-50 text-foreground font-medium py-3 rounded-xl transition-colors shadow-[0_0_15px_rgba(79,70,229,0.2)]"
//               >
//                 {loading ? "Generating..." : "Generate AI Content"}
//               </button>
//             </div>
//           </div>
//         </div>

//         <div className="lg:col-span-2 space-y-6">
//           {loading && (
//             <div className="bg-[var(--color-brown)] border border-(--color-border) rounded-xl p-6 text-center text-sm text-(--color-text-secondary) h-full flex flex-col justify-center min-h-[300px]">
//                <div className="w-8 h-8 border-2 border-t-transparent border-[var(--color-accent-primary)] rounded-full animate-spin mx-auto mb-4"></div>
//                Retrieving identity context from pgvector...<br/>
//                Generating perfect drafts across platforms...
//             </div>
//           )}

//           {!loading && results.length === 0 && (
//             <div className="bg-[var(--color-brown)] border border-(--color-border) border-dashed rounded-xl p-6 text-center text-sm text-(--color-text-muted) h-full flex flex-col justify-center min-h-[300px]">
//               Ready to generate.<br/>Your drafts will appear here.
//             </div>
//           )}

//           {!loading && results.map((res, i) => (
//             <div key={i} className="bg-[var(--color-brown)] border border-(--color-border) rounded-xl p-6 relative group animate-[fadeUp_0.4s_ease_both]" style={{animationDelay: `${i * 0.1}s`}}>
//               <div className="flex justify-between items-center mb-4">
//                 <div className="flex items-center gap-3">
//                   <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
//                     res.platform === 'linkedin' ? 'bg-blue-500/20 text-blue-400' :
//                     res.platform === 'twitter' ? 'bg-gray-500/20 text-gray-300' :
//                     'bg-pink-500/20 text-pink-400'
//                   }`}>
//                     {res.platform}
//                   </span>
//                   <span className="text-xs text-(--color-text-muted)">&bull; Draft Auto-Saved</span>
//                 </div>
//                 <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
//                   <button className="text-xs text-(--color-text-secondary) hover:text-foreground bg-[var(--color-bg-card)] px-2 py-1 rounded">Edit</button>
//                   <button className="text-xs text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 px-2 py-1 rounded">Approve</button>
//                 </div>
//               </div>

//               <div className="bg-[var(--color-bg-card)] rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap leading-relaxed border border-[var(--color-border)]">
//                 {res.content}
//               </div>

//               {res.platform === 'instagram' && res.carousel_slides && (
//                 <div className="mt-4 flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
//                   {res.carousel_slides.map((slide, j) => (
//                     <div key={j} className="w-32 h-40 shrink-0 bg-[var(--color-bg-card)] border border-(--color-border) rounded-lg flex flex-col items-center justify-center p-3 text-center relative">
//                       <span className="absolute top-2 right-2 text-[10px] text-gray-600">{slide.slide || j+1}</span>
//                       <div className="text-[10px] font-bold text-foreground mb-2 leading-tight">{slide.title}</div>
//                       <div className="text-[9px] text-(--color-text-muted) leading-tight line-clamp-4">{slide.body}</div>
//                     </div>
//                   ))}
//                 </div>
//               )}
//             </div>
//           ))}
//         </div>
//       </div>
//     </>
//   );
// }
"use client";

import { useState, useEffect } from "react";

const CONTENT_TYPES = [
  { id: "post", label: "Standard Post" },
  { id: "story", label: "Personal Story" },
  { id: "opinion", label: "Hot Take" },
  { id: "educational", label: "Educational" },
  { id: "thread", label: "Thread" },
];

export default function GenerateView({ user }) {
  const [topic, setTopic] = useState("");
  const [contentType, setContentType] = useState("post");
  const [platform, setPlatform] = useState("all");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const prefill = sessionStorage.getItem("prefill_topic");
    if (prefill) {
      setTopic(prefill);
      sessionStorage.removeItem("prefill_topic");
    }
  }, []);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setError("");
    setResults([]);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: user.id,
          topic: topic.trim(),
          platform: platform,
          content_type: contentType,
        }),
      });

      const data = await res.json();

      if (!res.ok) {
        // Backend returned 4xx/5xx — data.detail has the error message
        setError(data?.detail || `Server error: ${res.status}`);
        return;
      }

      // Ensure we always set an array — never let a non-array reach .map()
      if (Array.isArray(data)) {
        setResults(data);
      } else {
        setError("Unexpected response from server. Check backend logs.");
        console.error("Expected array, got:", data);
      }
    } catch (e) {
      setError("Network error — make sure the FastAPI backend is running on :8000");
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="mb-8">
        <h2 className="text-2xl font-heading font-bold text-foreground mb-2">
          Phase 2B — Generation Core
        </h2>
        <p className="text-(--color-text-secondary)">GPT-4o generation with identity context injection.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* ── Left panel — settings ── */}
        <div className="lg:col-span-1 space-y-6">
          <div className="glass-card border border-(--color-border) rounded-xl p-6">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-5">
              Generator Settings
            </h3>

            <div className="space-y-5">
              {/* Topic */}
              <div>
                <label className="block text-[11px] font-medium text-(--color-text-muted) uppercase tracking-wider mb-2">
                  Topic or Idea
                </label>
                <textarea
                  value={topic}
                  onChange={e => setTopic(e.target.value)}
                  rows={3}
                  className="w-full bg-(--color-bg-card) border border-(--color-border) rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-(--color-accent-primary) transition-colors resize-none"
                  placeholder="What do you want to talk about?"
                />
              </div>

              {/* Platform */}
              <div>
                <label className="block text-[11px] font-medium text-(--color-text-muted) uppercase tracking-wider mb-2">
                  Platform
                </label>
                <select
                  value={platform}
                  onChange={e => setPlatform(e.target.value)}
                  className="w-full bg-(--color-bg-card) border border-(--color-border) rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-(--color-accent-primary) transition-colors"
                >
                  <option value="all">All Platforms</option>
                  <option value="linkedin">LinkedIn</option>
                  <option value="twitter">X / Twitter</option>
                  <option value="instagram">Instagram Carousel</option>
                </select>
              </div>

              {/* Content type */}
              <div>
                <label className="block text-[11px] font-medium text-(--color-text-muted) uppercase tracking-wider mb-2">
                  Content Type
                </label>
                <div className="flex flex-wrap gap-2">
                  {CONTENT_TYPES.map(ct => (
                    <button
                      key={ct.id}
                      onClick={() => setContentType(ct.id)}
                      className={`px-3 py-1.5 rounded-lg text-[11px] font-medium border transition-colors ${contentType === ct.id
                        ? "bg-(--color-accent-primary) text-foreground border-(--color-accent-primary)/30"
                        : "bg-(--color-bg-card) text-(--color-text-secondary) border-(--color-border) hover:border-(--color-border-secondary)"
                        }`}
                    >
                      {ct.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Model */}
              <div>
                <label className="block text-[11px] font-medium text-(--color-text-muted) uppercase tracking-wider mb-2">
                  Model
                </label>
                <select className="w-full bg-(--color-bg-card) border border-(--color-border) rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:border-(--color-accent-primary) transition-colors">
                  <option>Gemini — 2.0 Flash</option>
                </select>
              </div>

              <button
                onClick={handleGenerate}
                disabled={loading || !topic.trim()}
                className="w-full bg-(--color-accent-primary) text-foreground hover:bg-(--color-accent-primary) disabled:opacity-50 font-medium py-3 rounded-xl transition-colors shadow-[0_0_15px_rgba(79,70,229,0.2)]"
              >
                {loading ? "Generating..." : "Generate AI Content"}
              </button>
            </div>
          </div>
        </div>

        {/* ── Right panel — results ── */}
        <div className="lg:col-span-2 space-y-6">
          {/* Loading state */}
          {loading && (
            <div className="glass-card border border-(--color-border) rounded-xl p-6 text-center text-sm text-(--color-text-secondary) flex flex-col justify-center min-h-75">
              <div className="w-8 h-8 border-2 border-t-transparent border-(--color-accent-primary) rounded-full animate-spin mx-auto mb-4" />
              Retrieving identity context from pgvector…
              <br />
              Generating drafts across platforms…
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl p-5 text-sm">
              <span className="font-semibold">Error: </span>{error}
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && results.length === 0 && (
            <div className="glass-card border border-(--color-border) border-dashed rounded-xl p-6 text-center text-sm text-(--color-text-muted) flex flex-col justify-center min-h-75">
              Ready to generate.
              <br />
              Your drafts will appear here.
            </div>
          )}

          {/* Results */}
          {!loading && results.map((res, i) => (
            <div
              key={i}
              className="glass-card border border-(--color-border) rounded-xl p-6 relative group"
              style={{ animationDelay: `${i * 0.1}s` }}
            >
              <div className="flex justify-between items-center mb-4">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${res.platform === "linkedin" ? "bg-blue-500/20 text-blue-400" :
                    res.platform === "twitter" ? "bg-gray-500/20 text-gray-300" :
                      "bg-pink-500/20 text-pink-400"
                    }`}>
                    {res.platform}
                  </span>
                  <span className="text-xs text-(--color-text-muted)">
                    {res.draft_id ? "• Draft Auto-Saved" : "• Not saved"}
                  </span>
                </div>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button className="text-xs text-(--color-text-secondary) hover:text-foreground bg-(--color-bg-card) px-2 py-1 rounded">
                    Edit
                  </button>
                  <button className="text-xs text-emerald-400 hover:text-emerald-300 bg-emerald-500/10 px-2 py-1 rounded">
                    Approve
                  </button>
                </div>
              </div>

              <div className="bg-(--color-bg-card) rounded-lg p-4 text-sm text-gray-300 whitespace-pre-wrap leading-relaxed border border-(--color-border)">
                {res.content}
              </div>

              {/* Instagram carousel preview */}
              {res.platform === "instagram" && Array.isArray(res.carousel_slides) && res.carousel_slides.length > 0 && (
                <div className="mt-4 flex gap-3 overflow-x-auto pb-2 scrollbar-hide">
                  {res.carousel_slides.map((slide, j) => (
                    <div
                      key={j}
                      className="w-32 h-40 shrink-0 bg-(--color-bg-card) border border-(--color-border) rounded-lg flex flex-col items-center justify-center p-3 text-center relative"
                    >
                      <span className="absolute top-2 right-2 text-[10px] text-gray-600">
                        {slide.slide || j + 1}
                      </span>
                      {slide.emoji && (
                        <div className="text-xl mb-1">{slide.emoji}</div>
                      )}
                      <div className="text-[10px] font-bold text-foreground mb-1 leading-tight">
                        {slide.title}
                      </div>
                      <div className="text-[9px] text-(--color-text-muted) leading-tight line-clamp-4">
                        {slide.body}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </>
  );
}