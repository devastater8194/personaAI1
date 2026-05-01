# from fastapi import APIRouter, HTTPException
# from pydantic import BaseModel
# from typing import Optional, List
# import json

# from supabase_client import get_admin_db
# from llm_service import build_identity_system_prompt, generate_with_llm, generate_carousel_images

# router = APIRouter()


# class GenerateRequest(BaseModel):
#     user_id: str
#     topic: str
#     platform: str          # linkedin | instagram | twitter | all
#     content_type: str      # post | story | thread | opinion | educational


# class GenerateResponse(BaseModel):
#     platform: str
#     content: str
#     carousel_slides: Optional[list] = None
#     draft_id: Optional[str] = None


# @router.post("/", response_model=List[GenerateResponse])
# async def generate_content(req: GenerateRequest):

#     db = get_admin_db()

#     identity_result = db.table("identities").select("*").eq("user_id", req.user_id).maybe_single().execute()

#     if not identity_result or not getattr(identity_result, "data", None):
#         # Auto-create a minimal placeholder so users are never blocked.
#         # Uses upsert with a zero-vector — safe, no embedding call that could fail.
#         try:
#             db.table("identities").upsert(
#                 {
#                     "user_id": req.user_id,
#                     "name": "User",
#                     "domain": "",
#                     "role": "",
#                     "embedding": [0.0] * 768,
#                 },
#                 on_conflict="user_id",
#             ).execute()
#         except Exception as e:
#             # If upsert fails (e.g. RLS), still continue with a minimal dict
#             # so generation is never fully blocked.
#             return await _generate_with_identity(
#                 req, {"user_id": req.user_id, "name": "User", "domain": "", "role": ""}, db
#             )
#         identity_result = db.table("identities").select("*").eq("user_id", req.user_id).maybe_single().execute()

#     identity = identity_result.data if identity_result and identity_result.data else {
#         "user_id": req.user_id, "name": "User", "domain": "", "role": ""
#     }
#     system_prompt = build_identity_system_prompt(identity)

#     platforms = ["linkedin", "instagram", "twitter"] if req.platform == "all" else [req.platform]
    
#     async def generate_for_platform(platform: str):
#         platform_instruction = {
#             "linkedin": f"""Write a LINKEDIN post about the topic below.

# LINKEDIN-SPECIFIC REQUIREMENTS:
# - Write 250-400 words. This is NOT optional — short LinkedIn posts get buried.
# - First line = powerful hook that makes people click "...see more".
# - Use single-line paragraphs with blank lines between them (LinkedIn formatting).
# - Include a personal angle — reference my real experience in {identity.get('domain')}.
# - End with an engaging question or clear CTA to drive comments.
# - Add 3-5 relevant hashtags at the very end.
# - Use 2-3 emojis as visual markers, not decoration.
# - NO markdown (no bold, no headers). LinkedIn doesn't render markdown.
# - Make it feel like I just sat down and typed this from the heart.""",

#             "instagram": f"""Write an INSTAGRAM CAROUSEL post about the topic below.

# INSTAGRAM-SPECIFIC REQUIREMENTS:
# - Return ONLY a raw JSON object. No markdown fences, no explanation text.
# - Format MUST be exactly:
#   {{
#     "caption": "Your engaging caption with hashtags and emojis...",
#     "slides": [{{"slide":1,"title":"...","body":"...","emoji":"..."}}]
#   }}
# - Include 7-10 slides for maximum swipe-through and engagement.
# - Slide 1: Bold, curiosity-driven hook title (5-8 words) + teaser body (15-25 words).
# - Slides 2-8: ONE clear insight per slide. Title = 4-8 words. Body = 30-60 words.
#   Each slide should create a cliffhanger that makes people swipe.
# - Second-to-last slide: Quick summary of key takeaways.
# - Last slide: Strong CTA — "Save this 🔖", "Share with a friend", "Follow for more".
# - Use emojis that match each slide's content.
# - Write in Instagram voice — punchy, bold, value-packed, conversational.
# - Reference my expertise in {identity.get('domain')} to build authority.""",

#             "twitter": f"""Write a TWITTER/X THREAD about the topic below.

