"""
Fix Sarthak's identity row - it was saved with a null embedding due to the 1536-dim bug.
We'll re-save it with a proper 768-dim embedding so generate works immediately.
"""
import asyncio
from supabase_client import get_admin_db
from llm_service import get_embedding

SARTHAK_USER_ID = "f8acfe8f-c2c3-4fe4-b1fd-6d7e7820e93f"

async def fix():
    db = get_admin_db()
    # Get existing row
    res = db.table("identities").select("*").eq("user_id", SARTHAK_USER_ID).maybe_single().execute()
    if not res.data:
        print("Row not found!")
        return

    row = res.data
    print(f"Found row: name={row['name']}, domain={row.get('domain')}, role={row.get('role')}")

    # Generate a proper embedding from whatever data already exists
    embed_text = f"{row.get('name','')} {row.get('domain','')} {row.get('role','')} {row.get('journey','')} {row.get('interests','')}"
    embedding = await get_embedding(embed_text)
    print(f"Generated embedding length: {len(embedding)}")

    # Patch just the embedding
    patch_res = db.table("identities").update({"embedding": embedding}).eq("user_id", SARTHAK_USER_ID).execute()
    print(f"Update result: {patch_res.data}")
    print("DONE: Sarthak identity row is now fixed!")

asyncio.run(fix())
