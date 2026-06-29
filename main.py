import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional
from pydantic import BaseModel

load_dotenv()

from model import init_db, get_assets, get_measurements, get_summary, get_status_counts
from agent import run_agent

app = FastAPI(title="Asset Monitoring Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/assets")
def assets_endpoint():
    return get_assets()


@app.get("/api/measurements/{asset}/{mtype}")
def measurements_endpoint(asset: str, mtype: str):
    return get_measurements(asset, mtype)


@app.get("/api/summary/{asset}")
def summary_endpoint(asset: str):
    return get_summary(asset)


@app.get("/api/status")
def status_endpoint():
    return get_status_counts()


class ChatRequest(BaseModel):
    message: str
    history: list = []
    asset_context: Optional[str] = None


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    api_key = os.getenv("ANTHROPIC_API_KEY")

    message = req.message
    if req.asset_context:
        message = f"[Context: User is viewing {req.asset_context}]\n{req.message}"

    text = await asyncio.to_thread(run_agent, message, req.history, api_key)

    async def stream():
        for char in text:
            yield char

    return StreamingResponse(stream(), media_type="text/plain")
