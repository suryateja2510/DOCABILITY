import re
from transformers import pipeline
from app.utils.helpers import clean_text

# Initialize summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def run(text: str) -> dict:
    """Summarize text with dynamic max_length based on input size."""
    cleaned_text = clean_text(text)
    words = cleaned_text.split()
    input_length = len(words)

    # Adjust max_length for small inputs
    max_length = min(250, max(20, input_length // 2))
    min_length = min(20, max_length)

    try:
        summary_result = summarizer(
            cleaned_text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
        )
        summary_text = summary_result[0]["summary_text"]
        error = None
    except Exception as e:
        summary_text = None
        error = str(e)

    return {
        "task": "summarization",
        "input_length": input_length,
        "output": summary_text,
        "error": error,
    }
