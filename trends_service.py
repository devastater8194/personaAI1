# import os
# import asyncio
# import logging
# import feedparser
# import httpx
# from typing import List, Dict
# from dotenv import load_dotenv

# load_dotenv()

# logger = logging.getLogger(__name__)

# NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")

# DOMAIN_KEYWORDS: Dict[str, List[str]] = {
#     "ai":         ["AI", "machine learning", "LLM", "GPT", "artificial intelligence"],
#     "saas":       ["SaaS", "startup", "product", "B2B", "software"],
#     "tech":       ["technology", "programming", "software", "developer", "coding"],
#     "startup":    ["startup", "founder", "fundraising", "YC", "venture"],
#     "finance":    ["investing", "stocks", "market", "fintech", "crypto"],
#     "marketing":  ["marketing", "growth", "SEO", "social media", "content"],
#     "content":    ["content creator", "viral", "LinkedIn", "Instagram", "personal brand"],
#     "design":     ["design", "UI", "UX", "Figma", "product design"],
#     "edtech":     ["education", "learning", "course", "edtech", "skills"],
#     "default":    ["technology", "startup", "AI", "innovation", "product"],
# }


# def get_keywords_for_domain(domain: str) -> List[str]:
#     d = domain.lower()
#     for key, kws in DOMAIN_KEYWORDS.items():
#         if key in d:
#             return kws
#     extra = [w.strip() for w in domain.replace("/", " ").split() if len(w) > 2]
#     return DOMAIN_KEYWORDS["default"] + extra[:3]


# # ── Hacker News ──────────────────────────────────────────────────────────────

# async def fetch_hackernews(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = [kw.lower() for kw in get_keywords_for_domain(domain)]

#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             top_resp = await client.get(
#                 "https://hacker-news.firebaseio.com/v0/topstories.json"
#             )
#             top_resp.raise_for_status()
#             top_ids = top_resp.json()[:50]

#             tasks = [
#                 client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
#                 for sid in top_ids
#             ]
#             responses = await asyncio.gather(*tasks, return_exceptions=True)

#             trends = []
#             for resp in responses:
#                 if isinstance(resp, Exception) or resp.status_code != 200:
#                     continue
#                 story = resp.json()
#                 if not story or story.get("type") != "story":
#                     continue
#                 title = (story.get("title") or "").lower()
#                 if not any(kw in title for kw in keywords):
#                     continue
#                 trends.append({
#                     "source":          "Hacker News",
#                     "title":           story.get("title", ""),
#                     "url":             story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
#                     "score":           story.get("score", 0),
#                     "tag":             "tech",
#                     "relevance_score": 0.86,
#                 })
#                 if len(trends) >= limit:
#                     break

#         return trends

#     except Exception as e:
#         logger.warning("HackerNews fetch failed: %s", e)
#         return []


# # ── Dev.to ───────────────────────────────────────────────────────────────────

# async def fetch_devto(domain: str, limit: int = 6) -> List[Dict]:
#     keywords = get_keywords_for_domain(domain)
#     tag = keywords[0].lower().replace(" ", "")

#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://dev.to/api/articles",
#                 params={"tag": tag, "top": 7, "per_page": limit}
#             )
#             if resp.status_code != 200:
#                 resp = await client.get(
#                     "https://dev.to/api/articles",
#                     params={"top": 7, "per_page": limit}
#                 )

#             trends = []
#             for a in resp.json():
#                 trends.append({
#                     "source":          "Dev.to",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("url", ""),
#                     "score":           a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 5,
#                     "tag":             tag,
#                     "relevance_score": 0.82,
#                 })
#             return trends

#     except Exception as e:
#         logger.warning("Dev.to fetch failed: %s", e)
#         return []


# # ── Google News RSS ──────────────────────────────────────────────────────────

# async def fetch_google_news(query: str, limit: int = 8) -> List[Dict]:
#     safe_query = query.replace(" ", "+").replace("/", "+")
#     url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-IN&gl=IN&ceid=IN:en"

#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             response = await client.get(url)
#             response.raise_for_status()
#         feed = feedparser.parse(response.text)

#         trends = []
#         for entry in feed.entries[:limit]:
#             trends.append({
#                 "source":          "Google News",
#                 "title":           entry.get("title", "").split(" - ")[0],
#                 "url":             entry.get("link", ""),
#                 "score":           500,
#                 "tag":             "news",
#                 "relevance_score": 0.80,
#             })
#         return trends

#     except Exception as e:
#         logger.warning("Google News fetch failed: %s", e)
#         return []


# # ── Newsdata.io ──────────────────────────────────────────────────────────────

# async def fetch_newsdata(query: str, limit: int = 6) -> List[Dict]:
#     if not NEWSDATA_API_KEY:
#         return []

#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://newsdata.io/api/1/news",
#                 params={
#                     "apikey":   NEWSDATA_API_KEY,
#                     "q":        query,
#                     "language": "en",
#                     "category": "technology,business",
#                 },
#             )
#             data = resp.json()
#             if data.get("status") != "success":
#                 logger.warning("Newsdata returned non-success: %s", data.get("results", {}).get("message", "unknown"))
#                 return []

#             trends = []
#             for article in (data.get("results") or [])[:limit]:
#                 trends.append({
#                     "source":          f"Newsdata · {article.get('source_id', '')}",
#                     "title":           article.get("title", ""),
#                     "url":             article.get("link", ""),
#                     "score":           700,
#                     "tag":             "news",
#                     "relevance_score": 0.83,
#                 })
#             return trends

#     except Exception as e:
#         logger.warning("Newsdata fetch failed: %s", e)
#         return []


# # ── Aggregate ────────────────────────────────────────────────────────────────

# async def fetch_all_trends(domain: str, interests: str = "") -> List[Dict]:
#     query = f"{domain} {interests}".strip()

#     results = await asyncio.gather(
#         fetch_hackernews(domain),
#         fetch_devto(domain),
#         fetch_google_news(query),
#         fetch_newsdata(query),
#         return_exceptions=True,
#     )

#     all_trends: List[Dict] = []
#     for r in results:
#         if isinstance(r, list):
#             all_trends.extend(r)
#         elif isinstance(r, Exception):
#             logger.warning("Trend source failed: %s", r)

#     # Deduplicate by title prefix
#     seen: set = set()
#     unique: List[Dict] = []
#     for t in all_trends:
#         key = t.get("title", "")[:50].lower().strip()
#         if key and key not in seen:
#             seen.add(key)
#             unique.append(t)

#     unique.sort(
#         key=lambda x: (x.get("relevance_score", 0), x.get("score", 0)),
#         reverse=True,
#     )

#     return unique[:20]
# """
# trends_service.py
# ─────────────────
# Fetches trending content from:
#   • Hacker News  (always works, no key needed)
#   • Dev.to       (always works, no key needed)
#   • Google News  (RSS, always works, no key needed)
#   • Newsdata.io  (requires NEWSDATA_API_KEY in .env — you have one)
 
# snscrape / Twitter removed: Twitter blocked snscrape in 2023.
# """
 
# import os
# import asyncio
# import feedparser
# import httpx
# from typing import List, Dict
# from dotenv import load_dotenv
 
# load_dotenv()
 
# NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
 
# # ── Domain → keyword mapping ──────────────────────────────────────────────────
 
