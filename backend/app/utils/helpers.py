from typing import List
import re
import os
import time
import tempfile
from fastapi import UploadFile
import os
from PyPDF2 import PdfReader
from docx import Document


def chunk_text(text: str, max_chars: int = 1000) -> List[str]:
    """
    Split long text into chunks of ~max_chars.
    Tries to split on sentences (periods) if possible.
    """
    import re

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # If single sentence is longer than max_chars, split hard
            while len(sentence) > max_chars:
                chunks.append(sentence[:max_chars])
                sentence = sentence[max_chars:]
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def clean_text(text: str) -> str:
    """
    Remove HTML/JSX tags and excessive line breaks.
    """
    text = re.sub(r"<[^>]+>", "", text)  # Remove tags like <Frame>, <Card>
    text = re.sub(r"\n{2,}", "\n", text)  # Replace multiple line breaks with single
    return text.strip()


AUDIO_DIR = "temp_audio"


def cleanup_temp(ttl: int = 3600):
    """
    Delete files older than TTL seconds from AUDIO_DIR
    """
    while True:
        now = time.time()
        for f in os.listdir(AUDIO_DIR):
            path = os.path.join(AUDIO_DIR, f)
            if os.path.isfile(path) and now - os.path.getmtime(path) > ttl:
                try:
                    os.remove(path)
                except Exception:
                    pass
        time.sleep(600)  # run every 10 minutes


def extract_text(file_path: str) -> dict:
    """
    Extract text from TXT, PDF, or DOCX.
    Returns a dict with keys:
        - text: str
        - error: str | None
    """
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return {"text": f.read(), "error": None}

        elif ext == ".pdf":
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                text.append(page.extract_text() or "")
            return {"text": "\n".join(text), "error": None}

        elif ext == ".docx":
            doc = Document(file_path)
            return {"text": "\n".join([p.text for p in doc.paragraphs]), "error": None}

        else:
            return {"text": "", "error": f"Unsupported file type: {ext}"}

    except Exception as e:
        return {"text": "", "error": str(e)}


def save_and_extract(file: UploadFile) -> dict:
    """
    Save uploaded file temporarily and extract text.
    Returns dict with 'text' and 'error'.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        result = extract_text(tmp_path)  # dict
        if result["error"]:
            return {"text": "", "error": result["error"]}

        text = result["text"]
        if not text.strip():
            return {"text": "", "error": "Uploaded file contains no text."}

        return {"text": text, "error": None}

    except Exception as e:
        return {"text": "", "error": f"Failed to extract text: {str(e)}"}
