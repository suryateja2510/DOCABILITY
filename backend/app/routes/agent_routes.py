from fastapi import APIRouter, File, UploadFile, Form
from app.utils.process_doc import process_document

router = APIRouter()


@router.post("/process-doc")
async def process_doc_endpoint(
    file: UploadFile = File(...),
    task: str = Form(...),
    target_lang: str = Form("te"),
):
    """
    Single endpoint to process a document based on task:
        - summarize
        - translate
        - tts
    Only file upload is required.
    """
    return await process_document(file=file, task=task, target_lang=target_lang)