# DOMAIN_KEYWORDS: Dict[str, List[str]] = {
#     "ai":        ["AI", "machine learning", "LLM", "GPT", "artificial intelligence"],
#     "saas":      ["SaaS", "startup", "product", "B2B", "software"],
#     "tech":      ["technology", "programming", "software", "developer", "coding"],
#     "startup":   ["startup", "founder", "fundraising", "YC", "venture"],
#     "finance":   ["investing", "stocks", "market", "fintech", "crypto"],
#     "marketing": ["marketing", "growth", "SEO", "social media", "content"],
#     "content":   ["content creator", "viral", "LinkedIn", "Instagram", "personal brand"],
#     "design":    ["design", "UI", "UX", "Figma", "product design"],
#     "edtech":    ["education", "learning", "course", "edtech", "skills"],
#     "default":   ["technology", "startup", "AI", "innovation", "product"],
# }
 
 
# def get_keywords_for_domain(domain: str) -> List[str]:
#     d = domain.lower()
#     for key, kws in DOMAIN_KEYWORDS.items():
#         if key in d:
#             return kws
#     # Unknown domain: use words from domain string + defaults
#     extra = [w.strip() for w in domain.replace("/", " ").split() if len(w) > 2]
#     return DOMAIN_KEYWORDS["default"] + extra[:3]
 
 
# # ── Individual fetchers ───────────────────────────────────────────────────────
 
