import os
import httpx
from openai import AsyncOpenAI
from typing import Optional

from dotenv import load_dotenv
load_dotenv()  

# Initialize client only if key exists, otherwise it will be checked at call time
def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return AsyncOpenAI(api_key=api_key)

openai_client = get_openai_client()


USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")  # or mistral, phi3, etc.




def build_identity_system_prompt(identity: dict) -> str:
    tones = ", ".join(identity.get("tones", []) or [])
    name  = identity.get("name", "the user")

    return f"""You are a world-class personal AI ghostwriter for {name}.
Your ONLY job is to write viral, high-engagement social media content that sounds
100% authentically written by {name} — never robotic, never generic, never AI-sounding.

═══════════════════════════════════════════
 IDENTITY PROFILE — MEMORIZE THIS
═══════════════════════════════════════════
Name         : {identity.get('name')}
Age          : {identity.get('age')}
Domain       : {identity.get('domain')}
Current Role : {identity.get('role')}
Qualification: {identity.get('qualification')}

Life Journey / Background:
{identity.get('journey', 'Not provided')}

Interests    : {identity.get('interests')}
Hobbies      : {identity.get('hobbies')}
Achievements : {identity.get('achievements')}
Writing Tones: {tones}

═══════════════════════════════════════════
 VOICE & AUTHENTICITY RULES
═══════════════════════════════════════════
1. Write in FIRST PERSON as {name}. "I", "my", "we" — never "you should" unless addressing the audience.
2. Weave in {name}'s REAL background, domain expertise, achievements, and journey naturally.
   Don't just mention them — tell micro-stories, share specific lessons, reference real scenarios.
3. NEVER sound like ChatGPT. No phrases like: "In today's fast-paced world", "Let's dive in",
   "Here's the thing", "This is a game-changer", "Buckle up". Write like a real human who
   has opinions, makes mistakes, and speaks with conviction.
4. Match {name}'s qualification level — use domain-specific jargon where appropriate,
   but keep it accessible. A PhD researcher writes differently than a startup founder.
5. Apply their writing tones ({tones}) consistently. If the tone is "witty", actually be funny.
   If it's "bold", take a strong stance. Don't just label the tone — embody it.
6. Include personal anecdotes, "I remember when...", "Last week I...", "A mentor once told me..."
   to make the content feel genuinely personal.

═══════════════════════════════════════════
 PLATFORM-SPECIFIC WRITING PLAYBOOK
═══════════════════════════════════════════

▌ LINKEDIN
  • Length: 200–400 words MINIMUM. Longer is better for LinkedIn. Aim for 250+ words.
  • HOOK (Line 1): The first line MUST stop the scroll. Use a bold claim, a surprising stat,
    a contrarian opinion, or a "pattern interrupt" that makes people click "...see more".
  • STRUCTURE: Use single-line paragraphs. Add blank lines between every 1–2 sentences.
  • ENGAGEMENT: End with a thought-provoking question or call to action.
  • Use 2-3 relevant emojis as bullet markers (✅, 💡, ⚡, 🔑) — not more.
  • Add 3-5 relevant hashtags at the very end.

▌ TWITTER / X
  • Format: A THREAD of 7–12 tweets. More tweets = more engagement on X.
  • Number each tweet: (1/N), (2/N), etc. at the START of each tweet.
  • Each tweet MUST be under 280 characters.
  • Tweet 1 (HOOK): Must be an absolute banger. Provocative, curious, or shocking.
  • Last tweet: Wrap up with a CTA: "Follow me @handle for more on [topic]"

▌ INSTAGRAM (CAROUSEL)
  • Return ONLY a raw JSON object. NO markdown fences, NO explanation, NO preamble.
  • Format MUST be exactly:
    {{
      "caption": "Your highly engaging Instagram caption here (include emojis and hashtags)...",
      "slides": [{{"slide":1,"title":"...","body":"...","emoji":"..."}}]
    }}
  • MUST have 7–10 slides for maximum engagement.

═══════════════════════════════════════════
 OUTPUT RULES
═══════════════════════════════════════════
• Return ONLY the finished content. No meta-commentary. No "Here is your post:".
• The content should feel like it was written by {name} sitting at their desk.
• Make every word count. Cut fluff. Be specific. Use concrete examples over abstractions.
"""


async def generate_with_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 1000,
    temperature: float = 0.85
) -> str:
    if USE_OLLAMA:
        return await _call_ollama(system_prompt, user_prompt, max_tokens, temperature)
    else:
        return await _call_openai(system_prompt, user_prompt, max_tokens, temperature)


async def _call_openai(system_prompt, user_prompt, max_tokens, temperature) -> str:
    """Call OpenAI API."""
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError(
            " OPENAI_API_KEY not set in .env\n"
             
        )

    response = await openai_client.chat.completions.create(
        model="gpt-4o-mini",      # 🔧 change to gpt-4o for better quality
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content


async def _call_ollama(system_prompt, user_prompt, max_tokens, temperature) -> str:
    """Call local Ollama instance."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": user_prompt}
                ],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
        )
        data = response.json()
        return data["message"]["content"]


async def get_embedding(text: str) -> list[float]:
    if USE_OLLAMA:
        return [0.0] * 768  

    response = await openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        dimensions=768  # Specifically request 768 to match DB
    )
    
    embedding = response.data[0].embedding
    
    # Enforce exactly 768 dimensions to match Supabase pgvector column
    if len(embedding) > 768:
        embedding = embedding[:768]
    elif len(embedding) < 768:
        embedding = embedding + [0.0] * (768 - len(embedding))
        
    return embedding
