from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
import subprocess
import sys

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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