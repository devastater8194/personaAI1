import asyncio
from supabase_client import get_admin_db

async def test():
    db = get_admin_db()
    res = db.table("identities").select("user_id, name").execute()
    print("Identities:", res.data)

asyncio.run(test())
