import asyncio
import logging
from llm_service import get_embedding
from supabase_client import get_admin_db

logging.basicConfig(level=logging.INFO)

async def test():
    db = get_admin_db()
    res = db.table("identities").select("user_id, name").execute()
    print("Identities in DB:", res.data)
    
    emb = await get_embedding("Hello world")
    print("Embedding length:", len(emb))
    if all(x == 0.0 for x in emb):
        print("Embedding is all zeros! It failed.")

asyncio.run(test())
