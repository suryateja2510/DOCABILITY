# startup.py

import os
import time
import threading
import webbrowser
import uvicorn
from dotenv import load_dotenv
from app.utils.env_vars import ENVIRONMENT
from app.utils.constants import DEV_ENV

# Load environment variables from .env
load_dotenv()


def open_docs():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000/docs")


if __name__ == "__main__":
    env = os.getenv(ENVIRONMENT)

    if env == DEV_ENV:
        print("🚀 Starting FastAPI in *dev* mode...")
        threading.Thread(target=open_docs).start()
        uvicorn.run(
            "app.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            reload_excludes=[os.path.abspath(".venv")],
        )
