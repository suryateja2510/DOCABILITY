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
