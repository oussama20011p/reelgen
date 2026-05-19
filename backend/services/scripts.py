import anthropic
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

LANG_INSTRUCTIONS = {
    "darija": "Moroccan Darija (Arabic dialect written in Arabic script). Casual TikTok tone.",
    "french": "French. Casual TikTok tone, modern, direct.",
    "arabic": "Modern Standard Arabic (فصحى). Clear and engaging.",
    "english": "English. Casual TikTok tone, punchy, direct.",
}

def generate_scripts(product: dict, language: str) -> dict:
    lang_note = LANG_INSTRUCTIONS.get(language, LANG_INSTRUCTIONS["english"])
    prompt = f"""
You are a TikTok ad copywriter. Write 3 complete 30-second ad scripts for this product:

Product: {product['name']}
Niche: {product['niche']}
Description: {product['description']}
Language: {lang_note}

Rules:
- Use specific numbers ("37,000 customers" not "thousands")
- Never corporate tone
- Hook 3s / Body 20s / CTA 5s

Return JSON only:
{{
  "A": {{"hook": "...", "body": "...", "cta": "...", "angle": "CURIOSITY"}},
  "B": {{"hook": "...", "body": "...", "cta": "...", "angle": "SOCIAL PROOF"}},
  "C": {{"hook": "...", "body": "...", "cta": "...", "angle": "BEFORE/AFTER"}}
}}
No markdown. Pure JSON.
"""
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    import json
    text = response.content[0].text.strip()
    return json.loads(text)
