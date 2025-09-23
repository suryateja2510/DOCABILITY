# app/utils/intent_detector.py
from typing import List
from sentence_transformers import SentenceTransformer, util

# Lightweight CPU model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Expanded semantic templates for tasks
TASKS = {
    "summarize": [
        "summarize",
        "summary",
        "short summary",
        "make a short summary",
        "shorten",
        "condense",
        "give me a summary",
        "brief",
        "in short",
        "in brief",
        "summarize in",
        "summarize to",
        "summarize this",
        "summarize the text",
    ],
    "translate": [
        "translate",
        "convert language",
        "translate text",
        "translate to hindi",
        "translate to telugu",
        "translate to english",
        "translate into hindi",
        "translate into telugu",
        "translate into english",
        "hindi translation",
        "telugu translation",
        "english translation",
    ],
    "tts": [
        "play as audio",
        "read aloud",
        "text to speech",
        "speak",
        "generate audio",
        "play it",
        "audio output",
        "audio version",
        "listen",
        "play",
        "tts",
        "voice output",
        "speak aloud",
    ],
}

SIM_THRESHOLD = 0.55  # similarity threshold


def detect_intent(user_prompt: str, return_constraints=False) -> List[str]:
    """
    Detect tasks from a natural prompt: summarize, translate, tts
    """
    intents = []
    prompt_embedding = model.encode(user_prompt, convert_to_tensor=True)

    for task, examples in TASKS.items():
        example_embeddings = model.encode(examples, convert_to_tensor=True)
        cosine_scores = util.cos_sim(prompt_embedding, example_embeddings)
        if cosine_scores.max().item() >= SIM_THRESHOLD:
            intents.append(task)

    # Fallback: keyword-based detection for each intent
    prompt_lower = user_prompt.lower()
    if any(
        word in prompt_lower
        for word in ["summarize", "summary", "short summary", "brief"]
    ):
        if "summarize" not in intents:
            intents.append("summarize")
    if any(
        word in prompt_lower
        for word in ["translate", "translation", "hindi", "telugu", "english"]
    ):
        if "translate" not in intents:
            intents.append("translate")
    if any(
        word in prompt_lower for word in ["play", "tts", "audio", "read aloud", "speak"]
    ):
        if "tts" not in intents:
            intents.append("tts")
    if not intents:
        intents.append("summarize")  # default
    constraints = {}
    import re

    prompt_lower = user_prompt.lower()
    # Robust line constraint extraction
    line_patterns = [
        r"summary in (\d+) lines",
        r"summarize.*in (\d+) lines",
        r"summarize.*limit.*to (\d+) lines",
        r"in (\d+) lines",
        r"limit.*to (\d+) lines",
        r"(\d+) lines summary",
        r"(\d+)-line summary",
        r"short summary in (\d+) lines",
        r"brief summary in (\d+) lines",
    ]
    for pat in line_patterns:
        m = re.search(pat, prompt_lower)
        if m:
            constraints["lines"] = int(m.group(1))
            break
    # Robust character constraint extraction
    char_patterns = [
        r"summary in (\d+) characters",
        r"summarize.*in (\d+) characters",
        r"summarize.*limit.*to (\d+) characters",
        r"in (\d+) characters",
        r"limit.*to (\d+) characters",
        r"(\d+) character summary",
        r"(\d+)-character summary",
        r"short summary in (\d+) characters",
        r"brief summary in (\d+) characters",
    ]
    for pat in char_patterns:
        m = re.search(pat, prompt_lower)
        if m:
            constraints["chars"] = int(m.group(1))
            break
    # Robust word constraint extraction
    word_patterns = [
        r"summary in (\d+) words",
        r"summarize.*in (\d+) words",
        r"summarize.*limit.*to (\d+) words",
        r"in (\d+) words",
        r"limit.*to (\d+) words",
        r"(\d+) words summary",
        r"(\d+)-word summary",
        r"short summary in (\d+) words",
        r"brief summary in (\d+) words",
    ]
    for pat in word_patterns:
        m = re.search(pat, prompt_lower)
        if m:
            constraints["words"] = int(m.group(1))
            break
    # Detect requested translation language (also from 'summarize to <lang>')
    lang_patterns = [
        r"translate to ([a-zA-Z]+)",
        r"translate into ([a-zA-Z]+)",
        r"([a-zA-Z]+) translation",
        r"summarize to ([a-zA-Z]+)",
        r"summary to ([a-zA-Z]+)",
        r"summarize in ([a-zA-Z]+)",
        r"summary in ([a-zA-Z]+)",
    ]
    for pat in lang_patterns:
        m = re.search(pat, prompt_lower)
        if m:
            lang = m.group(1).strip().lower()
            if lang in ["hindi", "telugu", "english"]:
                constraints["target_lang"] = lang
            break
    if return_constraints:
        return intents, constraints
    return intents
