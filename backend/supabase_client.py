import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client = None
_admin_client: Client = None

def get_db() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("Supabase credentials not found")
        _client = create_client(url, key)
    return _client

def get_admin_db() -> Client:
    global _admin_client
    if _admin_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            import warnings
            warnings.warn("SUPABASE_SERVICE_KEY not set - falling back to anon key")
            return get_db()
        _admin_client = create_client(url, key)
    return _admin_client
