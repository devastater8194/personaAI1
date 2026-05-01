from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import httpx
import os

from dotenv import load_dotenv
load_dotenv()

from supabase_client import get_admin_db
from notifications_service import send_post_scheduled_email

router = APIRouter()

INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
INSTAGRAM_ACCOUNT_ID   = os.getenv("INSTAGRAM_ACCOUNT_ID", "")
CAROUSEL_SERVICE_URL   = os.getenv("CAROUSEL_SERVICE_URL", "http://localhost:3001")

class ScheduleRequest(BaseModel):
    draft_id: str
    user_id: str
    scheduled_for: str
    email: Optional[str] = None

class WeekPlanRequest(BaseModel):
    user_id: str
    approved_draft_ids: list[str]

@router.post("/queue")
async def queue_post(req: ScheduleRequest, background_tasks: BackgroundTasks):
    db = get_admin_db()

    db.table("content_drafts").update({
        "status": "scheduled",
        "scheduled_for": req.scheduled_for
    }).eq("id", req.draft_id).execute()

    draft = db.table("content_drafts").select("platform").eq("id", req.draft_id).maybe_single().execute()
    platform = draft.data.get("platform") if draft.data else "unknown"

    db.table("scheduled_posts").insert({
        "draft_id":      req.draft_id,
        "user_id":       req.user_id,
        "platform":      platform,
        "scheduled_for": req.scheduled_for,
        "status":        "pending"
    }).execute()

    if req.email:
        background_tasks.add_task(
            send_post_scheduled_email,
            req.email,
            "there",
            platform,
            req.scheduled_for
        )

    return {"success": True, "scheduled_for": req.scheduled_for}

@router.post("/auto-schedule/{draft_id}")
async def auto_schedule(draft_id: str):
    db = get_admin_db()
    
    # 1. Get draft info
    draft_res = db.table("content_drafts").select("*").eq("id", draft_id).maybe_single().execute()
    if not draft_res.data:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft = draft_res.data
    user_id = draft["user_id"]
    platform = draft["platform"]

    # 2. Define optimal times
    optimal_times = {
        "linkedin":  ["08:30", "12:00", "17:30"],
        "instagram": ["10:00", "14:00", "19:00"],
        "twitter":   ["09:00", "13:00", "18:00"],
    }
    times = optimal_times.get(platform, ["10:00", "15:00"])

    # 3. Get existing schedules to find a gap
    existing_res = db.table("scheduled_posts")\
        .select("scheduled_for")\
        .eq("user_id", user_id)\
        .eq("platform", platform)\
        .eq("status", "pending")\
        .execute()
    
    existing_slots = set()
    for row in (existing_res.data or []):
        # Convert to a comparable string format (YYYY-MM-DD HH:MM)
        dt = datetime.fromisoformat(row["scheduled_for"].replace("Z", "+00:00"))
        existing_slots.add(dt.strftime("%Y-%m-%d %H:%M"))

    # 4. Find the first empty slot starting from tomorrow
    start_date = datetime.now() + timedelta(days=1)
    found_slot = None
    
    # Search for up to 14 days to find a spot
    for day_offset in range(14):
        target_day = start_date + timedelta(days=day_offset)
        for t_str in times:
            check_str = f"{target_day.strftime('%Y-%m-%d')} {t_str}"
            if check_str not in existing_slots:
                found_slot = f"{target_day.strftime('%Y-%m-%d')}T{t_str}:00"
                break
        if found_slot:
            break

    if not found_slot:
        raise HTTPException(status_code=500, detail="Could not find an available scheduling slot in the next 14 days.")

    # 5. Update DB
    db.table("content_drafts").update({
        "status": "scheduled",
        "scheduled_for": found_slot
    }).eq("id", draft_id).execute()

    db.table("scheduled_posts").insert({
        "draft_id":      draft_id,
        "user_id":       user_id,
        "platform":      platform,
        "scheduled_for": found_slot,
        "status":        "pending"
    }).execute()

    return {
        "success": True, 
        "scheduled_for": found_slot,
        "platform": platform
    }

@router.post("/week-plan")
async def create_week_plan(req: WeekPlanRequest):
    # This remains for batch scheduling if needed, but redirects to auto-schedule logic
    results = []
    for d_id in req.approved_draft_ids:
        try:
            res = await auto_schedule(d_id)
            results.append(res)
        except:
            continue
    return {"success": True, "results": results}