# async def fetch_hackernews(domain: str, limit: int = 8) -> List[Dict]:
#     """
#     Fetches top HN stories matching domain keywords.
#     Fixed: opens a single client and fetches items sequentially to avoid
#     the 'async generator used outside context' error from the previous version.
#     """
#     keywords = [kw.lower() for kw in get_keywords_for_domain(domain)]
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             top_resp = await client.get(
#                 "https://hacker-news.firebaseio.com/v0/topstories.json"
#             )
#             if top_resp.status_code != 200:
#                 return []
#             top_ids = top_resp.json()[:60]  # fetch more so we have enough after filtering
 
#             trends: List[Dict] = []
#             for sid in top_ids:
#                 if len(trends) >= limit:
#                     break
#                 try:
#                     resp = await client.get(
#                         f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
#                         timeout=8.0,
#                     )
#                     if resp.status_code != 200:
#                         continue
#                     story = resp.json()
#                     if not story or story.get("type") != "story":
#                         continue
#                     title = (story.get("title") or "").lower()
#                     if not any(kw in title for kw in keywords):
#                         continue
#                     trends.append({
#                         "source":          "Hacker News",
#                         "title":           story.get("title", ""),
#                         "url":             story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
#                         "score":           story.get("score", 0),
#                         "tag":             "tech",
#                         "relevance_score": 0.86,
#                     })
#                 except Exception:
#                     continue
 
#         return trends
 
#     except Exception:
#         return []
 
 
# async def fetch_devto(domain: str, limit: int = 8) -> List[Dict]:
#     """
#     Fetches trending articles from Dev.to.
#     Falls back to global top articles if the domain tag returns nothing.
#     """
#     keywords = get_keywords_for_domain(domain)
#     # Build a clean tag: lowercase, no spaces, no special chars
#     tag = re.sub(r"[^a-z0-9]", "", keywords[0].lower()) if keywords else "webdev"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://dev.to/api/articles",
#                 params={"tag": tag, "top": 7, "per_page": limit},
#             )
#             articles = resp.json() if resp.status_code == 200 else []
 
#             # Fallback to global trending if tag returned nothing
#             if not articles:
#                 resp = await client.get(
#                     "https://dev.to/api/articles",
#                     params={"top": 7, "per_page": limit},
#                 )
#                 articles = resp.json() if resp.status_code == 200 else []
 
#             trends = []
#             for a in articles:
#                 if not isinstance(a, dict):
#                     continue
#                 trends.append({
#                     "source":          "Dev.to",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("url", ""),
#                     "score":           a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 5,
#                     "tag":             tag,
#                     "relevance_score": 0.82,
#                 })
#             return trends
 
#     except Exception:
#         return []
 
 
# async def fetch_google_news(query: str, limit: int = 10) -> List[Dict]:
#     """
#     Fetches from Google News RSS — no API key needed.
#     """
#     safe_query = query.strip().replace(" ", "+").replace("/", "+")
#     url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-IN&gl=IN&ceid=IN:en"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             response = await client.get(url)
#         feed = feedparser.parse(response.text)
 
#         trends = []
#         for entry in feed.entries[:limit]:
#             title = entry.get("title", "")
#             # Strip the source suffix Google appends: "Title - Source Name"
#             clean_title = title.rsplit(" - ", 1)[0].strip()
#             if not clean_title:
#                 continue
#             trends.append({
#                 "source":          "Google News",
#                 "title":           clean_title,
#                 "url":             entry.get("link", ""),
#                 "score":           500,
#                 "tag":             "news",
#                 "relevance_score": 0.80,
#             })
#         return trends
 
#     except Exception:
#         return []
 
 
# async def fetch_newsdata(query: str, limit: int = 8) -> List[Dict]:
#     """
#     Fetches from Newsdata.io — requires NEWSDATA_API_KEY.
#     """
#     if not NEWSDATA_API_KEY:
#         return []
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://newsdata.io/api/1/news",
#                 params={
#                     "apikey":   NEWSDATA_API_KEY,
#                     "q":        query,
#                     "language": "en",
#                     "category": "technology,business",
#                 },
#             )
#             data = resp.json()
#             if data.get("status") != "success":
#                 return []
 
#             trends = []
#             for article in (data.get("results") or [])[:limit]:
#                 if not isinstance(article, dict):
#                     continue
#                 trends.append({
#                     "source":          f"Newsdata · {article.get('source_id', '')}",
#                     "title":           article.get("title", ""),
#                     "url":             article.get("link", ""),
#                     "score":           700,
#                     "tag":             "news",
#                     "relevance_score": 0.85,
#                 })
#             return trends
 
#     except Exception:
#         return []
 
 
# # ── Aggregator ────────────────────────────────────────────────────────────────
 
# async def fetch_all_trends(domain: str, interests: str = "") -> List[Dict]:
#     """
#     Runs all fetchers concurrently, deduplicates, and returns top 20.
#     """
#     query = f"{domain} {interests}".strip() or "technology"
 
#     results = await asyncio.gather(
#         fetch_hackernews(domain),
#         fetch_devto(domain),
#         fetch_google_news(query),
#         fetch_newsdata(query),
#         return_exceptions=True,
#     )
 
#     all_trends: List[Dict] = []
#     for r in results:
#         if isinstance(r, list):
#             all_trends.extend(r)
 
#     # Deduplicate by title prefix (case-insensitive)
#     seen: set = set()
#     unique: List[Dict] = []
#     for t in all_trends:
#         key = t.get("title", "")[:60].lower().strip()
#         if key and key not in seen:
#             seen.add(key)
#             unique.append(t)
 
#     # Sort: relevance first, then engagement score
#     unique.sort(
#         key=lambda x: (x.get("relevance_score", 0), x.get("score", 0)),
#         reverse=True,
#     )
 
#     return unique[:20]
 
 
# # ── Missing import used in fetch_devto ───────────────────────────────────────
# import re
# """
# trends_service.py — fetches from Hacker News, Dev.to, Google News, Newsdata.io
# """
 
# import os
# import re
# import asyncio
# import feedparser
# import httpx
# from typing import List, Dict
# from dotenv import load_dotenv
 
# load_dotenv()
 
# NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
 
# DOMAIN_KEYWORDS: Dict[str, List[str]] = {
#     "ai":        ["AI", "machine learning", "LLM", "GPT", "artificial intelligence"],
#     "saas":      ["SaaS", "startup", "product", "B2B", "software"],
#     "tech":      ["technology", "programming", "software", "developer", "coding"],
#     "startup":   ["startup", "founder", "fundraising", "YC", "venture"],
#     "finance":   ["investing", "stocks", "market", "fintech", "crypto"],
#     "marketing": ["marketing", "growth", "SEO", "social media", "content"],
#     "content":   ["content creator", "viral", "LinkedIn", "Instagram", "personal brand"],
#     "design":    ["design", "UI", "UX", "Figma", "product design"],
#     "edtech":    ["education", "learning", "course", "edtech", "skills"],
#     "default":   ["technology", "startup", "AI", "innovation", "product"],
# }
 
 
# def get_keywords_for_domain(domain: str) -> List[str]:
#     d = domain.lower()
#     for key, kws in DOMAIN_KEYWORDS.items():
#         if key in d:
#             return kws
#     extra = [w.strip() for w in domain.replace("/", " ").split() if len(w) > 2]
#     return DOMAIN_KEYWORDS["default"] + extra[:3]
 
 
# # ── Hacker News ───────────────────────────────────────────────────────────────
 
# async def fetch_hackernews(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = [kw.lower() for kw in get_keywords_for_domain(domain)]
#     trends: List[Dict] = []
 
#     try:
#         async with httpx.AsyncClient(timeout=20.0) as client:
#             top_resp = await client.get(
#                 "https://hacker-news.firebaseio.com/v0/topstories.json"
#             )
#             if top_resp.status_code != 200:
#                 return []
 
#             top_ids = top_resp.json()[:80]
 
#             # Fetch up to 80 stories concurrently then filter
#             tasks = [
#                 client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=6.0)
#                 for sid in top_ids
#             ]
#             responses = await asyncio.gather(*tasks, return_exceptions=True)
 
#             for resp in responses:
#                 if len(trends) >= limit:
#                     break
#                 if isinstance(resp, Exception):
#                     continue
#                 if resp.status_code != 200:
#                     continue
#                 story = resp.json()
#                 if not story or story.get("type") != "story":
#                     continue
#                 title = (story.get("title") or "").lower()
#                 if not any(kw in title for kw in keywords):
#                     continue
#                 trends.append({
#                     "source":          "Hacker News",
#                     "title":           story.get("title", ""),
#                     "url":             story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
#                     "score":           story.get("score", 0),
#                     "tag":             "tech",
#                     "relevance_score": 0.86,
#                 })
 
#     except Exception as e:
#         print(f"[trends] HackerNews error: {e}")
 
#     return trends
 
 
# # ── Dev.to ────────────────────────────────────────────────────────────────────
 
# async def fetch_devto(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = get_keywords_for_domain(domain)
#     tag = re.sub(r"[^a-z0-9]", "", keywords[0].lower()) if keywords else "webdev"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://dev.to/api/articles",
#                 params={"tag": tag, "top": 7, "per_page": limit},
#             )
#             articles = resp.json() if resp.status_code == 200 else []
 
#             if not articles:
#                 resp = await client.get(
#                     "https://dev.to/api/articles",
#                     params={"top": 7, "per_page": limit},
#                 )
#                 articles = resp.json() if resp.status_code == 200 else []
 
#             return [
#                 {
#                     "source":          "Dev.to",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("url", ""),
#                     "score":           a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 5,
#                     "tag":             tag,
#                     "relevance_score": 0.82,
#                 }
#                 for a in articles if isinstance(a, dict) and a.get("title")
#             ]
 
#     except Exception as e:
#         print(f"[trends] Dev.to error: {e}")
#         return []
 
 
# # ── Google News RSS ───────────────────────────────────────────────────────────
 
# async def fetch_google_news(query: str, limit: int = 10) -> List[Dict]:
#     safe_query = query.strip().replace(" ", "+").replace("/", "+")
#     url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-IN&gl=IN&ceid=IN:en"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             response = await client.get(url, follow_redirects=True)
 
#         # feedparser works on raw bytes/text — pass text directly
#         feed = feedparser.parse(response.text)
 
#         if not feed.entries:
#             # Fallback: try without locale
#             url2 = f"https://news.google.com/rss/search?q={safe_query}"
#             async with httpx.AsyncClient(timeout=15.0) as client:
#                 response2 = await client.get(url2, follow_redirects=True)
#             feed = feedparser.parse(response2.text)
 
#         trends = []
#         for entry in feed.entries[:limit]:
#             title = entry.get("title", "")
#             clean_title = title.rsplit(" - ", 1)[0].strip()
#             if not clean_title:
#                 continue
#             trends.append({
#                 "source":          "Google News",
#                 "title":           clean_title,
#                 "url":             entry.get("link", ""),
#                 "score":           500,
#                 "tag":             "news",
#                 "relevance_score": 0.80,
#             })
#         return trends
 
#     except Exception as e:
#         print(f"[trends] Google News error: {e}")
#         return []
 
 
# # ── Newsdata.io ───────────────────────────────────────────────────────────────
 
# async def fetch_newsdata(query: str, limit: int = 8) -> List[Dict]:
#     if not NEWSDATA_API_KEY:
#         return []
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://newsdata.io/api/1/news",
#                 params={
#                     "apikey":   NEWSDATA_API_KEY,
#                     "q":        query,
#                     "language": "en",
#                     "category": "technology,business",
#                 },
#             )
#             data = resp.json()
#             if data.get("status") != "success":
#                 print(f"[trends] Newsdata error: {data.get('message', 'unknown')}")
#                 return []
 
#             return [
#                 {
#                     "source":          f"Newsdata · {a.get('source_id', '')}",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("link", ""),
#                     "score":           700,
#                     "tag":             "news",
#                     "relevance_score": 0.85,
#                 }
#                 for a in (data.get("results") or [])[:limit]
#                 if isinstance(a, dict) and a.get("title")
#             ]
 
#     except Exception as e:
#         print(f"[trends] Newsdata error: {e}")
#         return []
 
 
# # ── Aggregator ────────────────────────────────────────────────────────────────
 
# async def fetch_all_trends(domain: str, interests: str = "") -> List[Dict]:
#     query = f"{domain} {interests}".strip() or "technology"
 
#     print(f"[trends] Fetching for domain='{domain}' query='{query}'")
 
#     results = await asyncio.gather(
#         fetch_hackernews(domain),
#         fetch_devto(domain),
#         fetch_google_news(query),
#         fetch_newsdata(query),
#         return_exceptions=True,
#     )
 
#     all_trends: List[Dict] = []
#     for i, r in enumerate(results):
#         if isinstance(r, Exception):
#             print(f"[trends] Source {i} failed: {r}")
#         elif isinstance(r, list):
#             print(f"[trends] Source {i} returned {len(r)} items")
#             all_trends.extend(r)
 
#     # Deduplicate
#     seen: set = set()
#     unique: List[Dict] = []
#     for t in all_trends:
#         key = t.get("title", "")[:60].lower().strip()
#         if key and key not in seen:
#             seen.add(key)
#             unique.append(t)
 
#     unique.sort(
#         key=lambda x: (x.get("relevance_score", 0), x.get("score", 0)),
#         reverse=True,
#     )
 
#     print(f"[trends] Total unique trends: {len(unique)}")
#     return unique[:20]
 

# """
# trends_service.py — fetches from Hacker News, Dev.to, Google News, Newsdata.io.
# Falls back gracefully when any source is unreachable.
# """
 
# import os
# import re
# import asyncio
# import logging
# import feedparser
# import httpx
# from typing import List, Dict
# from dotenv import load_dotenv
 
# load_dotenv()
 
# logger = logging.getLogger(__name__)
 
# NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
 
# DOMAIN_KEYWORDS: Dict[str, List[str]] = {
#     "ai":         ["AI", "machine learning", "LLM", "GPT", "artificial intelligence", "deep learning", "neural"],
#     "saas":       ["SaaS", "startup", "product", "B2B", "software", "cloud", "subscription"],
#     "tech":       ["technology", "programming", "software", "developer", "coding", "open source", "github"],
#     "startup":    ["startup", "founder", "fundraising", "YC", "venture", "seed", "pitch"],
#     "finance":    ["investing", "stocks", "market", "fintech", "crypto", "trading", "bitcoin"],
#     "marketing":  ["marketing", "growth", "SEO", "social media", "content", "brand", "campaign"],
#     "content":    ["content creator", "viral", "LinkedIn", "Instagram", "personal brand", "creator", "audience"],
#     "design":     ["design", "UI", "UX", "Figma", "product design", "typography", "interface"],
#     "edtech":     ["education", "learning", "course", "edtech", "skills", "training", "online course"],
#     "health":     ["health", "wellness", "fitness", "medical", "mental health", "nutrition"],
#     "default":    ["technology", "startup", "AI", "innovation", "product", "business", "growth"],
# }
 
 
# def get_keywords_for_domain(domain: str) -> List[str]:
#     """Return keyword list for the given domain string."""
#     d = domain.lower()
#     for key, kws in DOMAIN_KEYWORDS.items():
#         if key in d:
#             return kws
#     # Unknown domain: extract meaningful words + default keywords
#     extra = [w.strip() for w in domain.replace("/", " ").replace(",", " ").split() if len(w) > 2]
#     return DOMAIN_KEYWORDS["default"] + extra[:4]
 
 
# # ── Hacker News ───────────────────────────────────────────────────────────────
 
# async def fetch_hackernews(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = [kw.lower() for kw in get_keywords_for_domain(domain)]
#     trends: List[Dict] = []
 
#     try:
#         async with httpx.AsyncClient(timeout=20.0) as client:
#             top_resp = await client.get(
#                 "https://hacker-news.firebaseio.com/v0/topstories.json"
#             )
#             if top_resp.status_code != 200:
#                 logger.warning("[trends] HackerNews topstories returned non-200")
#                 return []
 
#             top_ids = top_resp.json()[:80]
 
#             tasks = [
#                 client.get(
#                     f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
#                     timeout=6.0,
#                 )
#                 for sid in top_ids
#             ]
#             responses = await asyncio.gather(*tasks, return_exceptions=True)
 
#             for resp in responses:
#                 if len(trends) >= limit:
#                     break
#                 if isinstance(resp, Exception):
#                     continue
#                 if resp.status_code != 200:
#                     continue
#                 story = resp.json()
#                 if not story or story.get("type") != "story":
#                     continue
#                 title = (story.get("title") or "").lower()
#                 if not any(kw in title for kw in keywords):
#                     continue
#                 trends.append({
#                     "source":          "Hacker News",
#                     "title":           story.get("title", ""),
#                     "url":             story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
#                     "score":           story.get("score", 0),
#                     "tag":             "tech",
#                     "relevance_score": 0.86,
#                 })
 
#     except Exception as e:
#         print(f"[trends] HackerNews error: {e}")
 
#     return trends
 
 
# # ── Dev.to ────────────────────────────────────────────────────────────────────
 
# async def fetch_devto(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = get_keywords_for_domain(domain)
#     tag = re.sub(r"[^a-z0-9]", "", keywords[0].lower()) if keywords else "webdev"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://dev.to/api/articles",
#                 params={"tag": tag, "top": 7, "per_page": limit},
#             )
#             articles = resp.json() if resp.status_code == 200 else []
 
#             if not articles:
#                 resp = await client.get(
#                     "https://dev.to/api/articles",
#                     params={"top": 7, "per_page": limit},
#                 )
#                 articles = resp.json() if resp.status_code == 200 else []
 
#             return [
#                 {
#                     "source":          "Dev.to",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("url", ""),
#                     "score":           a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 5,
#                     "tag":             tag,
#                     "relevance_score": 0.82,
#                 }
#                 for a in articles if isinstance(a, dict) and a.get("title")
#             ]
 
#     except Exception as e:
#         print(f"[trends] Dev.to error: {e}")
#         return []
 
 
# # ── Google News RSS ───────────────────────────────────────────────────────────
 
# async def fetch_google_news(query: str, limit: int = 10) -> List[Dict]:
#     safe_query = query.strip().replace(" ", "+").replace("/", "+")
#     url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-IN&gl=IN&ceid=IN:en"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             response = await client.get(url, follow_redirects=True)
 
#         # feedparser works on raw bytes/text — pass text directly
#         feed = feedparser.parse(response.text)
 
#         if not feed.entries:
#             # Fallback: try without locale
#             url2 = f"https://news.google.com/rss/search?q={safe_query}"
#             async with httpx.AsyncClient(timeout=15.0) as client:
#                 response2 = await client.get(url2, follow_redirects=True)
#             feed = feedparser.parse(response2.text)
 
#         trends = []
#         for entry in feed.entries[:limit]:
#             title = entry.get("title", "")
#             clean_title = title.rsplit(" - ", 1)[0].strip()
#             if not clean_title:
#                 continue
#             trends.append({
#                 "source":          "Google News",
#                 "title":           clean_title,
#                 "url":             entry.get("link", ""),
#                 "score":           500,
#                 "tag":             "news",
#                 "relevance_score": 0.80,
#             })
#         return trends
 
#     except Exception as e:
#         print(f"[trends] Google News error: {e}")
#         return []
 
 
# # ── Newsdata.io ───────────────────────────────────────────────────────────────
 
# async def fetch_newsdata(query: str, limit: int = 8) -> List[Dict]:
#     if not NEWSDATA_API_KEY:
#         return []
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://newsdata.io/api/1/news",
#                 params={
#                     "apikey":   NEWSDATA_API_KEY,
#                     "q":        query,
#                     "language": "en",
#                     "category": "technology,business",
#                 },
#             )
#             data = resp.json()
#             if data.get("status") != "success":
#                 print(f"[trends] Newsdata error: {data.get('message', 'unknown')}")
#                 return []
 
#             return [
#                 {
#                     "source":          f"Newsdata · {a.get('source_id', '')}",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("link", ""),
#                     "score":           700,
#                     "tag":             "news",
#                     "relevance_score": 0.85,
#                 }
#                 for a in (data.get("results") or [])[:limit]
#                 if isinstance(a, dict) and a.get("title")
#             ]
 
#     except Exception as e:
#         print(f"[trends] Newsdata error: {e}")
#         return []
 
 
# # ── Aggregator ────────────────────────────────────────────────────────────────
 
# async def fetch_all_trends(domain: str, interests: str = "") -> List[Dict]:
#     query = f"{domain} {interests}".strip() or "technology"
 
#     print(f"[trends] Fetching for domain='{domain}' query='{query}'")
 
#     results = await asyncio.gather(
#         fetch_hackernews(domain),
#         fetch_devto(domain),
#         fetch_google_news(query),
#         fetch_newsdata(query),
#         return_exceptions=True,
#     )
 
#     all_trends: List[Dict] = []
#     for i, r in enumerate(results):
#         if isinstance(r, Exception):
#             print(f"[trends] Source {i} failed: {r}")
#         elif isinstance(r, list):
#             print(f"[trends] Source {i} returned {len(r)} items")
#             all_trends.extend(r)
 
#     # Deduplicate
#     seen: set = set()
#     unique: List[Dict] = []
#     for t in all_trends:
#         key = t.get("title", "")[:60].lower().strip()
#         if key and key not in seen:
#             seen.add(key)
#             unique.append(t)
 
#     unique.sort(
#         key=lambda x: (x.get("relevance_score", 0), x.get("score", 0)),
#         reverse=True,
#     )
 
#     print(f"[trends] Total unique trends: {len(unique)}")
#     return unique[:20]
 
 
# # ── Missing import used in fetch_devto ───────────────────────────────────────
# import re
# """
# trends_service.py — fetches from Hacker News, Dev.to, Google News, Newsdata.io
# """
 
# import os
# import re
# import asyncio
# import feedparser
# import httpx
# from typing import List, Dict
# from dotenv import load_dotenv
 
# load_dotenv()
 
# NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
 
# DOMAIN_KEYWORDS: Dict[str, List[str]] = {
#     "ai":        ["AI", "machine learning", "LLM", "GPT", "artificial intelligence"],
#     "saas":      ["SaaS", "startup", "product", "B2B", "software"],
#     "tech":      ["technology", "programming", "software", "developer", "coding"],
#     "startup":   ["startup", "founder", "fundraising", "YC", "venture"],
#     "finance":   ["investing", "stocks", "market", "fintech", "crypto"],
#     "marketing": ["marketing", "growth", "SEO", "social media", "content"],
#     "content":   ["content creator", "viral", "LinkedIn", "Instagram", "personal brand"],
#     "design":    ["design", "UI", "UX", "Figma", "product design"],
#     "edtech":    ["education", "learning", "course", "edtech", "skills"],
#     "default":   ["technology", "startup", "AI", "innovation", "product"],
# }
 
 
# def get_keywords_for_domain(domain: str) -> List[str]:
#     d = domain.lower()
#     for key, kws in DOMAIN_KEYWORDS.items():
#         if key in d:
#             return kws
#     extra = [w.strip() for w in domain.replace("/", " ").split() if len(w) > 2]
#     return DOMAIN_KEYWORDS["default"] + extra[:3]
 
 
# # ── Hacker News ───────────────────────────────────────────────────────────────
 
# async def fetch_hackernews(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = [kw.lower() for kw in get_keywords_for_domain(domain)]
#     trends: List[Dict] = []
 
#     try:
#         async with httpx.AsyncClient(timeout=20.0) as client:
#             top_resp = await client.get(
#                 "https://hacker-news.firebaseio.com/v0/topstories.json"
#             )
#             if top_resp.status_code != 200:
#                 return []
 
#             top_ids = top_resp.json()[:80]
 
#             # Fetch up to 80 stories concurrently then filter
#             tasks = [
#                 client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json", timeout=6.0)
#                 for sid in top_ids
#             ]
#             responses = await asyncio.gather(*tasks, return_exceptions=True)
 
#             for resp in responses:
#                 if len(trends) >= limit:
#                     break
#                 if isinstance(resp, Exception):
#                     continue
#                 if resp.status_code != 200:
#                     continue
#                 story = resp.json()
#                 if not story or story.get("type") != "story":
#                     continue
#                 title = (story.get("title") or "").lower()
#                 if not any(kw in title for kw in keywords):
#                     continue
#                 trends.append({
#                     "source":          "Hacker News",
#                     "title":           story.get("title", ""),
#                     "url":             story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
#                     "score":           story.get("score", 0),
#                     "tag":             "tech",
#                     "relevance_score": 0.86,
#                 })
 
#     except Exception as e:
#         print(f"[trends] HackerNews error: {e}")
 
#     return trends
 
 
# # ── Dev.to ────────────────────────────────────────────────────────────────────
 
# async def fetch_devto(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = get_keywords_for_domain(domain)
#     tag = re.sub(r"[^a-z0-9]", "", keywords[0].lower()) if keywords else "webdev"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://dev.to/api/articles",
#                 params={"tag": tag, "top": 7, "per_page": limit},
#             )
#             articles = resp.json() if resp.status_code == 200 else []
 
#             if not articles:
#                 resp = await client.get(
#                     "https://dev.to/api/articles",
#                     params={"top": 7, "per_page": limit},
#                 )
#                 articles = resp.json() if resp.status_code == 200 else []
 
#             return [
#                 {
#                     "source":          "Dev.to",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("url", ""),
#                     "score":           a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 5,
#                     "tag":             tag,
#                     "relevance_score": 0.82,
#                 }
#                 for a in articles if isinstance(a, dict) and a.get("title")
#             ]
 
#     except Exception as e:
#         print(f"[trends] Dev.to error: {e}")
#         return []
 
 
# # ── Google News RSS ───────────────────────────────────────────────────────────
 
# async def fetch_google_news(query: str, limit: int = 10) -> List[Dict]:
#     safe_query = query.strip().replace(" ", "+").replace("/", "+")
#     url = f"https://news.google.com/rss/search?q={safe_query}&hl=en-IN&gl=IN&ceid=IN:en"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             response = await client.get(url, follow_redirects=True)
 
#         # feedparser works on raw bytes/text — pass text directly
#         feed = feedparser.parse(response.text)
 
#         if not feed.entries:
#             # Fallback: try without locale
#             url2 = f"https://news.google.com/rss/search?q={safe_query}"
#             async with httpx.AsyncClient(timeout=15.0) as client:
#                 response2 = await client.get(url2, follow_redirects=True)
#             feed = feedparser.parse(response2.text)
 
#         trends = []
#         for entry in feed.entries[:limit]:
#             title = entry.get("title", "")
#             clean_title = title.rsplit(" - ", 1)[0].strip()
#             if not clean_title:
#                 continue
#             trends.append({
#                 "source":          "Google News",
#                 "title":           clean_title,
#                 "url":             entry.get("link", ""),
#                 "score":           500,
#                 "tag":             "news",
#                 "relevance_score": 0.80,
#             })
#         return trends
 
#     except Exception as e:
#         print(f"[trends] Google News error: {e}")
#         return []
 
 
# # ── Newsdata.io ───────────────────────────────────────────────────────────────
 
# async def fetch_newsdata(query: str, limit: int = 8) -> List[Dict]:
#     if not NEWSDATA_API_KEY:
#         return []
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             resp = await client.get(
#                 "https://newsdata.io/api/1/news",
#                 params={
#                     "apikey":   NEWSDATA_API_KEY,
#                     "q":        query,
#                     "language": "en",
#                     "category": "technology,business",
#                 },
#             )
#             data = resp.json()
#             if data.get("status") != "success":
#                 print(f"[trends] Newsdata error: {data.get('message', 'unknown')}")
#                 return []
 
#             return [
#                 {
#                     "source":          f"Newsdata · {a.get('source_id', '')}",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("link", ""),
#                     "score":           700,
#                     "tag":             "news",
#                     "relevance_score": 0.85,
#                 }
#                 for a in (data.get("results") or [])[:limit]
#                 if isinstance(a, dict) and a.get("title")
#             ]
 
#     except Exception as e:
#         print(f"[trends] Newsdata error: {e}")
#         return []
 
 
# # ── Aggregator ────────────────────────────────────────────────────────────────
 
# async def fetch_all_trends(domain: str, interests: str = "") -> List[Dict]:
#     query = f"{domain} {interests}".strip() or "technology"
 
#     print(f"[trends] Fetching for domain='{domain}' query='{query}'")
 
#     results = await asyncio.gather(
#         fetch_hackernews(domain),
#         fetch_devto(domain),
#         fetch_google_news(query),
#         fetch_newsdata(query),
#         return_exceptions=True,
#     )
 
#     all_trends: List[Dict] = []
#     for i, r in enumerate(results):
#         if isinstance(r, Exception):
#             print(f"[trends] Source {i} failed: {r}")
#         elif isinstance(r, list):
#             print(f"[trends] Source {i} returned {len(r)} items")
#             all_trends.extend(r)
 
#     # Deduplicate
#     seen: set = set()
#     unique: List[Dict] = []
#     for t in all_trends:
#         key = t.get("title", "")[:60].lower().strip()
#         if key and key not in seen:
#             seen.add(key)
#             unique.append(t)
 
#     unique.sort(
#         key=lambda x: (x.get("relevance_score", 0), x.get("score", 0)),
#         reverse=True,
#     )
 
#     print(f"[trends] Total unique trends: {len(unique)}")
#     return unique[:20]
 
 
# # ── AI Enhancements (Summary and Live Graph) ──────────────────────────────────
 

#             ]
#             responses = await asyncio.gather(*tasks, return_exceptions=True)
 
#             for resp in responses:
#                 if len(trends) >= limit:
#                     break
#                 if isinstance(resp, Exception):
#                     continue
#                 if resp.status_code != 200:
#                     continue
#                 story = resp.json()
#                 if not story or story.get("type") != "story":
#                     continue
#                 title = (story.get("title") or "").lower()
#                 # Broad match — accept if ANY keyword is present
#                 if not any(kw in title for kw in keywords):
#                     continue
#                 trends.append({
#                     "source":          "Hacker News",
#                     "title":           story.get("title", ""),
#                     "url":             story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
#                     "score":           story.get("score", 0),
#                     "tag":             "tech",
#                     "relevance_score": 0.86,
#                 })
 
#         logger.info(f"[trends] HackerNews: {len(trends)} items")
 
#     except Exception as e:
#         logger.warning(f"[trends] HackerNews fetch failed: {e}")
 
#     return trends
 
 
# # ── Dev.to ────────────────────────────────────────────────────────────────────
 
# async def fetch_devto(domain: str, limit: int = 8) -> List[Dict]:
#     keywords = get_keywords_for_domain(domain)
#     # Build a clean tag slug
#     tag = re.sub(r"[^a-z0-9]", "", keywords[0].lower()) if keywords else "webdev"
 
#     try:
#         async with httpx.AsyncClient(timeout=15.0) as client:
#             # Try domain-specific tag first
#             resp = await client.get(
#                 "https://dev.to/api/articles",
#                 params={"tag": tag, "top": 7, "per_page": limit},
#             )
#             articles = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []
 
#             # Fallback: try second keyword
#             if not articles and len(keywords) > 1:
#                 tag2 = re.sub(r"[^a-z0-9]", "", keywords[1].lower())
#                 resp2 = await client.get(
#                     "https://dev.to/api/articles",
#                     params={"tag": tag2, "top": 7, "per_page": limit},
#                 )
#                 articles = resp2.json() if resp2.status_code == 200 and isinstance(resp2.json(), list) else []
 
#             # Final fallback: global trending
#             if not articles:
#                 resp3 = await client.get(
#                     "https://dev.to/api/articles",
#                     params={"top": 7, "per_page": limit},
#                 )
#                 articles = resp3.json() if resp3.status_code == 200 and isinstance(resp3.json(), list) else []
 
#             result = [
#                 {
#                     "source":          "Dev.to",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("url", ""),
#                     "score":           a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 5,
#                     "tag":             tag,
#                     "relevance_score": 0.82,
#                 }
#                 for a in articles
#                 if isinstance(a, dict) and a.get("title")
#             ]
 
#             logger.info(f"[trends] Dev.to: {len(result)} items")
#             return result
 
#     except Exception as e:
#         logger.warning(f"[trends] Dev.to fetch failed: {e}")
#         return []
 
 
# # ── Google News RSS ───────────────────────────────────────────────────────────
 
# async def fetch_google_news(query: str, limit: int = 10) -> List[Dict]:
#     safe_query = query.strip().replace(" ", "+").replace("/", "+")
 
#     urls_to_try = [
#         f"https://news.google.com/rss/search?q={safe_query}&hl=en-IN&gl=IN&ceid=IN:en",
#         f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en",
#         f"https://news.google.com/rss/search?q={safe_query}",
#     ]
 
#     for url in urls_to_try:
#         try:
#             async with httpx.AsyncClient(timeout=15.0) as client:
#                 response = await client.get(url, follow_redirects=True)
 
#             if response.status_code != 200:
#                 continue
 
#             feed = feedparser.parse(response.text)
#             if not feed.entries:
#                 continue
 
#             trends = []
#             for entry in feed.entries[:limit]:
#                 title = entry.get("title", "")
#                 clean_title = title.rsplit(" - ", 1)[0].strip()
#                 if not clean_title:
#                     continue
#                 trends.append({
#                     "source":          "Google News",
#                     "title":           clean_title,
#                     "url":             entry.get("link", ""),
#                     "score":           500,
#                     "tag":             "news",
#                     "relevance_score": 0.80,
#                 })
 
#             logger.info(f"[trends] Google News: {len(trends)} items")
#             return trends
 
#         except Exception as e:
#             logger.warning(f"[trends] Google News attempt failed ({url[:60]}): {e}")
#             continue
 
#     logger.warning("[trends] Google News: all attempts failed")
#     return []
 
 
# # ── Newsdata.io ───────────────────────────────────────────────────────────────
 
# async def fetch_newsdata(query: str, limit: int = 10) -> List[Dict]:
#     if not NEWSDATA_API_KEY:
#         logger.info("[trends] Newsdata: no API key — skipping")
#         return []
 
#     try:
#         async with httpx.AsyncClient(timeout=20.0) as client:
#             resp = await client.get(
#                 "https://newsdata.io/api/1/news",
#                 params={
#                     "apikey":   NEWSDATA_API_KEY,
#                     "q":        query,
#                     "language": "en",
#                     "category": "technology,business",
#                 },
#             )
#             data = resp.json()
 
#             if data.get("status") != "success":
#                 logger.warning(f"[trends] Newsdata non-success: {data.get('message', 'unknown')}")
#                 return []
 
#             results = [
#                 {
#                     "source":          f"Newsdata · {a.get('source_id', '')}",
#                     "title":           a.get("title", ""),
#                     "url":             a.get("link", ""),
#                     "score":           700,
#                     "tag":             "news",
#                     "relevance_score": 0.85,
#                 }
#                 for a in (data.get("results") or [])[:limit]
#                 if isinstance(a, dict) and a.get("title")
#             ]
 
#             logger.info(f"[trends] Newsdata: {len(results)} items")
#             return results
 
#     except Exception as e:
#         logger.warning(f"[trends] Newsdata fetch failed: {e}")
#         return []
 
 
# # ── Aggregator ────────────────────────────────────────────────────────────────
 
# async def fetch_all_trends(domain: str, interests: str = "") -> List[Dict]:
#     """
#     Runs all fetchers concurrently, deduplicates, and returns top 20 sorted by relevance.
#     Always returns results even if some sources fail.
#     """
#     query = f"{domain} {interests}".strip() or "technology"
#     logger.info(f"[trends] fetch_all_trends: domain='{domain}' query='{query}'")
 
#     results = await asyncio.gather(
#         fetch_hackernews(domain),
#         fetch_devto(domain),
#         fetch_google_news(query),
#         fetch_newsdata(query),
#         return_exceptions=True,
#     )
 
#     source_names = ["HackerNews", "Dev.to", "Google News", "Newsdata"]
#     all_trends: List[Dict] = []
 
#     for i, r in enumerate(results):
#         name = source_names[i] if i < len(source_names) else f"Source{i}"
#         if isinstance(r, Exception):
#             logger.warning(f"[trends] {name} raised exception: {r}")
#         elif isinstance(r, list):
#             logger.info(f"[trends] {name}: {len(r)} items collected")
#             all_trends.extend(r)
#         else:
#             logger.warning(f"[trends] {name}: unexpected result type {type(r)}")
 
#     # Deduplicate by title prefix (case-insensitive, first 60 chars)
#     seen: set = set()
#     unique: List[Dict] = []
#     for t in all_trends:
#         key = t.get("title", "")[:60].lower().strip()
#         if key and key not in seen:
#             seen.add(key)
#             unique.append(t)
 
#     # Sort: relevance_score first, then engagement score
#     unique.sort(
#         key=lambda x: (x.get("relevance_score", 0), x.get("score", 0)),
#         reverse=True,
#     )
 
#     logger.info(f"[trends] Total unique trends returned: {len(unique)}")
#     return unique[:20]



"""
trends_service.py — fetches from Hacker News, Dev.to, Google News, Newsdata.io.
Falls back gracefully when any source is unreachable.
"""
 
import os
import re
import asyncio
import logging
import feedparser
import httpx
from typing import List, Dict
from dotenv import load_dotenv
 
load_dotenv()
 
logger = logging.getLogger(__name__)
 
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
 
DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    "ai":         ["AI", "machine learning", "LLM", "GPT", "artificial intelligence", "deep learning", "neural", "openai", "gemini", "claude"],
    "saas":       ["SaaS", "startup", "product", "B2B", "software", "cloud", "subscription", "platform"],
    "tech":       ["technology", "programming", "software", "developer", "coding", "open source", "github", "engineer"],
    "startup":    ["startup", "founder", "fundraising", "YC", "venture", "seed", "pitch", "entrepreneur"],
    "finance":    ["investing", "stocks", "market", "fintech", "crypto", "trading", "bitcoin", "economy"],
    "marketing":  ["marketing", "growth", "SEO", "social media", "content", "brand", "campaign", "ads"],
    "content":    ["content creator", "viral", "LinkedIn", "Instagram", "personal brand", "creator", "audience", "followers"],
    "design":     ["design", "UI", "UX", "Figma", "product design", "typography", "interface", "CSS"],
    "edtech":     ["education", "learning", "course", "edtech", "skills", "training", "online course", "bootcamp"],
    "health":     ["health", "wellness", "fitness", "medical", "mental health", "nutrition", "therapy"],
    "default":    ["technology", "startup", "AI", "innovation", "product", "business", "growth", "future"],
}
 
 
def get_keywords_for_domain(domain: str) -> List[str]:
    """Return keyword list for the given domain string."""
    d = domain.lower()
    for key, kws in DOMAIN_KEYWORDS.items():
        if key in d:
            return kws
    # Unknown domain: extract meaningful words + default keywords
    extra = [w.strip() for w in domain.replace("/", " ").replace(",", " ").split() if len(w) > 2]
    if extra:
        return extra[:4]
    return DOMAIN_KEYWORDS["default"] + extra[:4]
 
 
# ── Hacker News ───────────────────────────────────────────────────────────────
 
async def fetch_hackernews(domain: str, limit: int = 8) -> List[Dict]:
    keywords = [kw.lower() for kw in get_keywords_for_domain(domain)]
    trends: List[Dict] = []
 
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            top_resp = await client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            if top_resp.status_code != 200:
                logger.warning("[trends] HackerNews topstories returned non-200")
                return []
 
            top_ids = top_resp.json()[:80]
 
            tasks = [
                client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                    timeout=6.0,
                )
                for sid in top_ids
            ]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
 
            for resp in responses:
                if len(trends) >= limit:
                    break
                if isinstance(resp, Exception):
                    continue
                if resp.status_code != 200:
                    continue
                story = resp.json()
                if not story or story.get("type") != "story":
                    continue
                title = (story.get("title") or "").lower()
                # Accept if ANY keyword matches
                if not any(kw in title for kw in keywords):
                    continue
                trends.append({
                    "source":          "Hacker News",
                    "title":           story.get("title", ""),
                    "url":             story.get("url") or f"https://news.ycombinator.com/item?id={story['id']}",
                    "score":           story.get("score", 0),
                    "tag":             "tech",
                    "relevance_score": 0.86,
                })
 
        logger.info(f"[trends] HackerNews: {len(trends)} items")
 
    except Exception as e:
        logger.warning(f"[trends] HackerNews fetch failed: {e}")
 
    return trends
 
 
