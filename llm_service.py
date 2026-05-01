"""
llm_service.py — Google Gemini (google.genai SDK)
Uses Gemini 2.5 Flash and text-embedding-004.
"""

import os
import asyncio
import logging
import uuid
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

_client = None

def get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set in .env — "
                "get yours at: https://aistudio.google.com/app/apikey"
            )
        _client = genai.Client(api_key=api_key)
        logger.info("[llm] Gemini client initialised")
    return _client

# ── Identity system prompt ────────────────────────────────────────────────────

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
1. Write in FIRST PERSON as {name}. Use "I", "my", "we" — NEVER speak from an outsider's perspective.
2. SPEAK FROM EXPERIENCE: Weave in {name}'s REAL background and journey. If they are an expert in {identity.get('domain')}, show it through nuanced insights, not just buzzwords.
3. BE CONVERSATIONAL & NATURAL: Write like you're talking to a friend or a respected colleague. Use contractions. Use varying sentence lengths. Avoid the "AI rhythm" (all sentences being the same length).
4. NO CORPORATE JARGON: Avoid "leveraging", "synergy", "game-changer", "dive deep", "in today's world". If {name} wouldn't say it in a coffee shop, don't write it.
5. EMBODY THE TONE: If the tone is "{tones}", don't just add a few adjectives. Let the structure and attitude of the writing reflect that tone.
6. SHOW, DON'T TELL: Instead of saying "I am an expert in {identity.get('domain')}", share a specific problem you solved or a non-obvious observation you made.

═══════════════════════════════════════════
 PLATFORM-SPECIFIC WRITING PLAYBOOK
═══════════════════════════════════════════

▌ LINKEDIN
  • Goal: Thought leadership and professional connection.
  • Length: 250–450 words. Substantiate your claims.
  • HOOK: Start with a personal story, a contrarian take, or a vulnerable moment.
  • FORMAT: Use lots of white space. 1-2 sentences per paragraph. No markdown.
  • CTA: End with a question that invites high-value comments, not just "thoughts?".

▌ TWITTER / X
  • Goal: Viral insights and punchy opinions.
  • Format: A THREAD of 8–12 tweets, numbered (1/N).
  • STYLE: Punchy, bold, and slightly provocative. Use line breaks within tweets.
  • CTA: Ask for a Retweet (RT) or a Follow.

▌ INSTAGRAM (CAROUSEL)
  • Goal: Visual education and aesthetic value.
  • Format: JSON with "caption" and "slides".
  • SLIDES: 7-10 slides. Slide 1 is the hook. Slides 2-9 provide value. Slide 10 is the CTA.
  • VOICE: More casual, emoji-rich, and community-focused.

═══════════════════════════════════════════
 OUTPUT RULES
═══════════════════════════════════════════
• Return ONLY the content. No preamble.
• Make it feel HUMAN. It should feel like {name} just had a "Eureka!" moment and shared it.
"""

# ── Core generation call ──────────────────────────────────────────────────────

async def generate_with_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 4096,
    temperature: float = 0.85,
    use_search_agent: bool = False
) -> str:
    """
    Calls Gemini 2.0 Flash (Fastest) and returns generated text.
    Uses the asynchronous client for maximum performance.
    """
    client = get_client()
    
    config = types.GenerateContentConfig(
        max_output_tokens=max_tokens,
        temperature=temperature,
        response_mime_type="application/json",
        system_instruction=system_prompt,
    )
    
    if use_search_agent:
        config.tools = [{"google_search": {}}]

    try:
        # Use Gemini 2.0 Flash for best speed/quality balance
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=user_prompt,
            config=config,
        )
        text = response.text.strip() if response.text else ""
        logger.info(f"[llm] Gemini response received: {len(text)} chars")
        return text

    except Exception as e:
        error_msg = str(e)
        logger.error(f"[llm] Gemini generation failed: {error_msg}")
        raise RuntimeError(f"Gemini API Error: {error_msg}")

# ── Embeddings ────────────────────────────────────────────────────────────────

async def get_embedding(text: str) -> list[float]:
    """
    Returns a 1536-dim embedding vector.
    Uses text-embedding-004 (768-dim) and pads to 1536 to match Supabase column.
    Falls back to zero vector on failure.
    """
    try:
        client = get_client()
        result = await asyncio.to_thread(
            client.models.embed_content,
            model="gemini-embedding-2",
            contents=text,
        )
        vec = result.embeddings[0].values
        # Gemini embeddings use Matryoshka Representation Learning, meaning we can
        # safely truncate the 3072-dim vector to 768 dims without losing semantic meaning.
        return list(vec)[:768]
    except Exception as e:
        logger.warning(f"[llm] Embedding failed, returning zeros: {e}")
        return [0.0] * 768

# ── Image Generation ──────────────────────────────────────────────────────────

async def generate_carousel_images(slides: list) -> list:
    """
    Takes a list of carousel slides, generates an image for each using Imagen 3,
    saves to frontend/public/generated_images/, and adds image_url to the slide.
    """
    client = get_client()
    output_dir = os.path.join(os.path.dirname(__file__), "frontend", "public", "generated_images")
    os.makedirs(output_dir, exist_ok=True)

    for slide in slides:
        prompt = f"A high quality Instagram carousel background image. Theme: {slide.get('title', '')}. Details: {slide.get('body', '')}. Style: modern, minimal, aesthetic, dark mode gradients, professional."
        try:
            result = await asyncio.to_thread(
                client.models.generate_images,
                model='imagen-4.0-generate-001',
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1"
                )
            )
            for generated_image in result.generated_images:
                filename = f"slide_{uuid.uuid4().hex[:8]}.jpg"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "wb") as f:
                    f.write(generated_image.image.image_bytes)
                slide["image_url"] = f"/generated_images/{filename}"
                break
        except Exception as e:
            logger.error(f"[llm] Image generation failed for slide {slide.get('slide')}: {e}")
            slide["image_url"] = None

    return slides