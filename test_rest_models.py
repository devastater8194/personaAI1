import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}")
models = res.json().get("models", [])

for m in models:
    if "image" in m["name"].lower() or "gen" in m["name"].lower():
        print(m["name"], m.get("supportedGenerationMethods", []))
