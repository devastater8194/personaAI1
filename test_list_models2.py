import logging
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    for m in client.models.list():
        if "image" in m.name.lower() or "generate" in m.name.lower():
            print(m.name)
except Exception as e:
    print("Error listing models:", e)
