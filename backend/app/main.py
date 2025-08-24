# app/main.py
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from app.routes.sample_routes import router as sample_router
from app.routes.agent_routes import router as agent_router


app = FastAPI()
app.include_router(sample_router, prefix="/sample", tags=["Sample"])
app.include_router(agent_router, prefix="/agents", tags=["Agents"])
