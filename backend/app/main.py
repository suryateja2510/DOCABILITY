# app/main.py
from dotenv import load_dotenv
import os
import threading
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes.agent_routes import router as agent_router
from app.utils.helpers import cleanup_temp

load_dotenv()

app = FastAPI()
app.include_router(agent_router, prefix="/agents", tags=["Agents"])

# -----------------------------
# Serve TTS audio files
# -----------------------------
AUDIO_DIR = "temp_audio"
os.makedirs(AUDIO_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=AUDIO_DIR), name="audio")

# -----------------------------
# Start background cleanup
# -----------------------------
threading.Thread(target=cleanup_temp, daemon=True).start()
