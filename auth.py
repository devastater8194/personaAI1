from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supabase_client import get_admin_db
import os

router = APIRouter()


class RegisterPayload(BaseModel):
    name: str
    email: str
    password: str


class LoginPayload(BaseModel):
    email: str
    password: str


@router.post("/register")
async def register(payload: RegisterPayload):

    try:
        from supabase_client import get_admin_db
        admin_supabase = get_admin_db()
        
        auth_response = admin_supabase.auth.admin.create_user({
            "email": payload.email,
            "password": payload.password,
            "email_confirm": True,
            "user_metadata": {
                "full_name": payload.name
            }
        })

        if auth_response.user is None:
            raise HTTPException(status_code=400, detail="Registration failed — check email/password")

        user_id = auth_response.user.id
 
        try:
            db = get_admin_db()
            db.table("identities").upsert({
                "user_id": user_id,
                "name": payload.name,
                "embedding": [0.0] * 768,
            }, on_conflict="user_id").execute()
        except Exception as e:
            print(f"  Identity row creation failed (non-fatal): {e}")

        return {
            "success": True,
            "user_id": user_id,
            "email": payload.email,
            "message": "Registration successful"
        }

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        if "already registered" in error_msg.lower() or "already been registered" in error_msg.lower():
            raise HTTPException(status_code=409, detail="This email is already registered. Try logging in instead.")
        raise HTTPException(status_code=400, detail=f"Registration failed: {error_msg}")


@router.post("/login")
async def login(payload: LoginPayload):
    """
    Login an existing user via Supabase Auth.
    """
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL") 
        key = os.getenv("SUPABASE_KEY")
        
        if not url or not key:
            raise HTTPException(status_code=500, detail="Supabase credentials not configured")
        
        supabase = create_client(url, key)
        
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })

        if auth_response.user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        return {
            "success": True,
            "user_id": auth_response.user.id,
            "email": auth_response.user.email,
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "message": "Login successful"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Login failed: {str(e)}")