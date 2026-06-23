from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from frontend.schemas import AtendimentoEntrada
from frontend.services import executar_atendimento_web

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

FRONTEND_DIR = Path(__file__).resolve().parent
STATIC_DIR = FRONTEND_DIR / "static"

app = FastAPI(title="Asclepio Frontend API")
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "http://localhost:8000",
        "http://localhost:8001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def cache_static_assets(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static/"):
        response.headers["Cache-Control"] = "public, max-age=3600"
    return response


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/status")
def status() -> dict[str, str]:
    return {"status": "ok", "app": "Asclepio"}


@app.get("/api/atendimentos")
def atendimentos(limite: int = 20) -> list[dict[str, Any]]:
    from database import listar_atendimentos

    return listar_atendimentos(limite=max(1, min(limite, 100)))


@app.post("/api/atendimento")
def atendimento(entrada: AtendimentoEntrada) -> dict[str, Any]:
    try:
        return executar_atendimento_web(entrada)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Nao foi possivel concluir o atendimento: {exc}",
        ) from exc
