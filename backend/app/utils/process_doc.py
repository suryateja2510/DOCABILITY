# app/utils/process_doc.py
import os
from app.agents.summarizer.agent import SummarizerAgent
from app.agents.translator.agent import TranslatorAgent
from app.agents.tts.agent import TTSAgent
from app.utils.helpers import extract_text
from app.utils.constants import AgentTasks

# Instantiate agents once
summarizer_agent = SummarizerAgent()
translator_agent = TranslatorAgent()
tts_agent = TTSAgent()


def process_document_from_path(file_path: str, task: str) -> dict:
    """
    Process a document from a local path with a given task:
    - summarize
    - translate
    - tts
    """
    if not os.path.exists(file_path):
        return {
            "task": task,
            "input_length": 0,
            "output": None,
            "error": "File not found",
        }

    # Extract text from file
    result = extract_text(file_path)
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
            "error": "File has no text",
        }

    try:
        # Call the appropriate agent
        task_lower = task.lower()
        if task_lower == AgentTasks.SUMMARIZE:
            output = summarizer_agent.run(text)
        elif task_lower == AgentTasks.TRANSLATE:
            output = translator_agent.run(text)
        elif task_lower == AgentTasks.TEXT_TO_SPEECH:
            output = tts_agent.run(text)
        else:
            return {
                "task": task,
                "input_length": input_length,
                "output": None,
                "error": f"Unsupported task '{task}'",
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
        "error": None if not isinstance(output, dict) else output.get("error"),
    }
