import asyncio
import os
import edge_tts

VOICE_MAP = {
    "darija": "ar-MA-JamalNeural",
    "arabic": "ar-SA-HamedNeural",
    "french": "fr-FR-HenriNeural",
    "english": "en-US-GuyNeural",
}


def generate_voiceover(text: str, output_path: str, language: str = "darija") -> str:
    voice = VOICE_MAP.get(language, "ar-MA-JamalNeural")

    async def _run():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

    asyncio.run(_run())
    return output_path
