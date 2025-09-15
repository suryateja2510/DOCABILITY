from typing import Optional
from app.utils.helpers import save_and_extract
from app.agents.summarizer.agent import run as summarize_agent
from app.agents.translator.agent import run as translate_agent
from app.agents.tts.agent import run as tts_agent
from fastapi import UploadFile
from app.utils.constants import AgentTasks


async def process_document(
    file: UploadFile, task: AgentTasks, target_lang: str = "te"
) -> dict:
    """
    Unified document processing:
        - summarize
        - translate
        - tts
    Only file upload is required.
    """
    # Extract text
    result = save_and_extract(file)
    if result["error"]:
        return {
            "task": task,
            "input_length": 0,
            "output": None,
            "error": result["error"],
        }

    text = result["text"].strip()
    input_length = len(text)

    if not text:
        return {
            "task": task,
            "input_length": 0,
            "output": None,
            "error": "Uploaded file contains no text.",
        }

    try:
        if task.lower() == AgentTasks.SUMMARIZE:
            output = summarize_agent(text)
        elif task.lower() == AgentTasks.TRANSLATE:
            output = translate_agent(text, target_lang)
        elif task.lower() == AgentTasks.TEXT_TO_SPEECH:
            output = tts_agent(text)
        else:
            return {
                "task": task,
                "input_length": input_length,
                "output": None,
                "error": f"Unsupported task '{task}'. Supported: summarize, translate, tts",
            }
    except Exception as e:
        return {
            "task": task,
            "input_length": input_length,
            "output": None,
            "error": str(e),
        }

    return {
        "task": task,
        "input_length": input_length,
        "output": output,
        "error": (
            None
            if not isinstance(output, dict) or "error" not in output
            else output.get("error")
        ),
    }
