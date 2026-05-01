import asyncio
import logging
from llm_service import generate_carousel_images

logging.basicConfig(level=logging.INFO)

async def test():
    slides = [
        {"slide": 1, "title": "Test Slide", "body": "This is a test slide."}
    ]
    
    try:
        updated = await generate_carousel_images(slides)
        print("Updated slides:", updated)
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
