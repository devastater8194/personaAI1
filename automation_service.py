import asyncio
import logging
from datetime import datetime, timedelta
from supabase_client import get_admin_db
from trends_service import fetch_all_trends
from generate import generate_content, GenerateRequest
from schedule import auto_schedule

logger = logging.getLogger(__name__)

async def automate_user_onboarding(user_id: str):
    """
    Fully automated flow:
    1. Fetch top 7 trends for the user's field.
    2. Generate 7 days of content (one platform per day, rotating).
    3. Auto-schedule all generated posts.
    """
    logger.info(f"[automation] Starting full automation for user: {user_id}")
    db = get_admin_db()

    # 1. Get identity
    identity_res = db.table("identities").select("*").eq("user_id", user_id).maybe_single().execute()
    if not identity_res.data:
        logger.error(f"[automation] Identity not found for {user_id}")
        return

    identity = identity_res.data
    domain = identity.get("domain", "technology")
    interests = identity.get("interests", "")

    # 2. Fetch trends
    try:
        trends = await fetch_all_trends(domain, interests)
        # Filter top 7
        top_trends = trends[:7]
        logger.info(f"[automation] Fetched {len(trends)} total trends, using top {len(top_trends)}")
        
        # ✅ CACHE TRENDS (So they appear in the UI)
        if top_trends:
            cache_rows = [
                {
                    "user_id":         user_id,
                    "title":           t["title"],
                    "source":          t["source"],
                    "tag":             t.get("tag", ""),
                    "relevance_score": t.get("relevance_score", 0.8),
                    "url":             t.get("url", ""),
                }
                for t in top_trends
            ]
            try:
                db.table("trends_cache").delete().eq("user_id", user_id).execute()
                db.table("trends_cache").insert(cache_rows).execute()
                logger.info(f"[automation] Cached {len(cache_rows)} trends for user={user_id}")
            except Exception as e:
                logger.error(f"[automation] Trend cache write failed: {e}")

    except Exception as e:
        logger.error(f"[automation] Trend fetch failed: {e}")
        return

    if not top_trends:
        logger.warning(f"[automation] No trends found for {user_id}")
        return

    # 3. Generate and Schedule for each trend
    platforms = ["linkedin", "twitter", "instagram"]
    content_types = ["post", "thread", "educational", "opinion", "story"]
    
    for i, trend in enumerate(top_trends):
        platform = platforms[i % len(platforms)]
        content_type = content_types[i % len(content_types)]
        topic = trend.get("title")
        
        # Add delay to avoid rate limiting (especially on free tier)
        if i > 0:
            logger.info(f"[automation] Waiting 15 seconds before next generation...")
            await asyncio.sleep(15)
        
        logger.info(f"[automation] Generating {platform} {content_type} for trend: {topic}")
        
        try:
            req = GenerateRequest(
                user_id=user_id,
                topic=topic,
                platform=platform,
                content_type=content_type
            )
            
            # Generate content with basic retry logic
            results = None
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"[automation] Generating content for {platform} (attempt {attempt+1})...")
                    results = await generate_content(req)
                    break
                except Exception as e:
                    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                        wait_time = (attempt + 1) * 30
                        logger.warning(f"[automation] Rate limited. Waiting {wait_time}s before retry...")
                        await asyncio.sleep(wait_time)
                    else:
                        raise e

            if results:
                for res in results:
                    if res.draft_id:
                        # Auto-schedule
                        try:
                            sched_res = await auto_schedule(res.draft_id)
                            logger.info(f"[automation] Scheduled {platform} post for {sched_res.get('scheduled_for')}")
                        except Exception as e:
                            logger.error(f"[automation] Scheduling failed for draft {res.draft_id}: {e}")
            
        except Exception as e:
            logger.error(f"[automation] Generation failed for trend '{topic}': {e}")
            continue

    logger.info(f"[automation] Completed full automation for user: {user_id}")
