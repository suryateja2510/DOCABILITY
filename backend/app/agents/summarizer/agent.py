# app/agents/summarizer/agent.py
from transformers import pipeline
from app.utils.helpers import clean_text, chunk_text
from app.agents.agent_interface import AgentBase


class SummarizerAgent(AgentBase):
    def __init__(self):
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    def run(self, text: str, **kwargs) -> dict:
        """Summarize text in chunks to avoid model limits."""
        cleaned_text = clean_text(text)
        if not cleaned_text:
            return {
                "task": "summarization",
                "input_length": 0,
                "output": "",
                "error": "No text to summarize.",
            }

        chunks = chunk_text(cleaned_text, max_chars=500)
        summaries = []
        errors = []

        for chunk in chunks:
            try:
                max_length = min(250, max(20, len(chunk.split()) // 2))
                min_length = min(20, max_length)
                summary_result = self.summarizer(
                    chunk, max_length=max_length, min_length=min_length, do_sample=False
                )
                summaries.append(summary_result[0]["summary_text"])
            except Exception as e:
                errors.append(str(e))

        final_summary = " ".join(summaries)
        return {
            "task": "summarization",
            "input_length": len(cleaned_text.split()),
            "output": final_summary,
            "error": "; ".join(errors) if errors else None,
        }
