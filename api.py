from fastapi import FastAPI
from src.api.routes import router
import subprocess
import sys

app = FastAPI()

app.include_router(router)

def run():
    subprocess.run(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "api:app",
            "--reload"
        ],
        check=True
    )