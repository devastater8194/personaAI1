import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from automation_service import automate_user_onboarding
from supabase_client import get_admin_db

load_dotenv()

async def test_automation():
    user_id = "f8acfe8f-c2c3-4fe4-b1fd-6d7e7820e93f" 
    
    print(f"Starting automation test for user: {user_id}")
    
    start_time = datetime.now()
    try:
        await automate_user_onboarding(user_id)
        print("Automation completed successfully!")
        
        # Verify results in DB
        db = get_admin_db()
        # Filter by created_at > start_time
        drafts = db.table("content_drafts")\
            .select("platform, status, scheduled_for, topic, created_at")\
            .eq("user_id", user_id)\
            .gte("created_at", start_time.isoformat())\
            .order("created_at", desc=True)\
            .execute()
            
        print(f"Found {len(drafts.data)} NEW drafts in DB.")
        for d in drafts.data:
            print(f"- {d['platform']} | {d['status']} | {d['scheduled_for']} | Topic: {d['topic'][:30]}... | Created: {d['created_at']}")
            
    except Exception as e:
        print(f"Automation test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_automation())
