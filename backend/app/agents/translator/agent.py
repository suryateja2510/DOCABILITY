# app/agents/translator/agent.py

from app.agents.agent_interface import AgentBase
from googletrans import Translator
from app.utils.helpers import clean_text


class TranslatorAgent(AgentBase):
    SUPPORTED_LANGS = ["te", "hi"]  # Telugu, Hindi

    def __init__(self):

        self.translator = Translator()

    def run(self, text: str, target_lang: str = "te", **kwargs) -> dict:

        cleaned_text = clean_text(text)
        if not cleaned_text:
            return {
                "task": "translation",
                "input_length": 0,
                "translated_text": None,
                "error": "No text to translate.",
            }

        if target_lang not in self.SUPPORTED_LANGS:
            return {
                "task": "translation",
                "input_length": len(cleaned_text),
                "translated_text": None,
                "error": f"Unsupported language: {target_lang}",
            }

        try:
            translated = self.translator.translate(cleaned_text, dest=target_lang)
            return {
                "task": "translation",
                "input_length": len(cleaned_text),
                "translated_text": translated.text,
                "error": None,
            }
        except Exception as e:
            return {
                "task": "translation",
                "input_length": len(cleaned_text),
                "translated_text": None,
                "error": str(e),
            }

    def translate(self, content, target_lang=None):
        # Use googletrans for actual translation if possible
        cleaned_text = clean_text(content)
        if not cleaned_text:
            return ""
        # If no target_lang, default to Telugu
        lang_map = {"telugu": "te", "hindi": "hi", "english": "en"}
        lang = lang_map.get(target_lang, "te") if target_lang else "te"
        try:
            translated = self.translator.translate(cleaned_text, dest=lang)
            return translated.text
        except Exception:
            # Fallback: reverse string as dummy
            return cleaned_text[::-1]