# ── Dev.to ────────────────────────────────────────────────────────────────────
 
async def fetch_devto(domain: str, limit: int = 8) -> List[Dict]:
    keywords = get_keywords_for_domain(domain)
    tag = re.sub(r"[^a-z0-9]", "", keywords[0].lower()) if keywords else "webdev"
 
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Try domain-specific tag first
            resp = await client.get(
                "https://dev.to/api/articles",
                params={"tag": tag, "top": 7, "per_page": limit},
            )
            articles = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []
 
            # Fallback: try second keyword
            if not articles and len(keywords) > 1:
                tag2 = re.sub(r"[^a-z0-9]", "", keywords[1].lower())
                resp2 = await client.get(
                    "https://dev.to/api/articles",
                    params={"tag": tag2, "top": 7, "per_page": limit},
                )
                articles = resp2.json() if resp2.status_code == 200 and isinstance(resp2.json(), list) else []
 
            # Final fallback: global trending
            if not articles:
                resp3 = await client.get(
                    "https://dev.to/api/articles",
                    params={"top": 7, "per_page": limit},
                )
                articles = resp3.json() if resp3.status_code == 200 and isinstance(resp3.json(), list) else []
 
            result = [
                {
                    "source":          "Dev.to",
                    "title":           a.get("title", ""),
                    "url":             a.get("url", ""),
                    "score":           a.get("positive_reactions_count", 0) + a.get("comments_count", 0) * 5,
                    "tag":             tag,
                    "relevance_score": 0.82,
                }
                for a in articles
                if isinstance(a, dict) and a.get("title")
            ]
 
            logger.info(f"[trends] Dev.to: {len(result)} items")
            return result
 
    except Exception as e:
        logger.warning(f"[trends] Dev.to fetch failed: {e}")
        return []
 
 
