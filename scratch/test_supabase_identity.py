import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")

print(f"URL: {url}")
print(f"Key set: {bool(key)}")

if not url or not key:
    print("Missing credentials")
    exit(1)

db = create_client(url, key)
user_id = "test_user_id"

try:
    print(f"Attempting to fetch identity for {user_id}...")
    result = db.table("identities").select("*").eq("user_id", user_id).maybe_single().execute()
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    if result:
        print(f"Data: {result.data}")
except Exception as e:
    print(f"Error: {e}")