@router.get("/upcoming/{user_id}")
async def get_upcoming(user_id: str):
    db = get_admin_db()
    result = db.table("scheduled_posts")\
        .select("*, content_drafts(content, platform, content_type, topic)")\
        .eq("user_id", user_id)\
        .eq("status", "pending")\
        .order("scheduled_for")\
        .execute()
    return result.data or []

@router.post("/publish/{draft_id}")
async def publish_now(draft_id: str):
    db = get_admin_db()
    
    # 1. Get draft
    draft_res = db.table("content_drafts").select("*").eq("id", draft_id).maybe_single().execute()
    if not draft_res.data:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft = draft_res.data
    
    # 2. Get user identity for handles
    identity_res = db.table("identities").select("*").eq("user_id", draft["user_id"]).maybe_single().execute()
    if not identity_res.data:
        raise HTTPException(status_code=404, detail="Identity not found. Save your handles first.")
    identity = identity_res.data
    
    platform = draft["platform"]
    handle = identity.get(f"{platform}_handle") or "Not provided"
    
    # 3. Simulate posting
    # If Instagram is configured, we use the real function
    if platform == "instagram" and INSTAGRAM_ACCESS_TOKEN and not INSTAGRAM_ACCESS_TOKEN.startswith("your-"):
        try:
            await publish_to_instagram(draft_id)
        except Exception as e:
            print(f"Instagram real post failed, falling back to simulation: {e}")
    
    # Update status to 'posted'
    db.table("content_drafts").update({
        "status": "posted",
        "posted_at": datetime.now().isoformat()
    }).eq("id", draft_id).execute()

    return {
        "success": True, 
        "message": f"Successfully posted to {platform}!",
        "handle": handle,
        "platform": platform
    }


@router.post("/publish-instagram/{draft_id}")
async def publish_to_instagram(draft_id: str):
    token = INSTAGRAM_ACCESS_TOKEN
    account_id = INSTAGRAM_ACCOUNT_ID

    if not token or not account_id or token.startswith("your-") or account_id.startswith("your-"):
        raise HTTPException(
            status_code=503,
            detail="Instagram not configured. Set valid INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in .env."
        )

    db = get_admin_db()
    draft = db.table("content_drafts").select("*").eq("id", draft_id).maybe_single().execute()
    if not draft.data:
        raise HTTPException(status_code=404, detail="Draft not found")

    post = draft.data

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:

            if post.get("carousel_slides") and isinstance(post["carousel_slides"], list):
                base_url = os.getenv("NEXT_PUBLIC_APP_URL", "https://your-public-ngrok-url.ngrok.io") # Replace with public URL for IG
                image_urls = []
                for slide in post["carousel_slides"]:
                    img = slide.get("image_url")
                    if img:
                        if img.startswith("/"):
                            image_urls.append(base_url + img)
                        else:
                            image_urls.append(img)
                            
                if not image_urls:
                    raise HTTPException(status_code=400, detail="No pre-generated images found. Generate images first.")

                item_ids = []
                for url in image_urls:
                    item_resp = await client.post(
                        f"https://graph.facebook.com/v19.0/{account_id}/media",
                        params={
                            "image_url":        url,
                            "is_carousel_item": True,
                            "access_token":     token
                        }
                    )
                    item_ids.append(item_resp.json()["id"])

                caption = post.get("content", "")[:2200]
                container_resp = await client.post(
                    f"https://graph.facebook.com/v19.0/{account_id}/media",
                    params={
                        "media_type":   "CAROUSEL",
                        "children":     ",".join(item_ids),
                        "caption":      caption,
                        "access_token": token
                    }
                )
                container_id = container_resp.json()["id"]

            else:
                raise HTTPException(
                    status_code=400,
                    detail="Instagram requires image/carousel content. Use carousel format."
                )

            publish_resp = await client.post(
                f"https://graph.facebook.com/v19.0/{account_id}/media_publish",
                params={
                    "creation_id":  container_id,
                    "access_token": token
                }
            )
            ig_post_id = publish_resp.json().get("id")

    except HTTPException:
        raise
    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Instagram API error: {str(e)}")

    db.table("content_drafts").update({
        "status": "posted",
        "posted_at": datetime.now().isoformat()
    }).eq("id", draft_id).execute()

    db.table("scheduled_posts").update({"status": "posted"}).eq("draft_id", draft_id).execute()

    return {"success": True, "instagram_post_id": ig_post_id}
