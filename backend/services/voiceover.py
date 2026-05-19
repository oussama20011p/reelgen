import wave
import os
from google import genai
from google.genai import types

def generate_voiceover(text: str, output_path: str) -> str:
    api_key = os.getenv("GOOGLE_AI_API_KEY", "")
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Charon")
                )
            )
        )
    )
    audio_data = response.candidates[0].content.parts[0].inline_data.data
    with wave.open(output_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)
    return output_path
