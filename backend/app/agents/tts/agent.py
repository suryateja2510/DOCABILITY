# app/agents/tts/agent.py
from app.agents.agent_interface import AgentBase
import tempfile
import base64
from gtts import gTTS
from app.utils.helpers import clean_text, AUDIO_DIR
import os

# Ensure AUDIO_DIR exists
os.makedirs(AUDIO_DIR, exist_ok=True)


class TTSAgent(AgentBase):
    SUPPORTED_LANGS = ["en", "hi", "te"]

    def run(self, text: str, tts_lang: str = "en", **kwargs) -> dict:
        cleaned_text = clean_text(text)
        if not cleaned_text:
            return {
                "task": "tts",
                "input_length": 0,
                "audio_base64": None,
                "file_path": None,
                "error": "No text to synthesize.",
            }

        if tts_lang not in self.SUPPORTED_LANGS:
            return {
                "task": "tts",
                "input_length": len(cleaned_text),
                "audio_base64": None,
                "file_path": None,
                "error": f"Unsupported TTS language: {tts_lang}",
            }

        try:
            tts = gTTS(text=cleaned_text, lang=tts_lang)
            with tempfile.NamedTemporaryFile(
                dir=AUDIO_DIR, suffix=".mp3", delete=False
            ) as tmp:
                tts.save(tmp.name)
                tmp.seek(0)
                audio_base64 = base64.b64encode(tmp.read()).decode("utf-8")
                file_path = tmp.name

            return {
                "task": "tts",
                "input_length": len(cleaned_text),
                "audio_base64": audio_base64,
                "file_path": file_path,
                "error": None,
            }

        except Exception as e:
            return {
                "task": "tts",
                "input_length": len(cleaned_text),
                "audio_base64": None,
                "file_path": None,
                "error": str(e),
            }
