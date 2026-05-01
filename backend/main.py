from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
from identity import router as identity_router
from generate import router as generate_router
from trends import router as trends_router
from schedule import router as schedule_router
from notifications_service import router as notif_router
from auth import router as auth_router

app = FastAPI(
    title="Persona AI Content Engine",
    description="Identity-first content generation for LinkedIn, Instagram, X",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(identity_router, prefix="/api/identity", tags=["Identity"])
app.include_router(generate_router, prefix="/api/generate", tags=["Generate"])
app.include_router(trends_router,   prefix="/api/trends",   tags=["Trends"])
app.include_router(schedule_router, prefix="/api/schedule", tags=["Schedule"])
app.include_router(notif_router,    prefix="/api/notify",   tags=["Notifications"])
app.include_router(auth_router,     prefix="/api/auth",     tags=["Auth"])


@app.get("/")
async def root():
    return {"status": "Persona API running", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/stats/{user_id}")
async def get_stats(user_id: str):
    from supabase_client import get_admin_db
    db = get_admin_db()
    
    drafts_resp = db.table("content_drafts").select("status").eq("user_id", user_id).execute()
    drafts = drafts_resp.data or []
    
    pending_count = sum(1 for d in drafts if d.get("status") == "draft")
    approved_count = sum(1 for d in drafts if d.get("status") == "approved")
    scheduled_drafts = sum(1 for d in drafts if d.get("status") == "scheduled")
    posted_drafts = sum(1 for d in drafts if d.get("status") == "posted")
    total_drafts = len(drafts)
    
    try:
        trends_resp = db.table("trends_cache").select("id", count="exact").eq("user_id", user_id).execute()
        trends_count = trends_resp.count or 0
    except Exception:
        trends_count = 0

    try:
        scheduled_resp = db.table("scheduled_posts").select("scheduled_for", "platform").eq("user_id", user_id).eq("status", "pending").order("scheduled_for").limit(1).execute()
        next_scheduled = scheduled_resp.data[0] if scheduled_resp.data else None
    except Exception:
        next_scheduled = None

    return {
        "success": True,
        "total_drafts": total_drafts,
        "pending_count": pending_count,
        "approved_count": approved_count,
        "scheduled_count": scheduled_drafts,
        "posted_count": posted_drafts,
        "trends_count": trends_count,
        "next_scheduled": next_scheduled
    }
