# app/routes/agent_routes.py

import os
from fastapi import APIRouter, UploadFile, File, Form
from app.utils.intent_detector import detect_intent
from app.utils.process_doc import process_document_from_path
from app.agents.summarizer.agent import SummarizerAgent
from app.agents.translator.agent import TranslatorAgent
from app.agents.tts.agent import TTSAgent

router = APIRouter()

# Directory to store uploaded docs
UPLOAD_DIR = "uploaded_docs"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Instantiate agents
summarizer_agent = SummarizerAgent()
translator_agent = TranslatorAgent()
tts_agent = TTSAgent()


@router.post("/admin/upload-doc/")
async def admin_upload_doc(file: UploadFile = File(...)):
    """Admin uploads document to server."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"filename": file.filename, "status": "uploaded"}


@router.get("/user/list-docs/")
async def user_list_docs():
    """List all uploaded documents for user to select."""
    files = os.listdir(UPLOAD_DIR)
    return {"documents": files}


@router.post("/process-prompt/")
async def process_prompt(
    file_name: str = Form(...),
    prompt: str = Form(...),
):
    """
    User selects a file (by name) and provides a prompt.
    Detects intents and processes each intent using local agents.
    """
    file_path = os.path.join(UPLOAD_DIR, file_name)

    if not os.path.exists(file_path):
        return {"error": f"File '{file_name}' not found."}

    # Detect intents and constraints from prompt
    intents, constraints = detect_intent(prompt, return_constraints=True)
    results = {}
    # Extract text from file
    from app.utils.helpers import extract_text

    extract_result = extract_text(file_path)
    if extract_result["error"]:
        return {"error": extract_result["error"]}
    content = extract_result["text"].strip()
    processed_content = content
    # Chain processing: summarize -> translate -> tts
    # Always process in the order: summarize, translate, tts/play
    # Use constraints for each step if present
    if "summarize" in intents:
        lines = constraints.get("lines")
        chars = constraints.get("chars")
        words = constraints.get("words")
        summary = summarizer_agent.summarize(
            processed_content, lines=lines, chars=chars, words=words
        )
        results["summary"] = summary
        processed_content = summary
    if "translate" in intents:
        target_lang = constraints.get("target_lang")
        if target_lang:
            translation = translator_agent.translate(
                processed_content, target_lang=target_lang
            )
        else:
            translation = translator_agent.translate(processed_content)
        results["translate"] = translation
        processed_content = translation
    if "tts" in intents or "play" in intents:
        audio_path = tts_agent.text_to_speech(processed_content)
        results["tts"] = audio_path
    return {"intents": intents, "results": results}