# TWITTER-SPECIFIC REQUIREMENTS:
# - Write a thread of 8-12 tweets. More tweets = more visibility on X.
# - Number each tweet: (1/N), (2/N) etc. at the START.
# - Each tweet MUST be under 280 characters — this is a hard limit.
# - Tweet 1: BANGER hook. End with 🧵 or "A thread 👇".
# - Tweets 2-3: Set up the problem or context. Build tension.
# - Tweets 4-9: Core insights, ONE per tweet. Short, punchy, opinionated.
# - Tweet 10-11: Personal lesson or hot take from my experience in {identity.get('domain')}.
# - Last tweet: CTA — "Follow for more" or "RT if this resonated 🔄".
# - Separate each tweet with a blank line.
# - Write like you talk — contractions, fragments, attitude, conviction.
# - Use 1-2 emojis per tweet max. Be strategic, not decorative."""
#         }.get(platform, "Write a social media post.")

#         content_type_instruction = {
#             "post": f"""
# CONTENT STYLE: Standard Professional Post
# Write a well-structured, insightful post that showcases thought leadership.
# Share a specific insight, lesson, or perspective from my experience as {identity.get('role', 'a professional')}.
# Make it substantial — not a throwaway thought. This should be something worth reading twice.""",

#             "story": f"""
# CONTENT STYLE: Personal Story / Narrative
# Tell a REAL-feeling personal story from my career journey in {identity.get('domain')}.
# Structure: Setup → Challenge/Conflict → What I learned → Takeaway for the reader.
# Include specific details (emotions, moments, dialogue if natural) to make it vivid and relatable.
# This should read like a memoir excerpt, not a generic "lessons learned" post.""",

#             "thread": f"""
# CONTENT STYLE: Thread / Breakdown
# Create a numbered breakdown with clear logical progression.
# Each point should build on the previous one. Start broad, go specific.
# Include practical examples and actionable insights from my field ({identity.get('domain')}).
# Make each point standalone-valuable but collectively tell a bigger story.""",

#             "opinion": f"""
# CONTENT STYLE: Bold Hot Take / Opinion
# Take a STRONG, potentially controversial stance on the topic.
# Don't hedge — commit to the opinion. Use conviction language.
# Back it up with my real experience in {identity.get('domain')} as evidence.
# Challenge conventional wisdom. Make people want to agree OR argue in the comments.
# This should spark debate, not just head-nods.""",

#             "educational": f"""
# CONTENT STYLE: Educational / How-To
# Teach something genuinely valuable, step by step.
# Draw from my expertise in {identity.get('domain')} and my role as {identity.get('role', 'a professional')}.
# Use concrete examples, not abstract principles.
# Structure it so someone can immediately apply what they learned.
# Include insider knowledge or non-obvious tips that only someone with real experience would know."""
#         }.get(req.content_type, "")

#         user_prompt = f"""{platform_instruction}

# {content_type_instruction}

# TOPIC: {req.topic}

# CRITICAL: Write as {identity.get('name')}. First person. Authentic voice. 
# Reference my background in {identity.get('domain')} naturally — don't force it.
# Make this content so good that someone would save it, share it, or come back to read it again.
# """

#         try:
#             content = await generate_with_llm(system_prompt, user_prompt)
#         except Exception as e:
#             raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

#         carousel_slides = None
#         if platform == "instagram":
#             try:
#                 clean = content.strip().replace("```json", "").replace("```", "").strip()
#                 parsed_json = json.loads(clean)
#                 if isinstance(parsed_json, dict) and "slides" in parsed_json:
#                     carousel_slides = parsed_json["slides"]
#                     content = parsed_json.get("caption", "Instagram Caption missing.")
#                 else:
#                     carousel_slides = parsed_json if isinstance(parsed_json, list) else None
#             except json.JSONDecodeError:
#                 carousel_slides = None

#         draft_data = {
#             "user_id":       req.user_id,
#             "platform":      platform,
#             "content_type":  req.content_type,
#             "content":       content,
#             "topic":         req.topic,
#             "status":        "draft",
#             "carousel_slides": carousel_slides
#         }
#         # Insert using the db instance passed down or retrieved
#         db_instance = get_admin_db()
#         saved = db_instance.table("content_drafts").insert(draft_data).execute()
#         draft_id = saved.data[0]["id"] if saved.data else None

#         return GenerateResponse(
#             platform=platform,
#             content=content,
#             carousel_slides=carousel_slides,
#             draft_id=draft_id
#         )

#     import asyncio
#     tasks = [generate_for_platform(p) for p in platforms]
#     results = await asyncio.gather(*tasks)
#     return list(results)