# ── Google News RSS ───────────────────────────────────────────────────────────
 
async def fetch_google_news(query: str, limit: int = 10) -> List[Dict]:
    safe_query = query.strip().replace(" ", "+").replace("/", "+")
 
    urls_to_try = [
        f"https://news.google.com/rss/search?q={safe_query}&hl=en-IN&gl=IN&ceid=IN:en",
        f"https://news.google.com/rss/search?q={safe_query}&hl=en-US&gl=US&ceid=US:en",
        f"https://news.google.com/rss/search?q={safe_query}",
    ]
 
    for url in urls_to_try:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, follow_redirects=True)
 
            if response.status_code != 200:
                continue
 
            feed = feedparser.parse(response.text)
            if not feed.entries:
                continue
 
            trends = []
            for entry in feed.entries[:limit]:
                title = entry.get("title", "")
                clean_title = title.rsplit(" - ", 1)[0].strip()
                if not clean_title:
                    continue
                trends.append({
                    "source":          "Google News",
                    "title":           clean_title,
                    "url":             entry.get("link", ""),
                    "score":           500,
                    "tag":             "news",
                    "relevance_score": 0.80,
                })
 
            logger.info(f"[trends] Google News: {len(trends)} items")
            return trends
 
        except Exception as e:
            logger.warning(f"[trends] Google News attempt failed: {e}")
            continue
 
    logger.warning("[trends] Google News: all attempts failed")
    return []
 
 
