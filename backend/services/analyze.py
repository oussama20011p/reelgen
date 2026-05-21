import anthropic
import base64
import os

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def analyze_product_image(image_bytes: bytes, mime_type: str) -> dict:
    b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": mime_type, "data": b64}
                },
                {
                    "type": "text",
                    "text": (
                        "Analyze this product image. Return JSON only with these fields:\n"
                        "- name: exact product name\n"
                        "- niche: product category\n"
                        "- keywords: list of 5 specific search keywords\n"
                        "- description: 1 sentence visual description\n"
                        "- tiktok_search: TikTok search query to find videos of this EXACT product. Include color, size, key features (e.g. 'blue portable USB mini blender', 'pink led face mask', 'black wireless earbuds'). Be specific enough to find this exact product but not overly long.\n"
                        "No markdown, pure JSON."
                    )
                }
            ]
        }]
    )
    import json
    text = response.content[0].text.strip()
    return json.loads(text)
