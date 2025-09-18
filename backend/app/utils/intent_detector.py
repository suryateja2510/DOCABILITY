# app/utils/intent_detector.py
from typing import List
from sentence_transformers import SentenceTransformer, util

# Lightweight CPU model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Semantic templates for tasks
TASKS = {
    "summarize": ["summarize the text", "make a short summary", "shorten", "condense"],
    "translate": ["translate to Telugu", "convert language", "translate text"],
    "tts": ["play as audio", "read aloud", "text to speech", "speak"],
}

SIM_THRESHOLD = 0.55  # similarity threshold


def detect_intent(prompt: str) -> List[str]:
    """
    Detect tasks from a natural prompt: summarize, translate, tts
    """
    intents = []
    prompt_embedding = model.encode(prompt, convert_to_tensor=True)

    for task, examples in TASKS.items():
        example_embeddings = model.encode(examples, convert_to_tensor=True)
        cosine_scores = util.cos_sim(prompt_embedding, example_embeddings)
        if cosine_scores.max().item() >= SIM_THRESHOLD:
            intents.append(task)

    if not intents:
        intents.append("summarize")  # default
    return intents
