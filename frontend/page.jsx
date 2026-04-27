"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import AppShell from "@/components/AppShell";
import { fetchTrends } from "@/lib/api";

const SOURCE_COLORS = {
"X / Twitter": "var(--accent2)",
"Hacker News": "var(--amber)",
"Dev.to": "var(--green)",
"Google News": "var(--blue)",
"Newsdata": "var(--pink)",
};

const SOURCE_ICONS = {
"X / Twitter": "𝕏",
"Hacker News": "▲",
"Dev.to": "DEV",
"Google News": "G",
"Newsdata": "N",
};

const TAG_ICONS = {
ai: "AI",
saas: "SaaS",
startup: "Startup",
tech: "Tech",
finance: "Finance",
marketing: "Marketing",
content: "Content",
design: "Design",
news: "News",
default: "○",
};

const FREE_SOURCES = [
{ name: "snscrape", color: "var(--accent2)", note: "X/Twitter · no key needed · pip install snscrape" },
{ name: "Hacker News", color: "var(--amber)", note: "official JSON API · no key needed" },
{ name: "Dev.to", color: "var(--green)", note: "public REST API · no key needed" },
{ name: "Google News", color: "var(--blue)", note: "public RSS · no key needed" },
{ name: "Newsdata.io", color: "var(--pink)", note: "free tier 200 req/day · NEWSDATA_API_KEY in .env (optional)" },
];