# async def _generate_with_identity(req: "GenerateRequest", identity: dict, db):
#     """Internal helper — runs generation with a pre-built identity dict."""
#     # Re-use the same logic by patching req.user_id lookup inline
#     # (this is only hit when the DB upsert itself fails, extremely rare)
#     from llm_service import build_identity_system_prompt, generate_with_llm
#     system_prompt = build_identity_system_prompt(identity)
#     platform = req.platform if req.platform != "all" else "linkedin"
#     user_prompt = f"Write a {req.content_type} post about: {req.topic}"
#     try:
#         content = await generate_with_llm(system_prompt, user_prompt)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")
#     return [GenerateResponse(platform=platform, content=content)]


# class ImageGenRequest(BaseModel):
#     draft_id: str

# @router.post("/images")
# async def generate_images_endpoint(req: ImageGenRequest):
#     """Generates images for an instagram carousel draft."""
#     db = get_admin_db()
#     draft = db.table("content_drafts").select("*").eq("id", req.draft_id).single().execute()
#     if not draft.data:
#         raise HTTPException(status_code=404, detail="Draft not found")
        
#     slides = draft.data.get("carousel_slides")
#     if not slides:
#         raise HTTPException(status_code=400, detail="No slides found in this draft")

#     # Generate images via Gemini
#     try:
#         updated_slides = await generate_carousel_images(slides)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
        
#     # Update DB
#     db.table("content_drafts").update({"carousel_slides": updated_slides}).eq("id", req.draft_id).execute()
    
#     return {"success": True, "carousel_slides": updated_slides}


# @router.get("/drafts/{user_id}")
# async def get_drafts(user_id: str, status: Optional[str] = None):
#     """Get all drafts for a user, optionally filtered by status."""
#     db = get_admin_db()
#     query = db.table("content_drafts").select("*").eq("user_id", user_id).order("created_at", desc=True)
#     if status:
#         query = query.eq("status", status)
#     result = query.execute()
#     return result.data or []


# @router.get("/history/{user_id}")
# async def get_content_history(user_id: str, limit: int = 20):
#     """Get all content ever generated for a user — all statuses, newest first."""
#     db = get_admin_db()
#     result = (
#         db.table("content_drafts")
#         .select("id, platform, content_type, topic, status, created_at, content")
#         .eq("user_id", user_id)
#         .order("created_at", desc=True)
#         .limit(limit)
#         .execute()
#     )
#     return result.data or []


# @router.patch("/approve/{draft_id}")
# async def approve_draft(draft_id: str):
#     """Approve a draft — moves it to scheduling queue."""
#     db = get_admin_db()
#     result = db.table("content_drafts").update({"status": "approved"}).eq("id", draft_id).execute()
#     return {"success": True, "draft": result.data}


# class UpdateDraftRequest(BaseModel):
#     content: str
#     carousel_slides: Optional[list] = None

# @router.patch("/draft/{draft_id}")
# async def update_draft(draft_id: str, req: UpdateDraftRequest):
#     """Update a draft's text content (and optionally carousel slides)."""
#     db = get_admin_db()
#     update_data = {"content": req.content}
#     if req.carousel_slides is not None:
#         update_data["carousel_slides"] = req.carousel_slides
        
#     result = db.table("content_drafts").update(update_data).eq("id", draft_id).execute()
#     return {"success": True, "draft": result.data}


# @router.delete("/draft/{draft_id}")
# async def delete_draft(draft_id: str):
#     db = get_admin_db()
#     db.table("content_drafts").delete().eq("id", draft_id).execute()
#     return {"success": True}


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json

from supabase_client import get_admin_db
from llm_service import build_identity_system_prompt, generate_with_llm, generate_carousel_images

router = APIRouter()


class GenerateRequest(BaseModel):
    user_id: str
    topic: str
    platform: str          # linkedin | instagram | twitter | all
    content_type: str      # post | story | thread | opinion | educational


class GenerateResponse(BaseModel):
    platform: str
    content: str
    carousel_slides: Optional[list] = None
    draft_id: Optional[str] = None


