import asyncio
from generate import generate_content, GenerateRequest

async def test():
    req = GenerateRequest(
        user_id="f8acfe8f-c2c3-4fe4-b1fd-6d7e7820e93f",
        topic="AI in 2026",
        platform="linkedin",
        content_type="post"
    )
    try:
        results = await generate_content(req)
        for r in results:
            print("Generated:", r.platform, len(r.content), "chars")
            print("Content:", r.content[:100], "...")
    except Exception as e:
        print("Error during generation:", str(e))

asyncio.run(test())
