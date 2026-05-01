import asyncio
from llm_service import get_embedding

async def test():
    vec = await get_embedding("test")
    print(f"Embedding length: {len(vec)}")

asyncio.run(test())
