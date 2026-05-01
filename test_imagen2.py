import asyncio
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)

async def test():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    prompt = "A high quality Instagram carousel background image."
    try:
        result = await asyncio.to_thread(
            client.models.generate_images,
            model='imagen-3.0-generate-002',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="1:1"
            )
        )
        print("Success!")
    except Exception as e:
        print("Error:", e)

asyncio.run(test())
