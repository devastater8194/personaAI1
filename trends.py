# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from typing import Optional
# from supabase_client import get_db
# from trends_service import fetch_all_trends
# from notifications_service import send_push_notification, send_trend_alert_email

# router = APIRouter()


# class TrendAlertRequest(BaseModel):
#     user_id: str
#     fcm_token: Optional[str] = None
#     email: Optional[str] = None


# @router.get("/{user_id}")
# async def get_trends(user_id: str):
#     db = get_db()

#     identity = db.table("identities").select("domain,interests,name").eq("user_id", user_id).maybe_single().execute()
#     if not identity or not getattr(identity, "data", None):
#         raise HTTPException(status_code=404, detail="Identity not found. Save your profile first.")

#     domain    = identity.data.get("domain", "technology")
#     interests = identity.data.get("interests", "")

#     trends = await fetch_all_trends(domain, interests)

#     if trends:
#         cache_rows = [{
#             "user_id":         user_id,
#             "title":           t["title"],
#             "source":          t["source"],
#             "tag":             t.get("tag", ""),
#             "relevance_score": t.get("relevance_score", 0.8),
#             "url":             t.get("url", ""),
#         } for t in trends]

#         try:
#             db.table("trends_cache").delete().eq("user_id", user_id).execute()
#             db.table("trends_cache").insert(cache_rows).execute()
#         except Exception:
#             pass

#     return {"trends": trends, "count": len(trends)}


# @router.post("/alert")
# async def send_trend_alert(req: TrendAlertRequest, trend_title: str, trend_source: str):
#     db = get_db()
#     identity = db.table("identities").select("name").eq("user_id", req.user_id).maybe_single().execute()
#     user_name = identity.data.get("name", "there") if identity and getattr(identity, "data", None) else "there"

#     if req.fcm_token:
#         await send_push_notification(
#             fcm_token=req.fcm_token,
#             title="Trending in your niche!",
#             body=trend_title[:100],
#             data={"type": "trend_alert", "source": trend_source}
#         )

#     if req.email:
#         await send_trend_alert_email(
#             to_email=req.email,
#             user_name=user_name,
#             trend_title=trend_title,
#             trend_source=trend_source
#         )

#     return {"success": True, "notified_via": {"push": bool(req.fcm_token), "email": bool(req.email)}}
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from supabase_client import get_admin_db
from trends_service import fetch_all_trends
from notifications_service import send_push_notification, send_trend_alert_email
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class TrendAlertRequest(BaseModel):
    user_id: str
    fcm_token: Optional[str] = None
    email: Optional[str] = None


@router.get("/{user_id}")
async def get_trends(user_id: str, topic: Optional[str] = None):
    db = get_admin_db()  # service role — bypasses RLS on trends_cache writes

    # ── Load identity ─────────────────────────────────────────────────────────
    identity = (
        db.table("identities")
        .select("domain,interests,name")
        .eq("user_id", user_id)
        .maybe_single()
        .execute()
    )

    if topic:
        domain = topic
        interests = ""
        logger.info(f"[trends] Fetching for user={user_id} topic='{topic}'")
    else:
        if identity and getattr(identity, "data", None):
            domain = identity.data.get("domain") or "technology"
            interests = identity.data.get("interests") or ""
        else:
            domain = "technology"
            interests = ""
        logger.info(f"[trends] Fetching for user={user_id} domain='{domain}'")

    # ── Fetch live trends ─────────────────────────────────────────────────────
    try:
        trends = await fetch_all_trends(domain, interests)
    except Exception as e:
        logger.error(f"[trends] fetch_all_trends failed: {e}")
        # Don't crash — fall back to whatever is cached
        trends = []

    # ── If live fetch returned nothing, serve from cache ─────────────────────
    if not trends:
        logger.warning("[trends] Live fetch empty — serving from cache")
        try:
            cached = (
                db.table("trends_cache")
                .select("*")
                .eq("user_id", user_id)
                .order("relevance_score", desc=True)
                .limit(20)
                .execute()
            )
            cached_trends = cached.data or []
            return {"trends": cached_trends, "count": len(cached_trends), "source": "cache"}
        except Exception as e:
            logger.error(f"[trends] Cache read failed: {e}")
            return {"trends": [], "count": 0, "source": "cache"}

    # ── Cache the fresh results ───────────────────────────────────────────────
    try:
        cache_rows = [
            {
                "user_id":         user_id,
                "title":           t["title"],
                "source":          t["source"],
                "tag":             t.get("tag", ""),
                "relevance_score": t.get("relevance_score", 0.8),
                "url":             t.get("url", ""),
            }
            for t in trends
        ]
        db.table("trends_cache").delete().eq("user_id", user_id).execute()
        db.table("trends_cache").insert(cache_rows).execute()
        logger.info(f"[trends] Cached {len(cache_rows)} trends for user={user_id}")
    except Exception as e:
        # Non-fatal — trends still return even if caching fails
        logger.error(f"[trends] Cache write failed: {e}")

    return {"trends": trends, "count": len(trends), "source": "live"}


class TrendSummaryRequest(BaseModel):
    url: str
    title: str

class TrendGraphRequest(BaseModel):
    topic: str
    trends: list


@router.post("/summary")
async def get_trend_summary(req: TrendSummaryRequest):
    from trends_service import generate_trend_summary
    summary = await generate_trend_summary(req.url, req.title)
    return {"summary": summary}


@router.post("/graph")
async def get_trend_graph(req: TrendGraphRequest):
    from trends_service import generate_trend_graph_data
    graph_data = await generate_trend_graph_data(req.trends, req.topic)
    return graph_data


@router.post("/alert")
async def send_trend_alert(req: TrendAlertRequest, trend_title: str, trend_source: str):
    db = get_admin_db()
    identity = (
        db.table("identities")
        .select("name")
        .eq("user_id", req.user_id)
        .maybe_single()
        .execute()
    )
    user_name = (
        identity.data.get("name", "there")
        if identity and getattr(identity, "data", None)
        else "there"
    )

    if req.fcm_token:
        await send_push_notification(
            fcm_token=req.fcm_token,
            title="Trending in your niche!",
            body=trend_title[:100],
            data={"type": "trend_alert", "source": trend_source},
        )

    if req.email:
        await send_trend_alert_email(
            to_email=req.email,
            user_name=user_name,
            trend_title=trend_title,
            trend_source=trend_source,
        )

    return {
        "success": True,
        "notified_via": {"push": bool(req.fcm_token), "email": bool(req.email)},
    }