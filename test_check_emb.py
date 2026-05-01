import asyncio
from supabase_client import get_admin_db

async def test():
    db = get_admin_db()
    res = db.table("identities").select("user_id, name, embedding").execute()
    for row in res.data:
        emb = row.get("embedding")
        length = len(eval(emb)) if isinstance(emb, str) else (len(emb) if emb else 0)
        print(f"User: {row['name']} | ID: {row['user_id']} | Embedding length: {length}")

asyncio.run(test())
