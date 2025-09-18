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
os.makedirs(UPLOAD_DIR, exist_ok=True)

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

    # Detect intents from prompt (can return multiple tasks)
    intents = detect_intent(prompt)
    results = {}

    # Process each intent
    for intent in intents:
        # Call unified process_document_from_path
        results[intent] = process_document_from_path(file_path=file_path, task=intent)

    return {"intents": intents, "results": results}