# ── Newsdata.io ───────────────────────────────────────────────────────────────
 
async def fetch_newsdata(query: str, limit: int = 10) -> List[Dict]:
    if not NEWSDATA_API_KEY:
        logger.info("[trends] Newsdata: no API key — skipping")
        return []
 
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.get(
                "https://newsdata.io/api/1/news",
                params={
                    "apikey":   NEWSDATA_API_KEY,
                    "q":        query,
                    "language": "en",
                    "category": "technology,business",
                },
            )
            data = resp.json()
 
            if data.get("status") != "success":
                logger.warning(f"[trends] Newsdata non-success: {data.get('message', 'unknown')}")
                return []
 
            results = [
                {
                    "source":          f"Newsdata · {a.get('source_id', '')}",
                    "title":           a.get("title", ""),
                    "url":             a.get("link", ""),
                    "score":           700,
                    "tag":             "news",
                    "relevance_score": 0.85,
                }
                for a in (data.get("results") or [])[:limit]
                if isinstance(a, dict) and a.get("title")
            ]
 
            logger.info(f"[trends] Newsdata: {len(results)} items")
            return results
 
    except Exception as e:
        logger.warning(f"[trends] Newsdata fetch failed: {e}")
        return []
 
 
# ── Aggregator ────────────────────────────────────────────────────────────────
 
