"""FastAPI device and demo adapter.

Provides authenticated device endpoints for real JPEG observations and telemetry,
while preserving backwards-compatible demo endpoints.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .domain import normalize_plate, PLATE, validate_observation
from .ocr import BasePlateOCR, get_ocr_engine
from .store import Conflict, Store

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = str(ROOT / "data" / "demo.sqlite3")
MAX_JPEG_BYTES = 512_000  # 500 KB limit for embedded camera capture
DEVICE_AUTH_TOKEN = os.environ.get("DEVICE_AUTH_TOKEN", "smart-barrier-device-key-2026")


class ObservationMetadata(BaseModel):
    device_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    session_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    request_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    deadline_ms: int | None = Field(default=None, ge=100, le=60000)
    roi: list[int] | None = Field(default=None)


class DeviceEventRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    session_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    event_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    event_type: str = Field(min_length=1, max_length=64)
    barrier_state: str | None = None
    details: dict[str, Any] | None = None


def create_app(db_path: str = DEFAULT_DB, ocr_engine: BasePlateOCR | None = None) -> FastAPI:
    store = Store(db_path)
    if ocr_engine is None:
        ocr_engine = get_ocr_engine("fast-plate-ocr")

    app = FastAPI(
        title="Smart Plate Barrier Backend",
        version="0.2.0",
        description="Unified backend providing demo endpoints and authenticated device adapter.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:3000", "http://localhost:3000", "http://127.0.0.1:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def verify_device_auth(
        authorization: Annotated[str | None, Header()] = None,
        x_device_token: Annotated[str | None, Header()] = None,
    ):
        token = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization[7:].strip()
        elif x_device_token:
            token = x_device_token.strip()

        expected = os.environ.get("DEVICE_AUTH_TOKEN", DEVICE_AUTH_TOKEN)
        if not token or token != expected:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid or missing device credentials",
            )
        return token

    # ---------------- Demo Endpoints (Preserved for compatibility) ----------------

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "0.2.0", "mode": "device_and_simulation"}

    @app.get("/api/state")
    def get_state():
        return store.snapshot()

    @app.post("/api/demo/scan")
    async def demo_scan(request: Request):
        try:
            body = await request.json()
            return store.scan(body)
        except Conflict as exc:
            raise HTTPException(status_code=409, detail=str(exc))
        except (ValueError, TypeError) as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/demo/clear")
    def demo_clear():
        return store.clear()

    @app.post("/api/plates/add")
    async def add_plate(request: Request):
        try:
            body = await request.json()
            return store.change_plate(body.get("plate"), add=True)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.post("/api/plates/remove")
    async def remove_plate(request: Request):
        try:
            body = await request.json()
            return store.change_plate(body.get("plate"), add=False)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # ---------------- Authenticated Device Adapter Endpoints ----------------

    @app.post("/api/device/v1/observations")
    async def device_observation(
        request: Request,
        _auth: str = Depends(verify_device_auth),
        x_device_id: Annotated[str | None, Header()] = None,
        x_session_id: Annotated[str | None, Header()] = None,
        x_request_id: Annotated[str | None, Header()] = None,
        x_deadline_ms: Annotated[int | None, Header()] = None,
    ):
        content_type = request.headers.get("content-type", "").split(";")[0].strip().lower()

        roi = None
        if content_type == "image/jpeg":
            # Raw JPEG stream with metadata in HTTP headers
            if not x_device_id or not x_session_id or not x_request_id:
                raise HTTPException(
                    status_code=400,
                    detail="missing required headers: X-Device-Id, X-Session-Id, X-Request-Id",
                )
            device_id, session_id, request_id = x_device_id, x_session_id, x_request_id
            image_bytes = await request.body()
        elif content_type == "multipart/form-data":
            # Multipart form upload
            form = await request.form()
            try:
                metadata_field = form.get("metadata")
                image_field = form.get("image")

                if not metadata_field or not image_field:
                    raise HTTPException(
                        status_code=400,
                        detail="multipart form must contain 'metadata' (JSON) and 'image' (file)",
                    )

                try:
                    meta_dict = json.loads(metadata_field) if isinstance(metadata_field, str) else {}
                    meta = ObservationMetadata(**meta_dict)
                    device_id, session_id, request_id = meta.device_id, meta.session_id, meta.request_id
                    roi = meta.roi
                except Exception as exc:
                    raise HTTPException(status_code=400, detail=f"invalid metadata: {exc}")

                image_bytes = await image_field.read()
            finally:
                for v in form.values():
                    if hasattr(v, "close"):
                        await v.close()
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail="expected image/jpeg or multipart/form-data",
            )

        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="empty image payload")
        if len(image_bytes) > MAX_JPEG_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"image exceeds maximum allowed size ({MAX_JPEG_BYTES} bytes)",
            )

        image_sha256 = hashlib.sha256(image_bytes).hexdigest()

        # Run OCR
        ocr_res = ocr_engine.recognize(image_bytes, roi=roi)

        try:
            record = store.record_device_observation(
                device_id=device_id,
                session_id=session_id,
                request_id=request_id,
                image_sha256=image_sha256,
                ocr_result=ocr_res,
            )
            # Add OCR telemetry details
            record["ocr"] = {
                "engine": ocr_res.engine,
                "model": ocr_res.model_name,
                "latency_ms": ocr_res.latency_ms,
                "raw_text": ocr_res.raw_text,
                "country_hint": ocr_res.country_hint,
            }
            return record
        except Conflict as exc:
            raise HTTPException(status_code=409, detail=str(exc))

    @app.post("/api/device/v1/events")
    async def device_event(
        req: DeviceEventRequest,
        _auth: str = Depends(verify_device_auth),
    ):
        result = store.record_device_event(
            device_id=req.device_id,
            session_id=req.session_id,
            event_id=req.event_id,
            event_type=req.event_type,
            details={"barrier_state": req.barrier_state, **(req.details or {})},
        )
        return {"status": "ok", **result}

    return app


app = create_app()