@router.post("/", response_model=List[GenerateResponse])
async def generate_content(req: GenerateRequest):

    db = get_admin_db()

    identity_result = db.table("identities").select("*").eq("user_id", req.user_id).maybe_single().execute()
    if not identity_result or not getattr(identity_result, "data", None):
        raise HTTPException(status_code=404, detail="Identity not found. Save your profile first.")

    identity = identity_result.data
    system_prompt = build_identity_system_prompt(identity)

    platforms = ["linkedin", "instagram", "twitter"] if req.platform == "all" else [req.platform]

    # ✅ SINGLE COMBINED PROMPT (IMPROVED)
    combined_prompt = f"""
You are the personal AI ghostwriter for {identity.get('name')}. 
Your goal is to transform the topic below into high-engagement content for {platforms}.

TOPIC: {req.topic}
CONTENT TYPE: {req.content_type}

STRICT GUIDELINES:
1. VOICE: Write 100% in {identity.get('name')}'s voice. Use their background in {identity.get('domain')} to provide unique insights.
2. NATURAL FLOW: Avoid AI cliches. No "In the ever-evolving landscape", no "Unlock your potential". Write like a human having a conversation.
3. PLATFORM OPTIMIZATION:
   - LinkedIn: Professional, story-driven, value-packed.
   - Twitter: Punchy, opinionated, thread format.
   - Instagram: Visual, emoji-friendly, helpful carousel slides.
4. FORMAT: Return ONLY valid JSON.

JSON STRUCTURE:
{{
  "linkedin": "A 300-word LinkedIn post...",
  "twitter": "(1/N) Tweet 1...\n\n(2/N) Tweet 2...",
  "instagram": {{
    "caption": "The IG caption...",
    "carousel": [
      {{"title": "Slide 1 Title", "body": "Slide 1 text..."}},
      {{"title": "Slide 2 Title", "body": "Slide 2 text..."}}
    ]
  }}
}}
"""

    try:
        response = await generate_with_llm(system_prompt, combined_prompt)
        clean = response.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(clean)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM error: {str(e)}")

    results = []

    all_draft_data = []
    
    for platform in platforms:
        content = None
        carousel_slides = None

        if platform == "instagram":
            ig_data = data.get("instagram", {})
            content = ig_data.get("caption")
            carousel_slides = ig_data.get("carousel")
        else:
            content = data.get(platform)

        if not content:
            continue

        all_draft_data.append({
            "user_id":       req.user_id,
            "platform":      platform,
            "content_type":  req.content_type,
            "content":       content,
            "topic":         req.topic,
            "status":        "draft",
            "carousel_slides": carousel_slides
        })

    if not all_draft_data:
        return []

    # ✅ BATCH INSERT (Optimized)
    saved = db.table("content_drafts").insert(all_draft_data).execute()
    saved_rows = saved.data if saved.data else []
    
    # Map saved IDs back to results
    results = []
    for i, draft in enumerate(all_draft_data):
        draft_id = saved_rows[i]["id"] if i < len(saved_rows) else None
        results.append(GenerateResponse(
            platform=draft["platform"],
            content=draft["content"],
            carousel_slides=draft["carousel_slides"],
            draft_id=draft_id
        ))

    return results


class ImageGenRequest(BaseModel):
    draft_id: str


@router.post("/images")
async def generate_images_endpoint(req: ImageGenRequest):
    db = get_admin_db()

    draft = db.table("content_drafts").select("*").eq("id", req.draft_id).single().execute()
    if not draft.data:
        raise HTTPException(status_code=404, detail="Draft not found")

    slides = draft.data.get("carousel_slides")
    if not slides:
        raise HTTPException(status_code=400, detail="No slides found in this draft")

    try:
        updated_slides = await generate_carousel_images(slides)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")

    db.table("content_drafts").update({"carousel_slides": updated_slides}).eq("id", req.draft_id).execute()

    return {"success": True, "carousel_slides": updated_slides}


@router.get("/drafts/{user_id}")
async def get_drafts(user_id: str, status: Optional[str] = None):
    db = get_admin_db()
    query = db.table("content_drafts").select("*").eq("user_id", user_id).order("created_at", desc=True)

    if status:
        query = query.eq("status", status)

    result = query.execute()
    return result.data


@router.patch("/approve/{draft_id}")
async def approve_draft(draft_id: str):
    db = get_admin_db()
    result = db.table("content_drafts").update({"status": "approved"}).eq("id", draft_id).execute()
    return {"success": True, "draft": result.data}


@router.delete("/draft/{draft_id}")
async def delete_draft(draft_id: str):
    db = get_admin_db()
    db.table("content_drafts").delete().eq("id", draft_id).execute()
    return {"success": True}


@router.get("/history/{user_id}")
async def get_content_history(user_id: str, limit: int = 20):
    """Get all content ever generated for a user — all statuses, newest first."""
    db = get_admin_db()
    result = (
        db.table("content_drafts")
        .select("id, platform, content_type, topic, status, created_at, content")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []