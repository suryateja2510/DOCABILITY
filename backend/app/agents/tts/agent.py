# app/agents/tts/agent.py
import tempfile
import base64
from gtts import gTTS
from app.utils.helpers import clean_text

SUPPORTED_LANGS = ["en", "hi", "te"]


def run(text: str, tts_lang: str = "en") -> dict:
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return {
            "task": "tts",
            "input_length": 0,
            "audio_base64": None,
            "error": "No text to synthesize.",
        }

    if tts_lang not in SUPPORTED_LANGS:
        return {
            "task": "tts",
            "input_length": len(cleaned_text),
            "audio_base64": None,
            "error": f"Unsupported TTS language: {tts_lang}",
        }

    try:
        tts = gTTS(text=cleaned_text, lang=tts_lang)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tts.save(tmp.name)
            tmp.seek(0)
            audio_base64 = base64.b64encode(tmp.read()).decode("utf-8")
        return {
            "task": "tts",
            "input_length": len(cleaned_text),
            "audio_base64": audio_base64,
            "error": None,
        }
    except Exception as e:
        return {
            "task": "tts",
            "input_length": len(cleaned_text),
            "audio_base64": None,
            "error": str(e),
        }