export default function TrendsPage() {
const router = useRouter();
const [trends, setTrends] = useState([]);
const [loading, setLoading] = useState(false);
const [lastFetch, setLastFetch] = useState(null);

const handleFetch = async () => {
setLoading(true);
try {
const data = await fetchTrends();
setTrends(Array.isArray(data?.trends) ? data.trends : []);
setLastFetch(new Date().toLocaleTimeString());
toast.success(`${data?.count || 0} trends fetched`);
} catch (e) {
const msg = e?.response?.data?.detail || e.message;
if (msg?.includes("Identity not found")) {
toast.error("Save your identity profile first");
router.push("/");
} else {
toast.error("Trend fetch failed: " + msg);
}
} finally {
setLoading(false);
}
};

const useTrend = (title) => {
sessionStorage.setItem("prefill_topic", title);
router.push("/generate");
toast.success("Trend loaded → Generate");
};

const getSourceColor = (source) => {
const key = Object.keys(SOURCE_COLORS).find((k) =>
(source || "").includes(k)
);
return key ? SOURCE_COLORS[key] : "var(--accent2)";
};

const getSourceIcon = (source) => {
const key = Object.keys(SOURCE_ICONS).find((k) =>
(source || "").includes(k)
);
return key ? SOURCE_ICONS[key] : "◎";
};

return ( <AppShell>
<div style={{ padding: 32, maxWidth: 860, animation: "fadeUp .3s ease" }}>
<div style={{ marginBottom: 28 }}>
<h1 style={{ fontSize: 28, fontWeight: 800, letterSpacing: "-1px" }}>
Trend <span style={{ color: "var(--accent2)" }}>Engine</span> </h1>
<p
style={{
fontSize: 12,
color: "var(--muted)",
fontFamily: "var(--font-mono)",
marginTop: 6,
}}
>
// snscrape + hacker_news + dev.to + google_news + newsdata.io → all free </p> </div>

```
    <div
      style={{
        background: "var(--surface)",
        border: "1px solid var(--border)",
        borderRadius: 12,
        padding: "16px 18px",
        marginBottom: 20,
      }}
    >
      <div
        style={{
          fontSize: 10,
          fontFamily: "var(--font-mono)",
          color: "var(--accent)",
          textTransform: "uppercase",
          letterSpacing: 1,
          marginBottom: 12,
        }}
      >
        Data sources — all free, no Reddit API needed
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {FREE_SOURCES.map((s) => (
          <div
            key={s.name}
            style={{ display: "flex", alignItems: "center", gap: 12 }}
          >
            <div
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: s.color,
                flexShrink: 0,
              }}
            />
            <span
              style={{
                fontSize: 12,
                fontWeight: 600,
                color: "var(--text)",
                minWidth: 100,
              }}
            >
              {s.name}
            </span>
            <span
              style={{
                fontSize: 11,
                fontFamily: "var(--font-mono)",
                color: "var(--muted)",
              }}
            >
              {s.note}
            </span>
          </div>
        ))}
      </div>
    </div>

    <div
      style={{
        display: "flex",
        gap: 12,
        alignItems: "center",
        marginBottom: 24,
      }}
    >
      <button
        className="btn btn-primary"
        onClick={handleFetch}
        disabled={loading}
      >
        {loading ? (
          <>
            <span className="spinner" /> Fetching trends...
          </>
        ) : (
          "◎ Fetch Trends"
        )}
      </button>
      {lastFetch && (
        <span
          style={{
            fontSize: 11,
            fontFamily: "var(--font-mono)",
            color: "var(--muted)",
          }}
        >
          last fetched: {lastFetch}
        </span>
      )}
    </div>

    {trends.length === 0 && !loading && (
      <div
        style={{
          textAlign: "center",
          padding: "60px 0",
          color: "var(--muted)",
          fontFamily: "var(--font-mono)",
          fontSize: 13,
        }}
      >
        No trends yet — click Fetch Trends.
        <br />
        <span style={{ fontSize: 11, color: "var(--muted2)" }}>
          Works out of the box. Optionally add NEWSDATA_API_KEY for more
          results.
        </span>
      </div>
    )}

    {trends.map((t, i) => {
      const tagKey = (t.tag || "").toLowerCase();
      const icon = TAG_ICONS[tagKey] || TAG_ICONS.default;
      const srcColor = getSourceColor(t.source);
      const srcIcon = getSourceIcon(t.source);
      const relevance = Math.round((t.relevance_score || 0.8) * 100);

      return (
        <div
          key={i}
          onClick={() => useTrend(t.title)}
          style={{
            background: "var(--surface2)",
            border: "1px solid var(--border2)",
            borderRadius: 12,
            padding: 16,
            marginBottom: 10,
            display: "flex",
            alignItems: "flex-start",
            gap: 14,
            cursor: "pointer",
            transition: "border-color .15s",
            animation: `fadeUp .3s ease ${i * 0.04}s both`,
          }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.borderColor = "var(--accent)")
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.borderColor = "var(--border2)")
          }
        >
          <div
            style={{
              width: 42,
              height: 42,
              borderRadius: 10,
              flexShrink: 0,
              background: "var(--surface)",
              border: "1px solid var(--border2)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 13,
              fontWeight: 700,
              color: srcColor,
              fontFamily: "var(--font-mono)",
            }}
          >
            {srcIcon}
          </div>

          <div style={{ flex: 1 }}>
            <div
              style={{
                fontSize: 10,
                fontFamily: "var(--font-mono)",
                color: srcColor,
                marginBottom: 4,
              }}
            >
              {t.source}
            </div>
            <div
              style={{
                fontSize: 14,
                fontWeight: 600,
                color: "var(--text)",
                marginBottom: 8,
                lineHeight: 1.4,
              }}
            >
              {t.title}
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                flexWrap: "wrap",
              }}
            >
              <span className="badge badge-purple">
                {t.tag || "general"}
              </span>
              <span
                style={{
                  fontSize: 11,
                  fontFamily: "var(--font-mono)",
                  color: "var(--muted)",
                }}
              >
                {relevance}% match
              </span>
              <span
                style={{
                  fontSize: 11,
                  fontFamily: "var(--font-mono)",
                  color: "var(--muted2)",
                }}
              >
                · click to generate →
              </span>
            </div>
          </div>

          <div style={{ width: 56, flexShrink: 0 }}>
            <div
              style={{
                fontSize: 10,
                fontFamily: "var(--font-mono)",
                color: "var(--muted)",
                marginBottom: 4,
                textAlign: "right",
              }}
            >
              {relevance}%
            </div>
            <div className="progress">
              <div
                className="progress-fill"
                style={{ width: `${relevance}%` }}
              />
            </div>
          </div>
        </div>
      );
    })}
  </div>
</AppShell>


);
}