async def fetch_all_trends(domain: str, interests: str = "") -> List[Dict]:
    """
    Runs all fetchers concurrently, deduplicates, and returns top 20 sorted by relevance.
    Always returns results even if some sources fail.
    """
    query = f"{domain} {interests}".strip() or "technology"
    logger.info(f"[trends] fetch_all_trends: domain='{domain}' query='{query}'")
 
    results = await asyncio.gather(
        fetch_hackernews(domain),
        fetch_devto(domain),
        fetch_google_news(query),
        fetch_newsdata(query),
        return_exceptions=True,
    )
 
    source_names = ["HackerNews", "Dev.to", "Google News", "Newsdata"]
    all_trends: List[Dict] = []
 
    for i, r in enumerate(results):
        name = source_names[i] if i < len(source_names) else f"Source{i}"
        if isinstance(r, Exception):
            logger.warning(f"[trends] {name} raised exception: {r}")
        elif isinstance(r, list):
            logger.info(f"[trends] {name}: {len(r)} items collected")
            all_trends.extend(r)
 
    # Deduplicate by title prefix (case-insensitive, first 60 chars)
    seen: set = set()
    unique: List[Dict] = []
    for t in all_trends:
        key = t.get("title", "")[:60].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique.append(t)
 
    # Sort: relevance_score first, then engagement score
    unique.sort(
        key=lambda x: (x.get("relevance_score", 0), x.get("score", 0)),
        reverse=True,
    )
 
    logger.info(f"[trends] Total unique trends returned: {len(unique)}")
    return unique[:20]

