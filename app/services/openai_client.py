# app/services/openai_client.py

import json
import re
import time
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def style_guidelines(style: str) -> str:
    """
    Returns tone/voice instructions for different styles.
    """
    style = (style or "formal").lower()

    if style == "formal":
        return "Use a professional, structured, and objective tone suitable for corporate or academic audiences."
    elif style == "casual":
        return "Use a friendly, conversational tone with simple words and relatable examples."
    elif style == "seo":
        return (
            "Optimize for SEO with keyword-rich headings, meta description hints, "
            "and short, scannable paragraphs. Avoid fluff and focus on ranking content."
        )
    elif style == "storytelling":
        return "Use a storytelling tone with engaging hooks, relatable characters, and a clear narrative flow."
    else:
        return "Use a balanced and clear tone."


def build_prompt(keyword: str, style: str = "formal") -> str:
    """
    Build a detailed prompt for article generation based on style.
    """
    tone_instruction = style_guidelines(style)

    return f"""
You are an expert SEO blog writer and WordPress content specialist.

Write a complete article for the topic: "{keyword}".

Writing Style: {style.title()}  
Tone Instructions: {tone_instruction}  
Structure: At least 1300 words, with <h2> and <h3> headings, bullet lists, a conclusion, and 5–7 FAQs.

The article must be formatted in clean HTML ready for WordPress.

Return STRICT JSON only in this format:
{{
  "title": "An SEO-friendly article title containing {keyword}",
  "content": "<HTML formatted article body>"
}}
""".strip()


def generate_article(keyword: str, style: str = "formal", retries: int = 2) -> dict | None:
    """
    Generate an SEO blog article using OpenAI.
    Returns dict { "title": ..., "content": ... } or None on failure.
    """
    prompt = build_prompt(keyword, style)

    for attempt in range(retries):
        try:
            resp = client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=4000,
            )

            text = resp.choices[0].message.content
            cleaned = re.sub(r"[\x00-\x1F\x7F]", "", text).strip()
            first, last = cleaned.find("{"), cleaned.rfind("}")
            payload = cleaned[first:last + 1] if first != -1 and last > first else cleaned

            return json.loads(payload)

        except Exception as e:
            print(f"[OpenAI Article Error] attempt {attempt + 1}: {e}")
            time.sleep(2)

    return None


def generate_image_b64(prompt: str, retries: int = 2) -> str | None:
    """
    Generate a base64-encoded image for WordPress featured image.
    """
    for attempt in range(retries):
        try:
            resp = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                size="1024x1024",
            )
            return resp.data[0].b64_json
        except Exception as e:
            print(f"[OpenAI Image Error] attempt {attempt + 1}: {e}")
            time.sleep(2)
    return None
