"""Command Center reference app (facilitator copy).

FastAPI entry that:
- Serves the Homebase prototype as static files (default doc: Homebase.html)
- Mounts `/api/wiring` so the UI can show a live connectivity banner
- (Stub) Genie / labor / inventory / feedback routers will be added next pass

Inspired by the lakehouse-market-e2e build's structure but scoped to the
ucode workshop's 8-table schema and 3-pillar UI.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from routers import feedback, genie, inventory, labor, today, wiring, writes

STATIC_DIR = Path(__file__).parent / "static"
DEFAULT_DOC = os.environ.get("DEFAULT_DOC", "Homebase.html")

app = FastAPI(title="Command Center (reference)")

app.include_router(wiring.router)
app.include_router(today.router)
app.include_router(labor.router)
app.include_router(inventory.router)
app.include_router(feedback.router)
app.include_router(genie.router)
app.include_router(writes.router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "command-center"}


@app.get("/")
def root():
    return RedirectResponse(url=f"/{DEFAULT_DOC}")


# Mount the prototype directory as static last so it doesn't shadow /api/*.
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