# ── AI Enhancements (Summary and Live Graph) ──────────────────────────────────

from llm_service import generate_with_llm, get_client
from google.genai import types
from bs4 import BeautifulSoup

def fetch_article_text(url: str) -> str:
    """Fetches the main text content of an article given its URL."""
    try:
        import httpx
        from bs4 import BeautifulSoup
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            try:
                resp = client.get(url, headers=headers)
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')
                text = " ".join([p.get_text() for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])])
                
                if len(text.strip()) > 100:
                    return text[:8000]
            except Exception as e:
                logger.warning(f"Primary fetch failed for {url}: {e}")

            # Fallback to Jina Reader API
            jina_url = f"https://r.jina.ai/{url}"
            resp = client.get(jina_url, headers=headers)
            if resp.status_code == 200 and len(resp.text.strip()) > 50:
                return resp.text[:8000]
                
            return "Not enough content extracted or page blocked."
    except Exception as e:
        return f"Failed to extract text: {e}"

async def generate_trend_summary(url: str, title: str) -> str:
    client = get_client()
    system_instruction = "You are an AI research agent. Your task is to fetch the provided URL using your tools and write a concise 3-5 point pointwise summary. Format with Markdown bullets."
    user_prompt = f"Please fetch the article at this URL and provide a pointwise summary.\nTitle: {title}\nURL: {url}"
    
    chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=[fetch_article_text],
            temperature=0.7,
        )
    )
    
    try:
        import asyncio
        response = await asyncio.to_thread(chat.send_message, user_prompt)
        text = response.text.strip() if response.text else ""
        return text
    except Exception as e:
        logger.error(f"Generate trend summary via agent failed: {e}")
        return "Failed to run agent summarization."


async def generate_trend_graph_data(trends: List[Dict], topic: str) -> Dict:
    system_prompt = "You are a trend analysis AI. You examine a list of current trends and generate a plausible 7-day historical heatmap dataset for data visualization."
    
    titles = "\\n".join([f"- {t.get('title', '')} ({t.get('source', '')})" for t in trends[:10]])
    user_prompt = f"""Based on the current hot topics for '{topic}', generate a 7-day trailing heat/relevance graph dataset representing how much traction this topic got across platforms.
Here are the current top articles:
{titles}

Return ONLY a valid JSON object matching this schema. The values for platform heat should be integers representing daily engagement volume (0-100 per platform):
{{
  "historical": [
    {{
      "date": "Day 1",
      "platforms": {{
        "X": 20,
        "Google News": 45,
        "HackerNews": 10,
        "Dev.to": 5
      }}
    }},
    ...
    {{
      "date": "Today",
      "platforms": {{ ... }}
    }}
  ]
}}
Do NOT use markdown fences around the JSON. Just return raw JSON text. Make the data curve look realistic for a trending topic across multiple platforms."""

    try:
        json_output = await generate_with_llm(system_prompt, user_prompt, max_tokens=600, temperature=0.7)
        # Strip markdown fences if Gemini added them
        json_output = json_output.strip()
        if json_output.startswith("```"):
            json_output = json_output.split("```")[1]
            if json_output.startswith("json"):
                json_output = json_output[4:]
        
        import json
        return json.loads(json_output.strip())
    except Exception as e:
        logger.error(f"Failed to generate graph data: {e}")
        # Default fallback graph
        return {"historical": [{"date": f"Day {i}", "heat": 10*i} for i in range(1,8)]}