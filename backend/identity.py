from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from supabase_client import get_db, get_admin_db
from llm_service import get_embedding

router = APIRouter()


class IdentityPayload(BaseModel):
    user_id: str    
    name: str
    age: Optional[int] = None
    domain: Optional[str] = ""
    role: Optional[str] = ""
    qualification: Optional[str] = ""
    journey: Optional[str] = ""
    interests: Optional[str] = ""
    hobbies: Optional[str] = ""
    achievements: Optional[str] = ""
    tones: Optional[List[str]] = []
    platforms: Optional[List[str]] = []


@router.post("/save")
async def save_identity(payload: IdentityPayload):
    db = get_admin_db()
    embed_text = f"{payload.name} {payload.domain} {payload.role} {payload.journey} {payload.interests}"

    try:
        embedding = await get_embedding(embed_text)
    except Exception as e:
        print(f"  Embedding failed (non-fatal): {e}")
        embedding = [0.0] * 768

    data = {
        "user_id":      payload.user_id,
        "name":         payload.name,
        "age":          payload.age,
        "domain":       payload.domain,
        "role":         payload.role,
        "qualification": payload.qualification,
        "journey":      payload.journey,
        "interests":    payload.interests,
        "hobbies":      payload.hobbies,
        "achievements": payload.achievements,
        "tones":        payload.tones,
        "platforms":    payload.platforms,
        "embedding":    embedding,
    }

    result = db.table("identities").upsert(data, on_conflict="user_id").execute()

    return {"success": True, "message": "Identity saved", "data": result.data}


@router.get("/check/{user_id}")
async def check_identity(user_id: str):
    """Lightweight check — returns {exists: bool} without raising HTTP errors."""
    db = get_admin_db()
    try:
        result = db.table("identities").select("user_id").eq("user_id", user_id).maybe_single().execute()
        if result is None:
            print(f"DEBUG: check_identity({user_id}) returned None result")
            return {"exists": False}
        return {"exists": bool(result.data)}
    except Exception as e:
        print(f"ERROR: check_identity({user_id}) failed: {e}")
        return {"exists": False}


@router.get("/{user_id}")
async def get_identity(user_id: str):
    """Retrieve identity profile by user_id."""
    db = get_admin_db()
    try:
        print(f"DEBUG: Fetching identity for {user_id}")
        # Use maybe_single() which returns data=None if no row is found
        response = db.table("identities").select("*").eq("user_id", user_id).maybe_single().execute()
        
        if not response or not hasattr(response, 'data') or response.data is None:
            print(f"DEBUG: No identity found for {user_id}")
            raise HTTPException(status_code=404, detail="Identity not found")
            
        return response.data

    except HTTPException:
        raise
    except Exception as e:
        print(f"ERROR: get_identity({user_id}) failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
