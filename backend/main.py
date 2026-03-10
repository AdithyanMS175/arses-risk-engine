from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import init_db
from routes import router


app = FastAPI(
    title="AI Risk Scoring Engine Stub (ARSES)",
    version="1.0.0",
    description="A small AI-style risk scoring API that returns risk score and confidence metadata.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()

