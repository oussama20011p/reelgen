import wave
import os
import time
from google import genai
from google.genai import types


def generate_voiceover(text: str, output_path: str, language: str = "darija") -> str:
    api_key = os.getenv("GOOGLE_AI_API_KEY", "")
    client = genai.Client(api_key=api_key)

    for attempt in range(3):
        try:
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

        except Exception as e:
            err = str(e)
            if "429" in err or "RESOURCE_EXHAUSTED" in err:
                wait = 30 * (attempt + 1)
                time.sleep(wait)
                continue
            raise

    # Fallback: gTTS
    return _gtts_fallback(text, output_path, language)


def _gtts_fallback(text: str, output_path: str, language: str = "darija") -> str:
    from gtts import gTTS
    import subprocess

    lang_map = {"darija": "ar", "arabic": "ar", "french": "fr", "english": "en"}
    lang = lang_map.get(language, "ar")

    mp3_path = output_path.replace(".wav", "_tmp.mp3")
    gTTS(text=text, lang=lang, slow=False).save(mp3_path)

    # Convert mp3 to wav
    subprocess.run(
        ["ffmpeg", "-y", "-i", mp3_path, output_path],
        capture_output=True
    )
    os.remove(mp3_path)
    return output_path
