# src/main.py

from fastapi import FastAPI
from src.api.routes import tools

app = FastAPI()

app.include_router(tools.router, prefix="/api")
