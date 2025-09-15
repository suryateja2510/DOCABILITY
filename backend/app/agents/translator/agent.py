# app/agents/translator/agent.py
from googletrans import Translator
from app.utils.helpers import clean_text

SUPPORTED_LANGS = ["te", "hi"]  # Telugu, Hindi

translator = Translator()


def run(text: str, target_lang: str = "te") -> dict:
    cleaned_text = clean_text(text)
    if not cleaned_text:
        return {
            "task": "translation",
            "input_length": 0,
            "translated_text": None,
            "error": "No text to translate.",
        }

    if target_lang not in SUPPORTED_LANGS:
        return {
            "task": "translation",
            "input_length": len(cleaned_text),
            "translated_text": None,
            "error": f"Unsupported language: {target_lang}",
        }

    try:
        translated = translator.translate(cleaned_text, dest=target_lang)
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
