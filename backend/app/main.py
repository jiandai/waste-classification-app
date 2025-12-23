from __future__ import annotations
from pathlib import Path
import logging
import os
from dotenv import load_dotenv
ENV_PATH = Path(__file__).resolve().parents[0] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

import io
import uuid
from typing import Optional, List

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from PIL import Image

from .schemas import ClassifyResponse, ErrorBody, LabelScore
from .vision_provider import get_provider
from .rules import decide_bin_from_profile, decide_bin_from_labels, apply_clarification


MAX_BYTES = 8 * 1024 * 1024  # 8MB
ALLOWED_MIME = {"image/jpeg", "image/png"}  # Sprint 0: keep minimal


app = FastAPI(title="Waste CV Prototype API", version="0.1.0")
logger = logging.getLogger("waste_app")

# Local testing convenience (tighten later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080", "http://localhost:8000", "http://127.0.0.1:8000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def log_provider_config() -> None:
    provider = os.getenv("VISION_PROVIDER", "stub").strip().lower()
    logger.info("VISION_PROVIDER=%s", provider)
    if provider == "openai":
        logger.info("OPENAI_MODEL=%s", os.getenv("OPENAI_MODEL", "unset"))


def _error_body(message: str, status_code: int, error_type: str, details: Optional[dict] = None) -> dict:
    body = {
        "request_id": f"req_{uuid.uuid4().hex[:12]}",
        "error": {
            "message": message,
            "code": status_code,
            "type": error_type,
        },
    }
    if details:
        body["error"]["details"] = details
    return body


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    body = _error_body(str(exc.detail), exc.status_code, "http_error")
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    body = _error_body("Validation error", 422, "validation_error", {"errors": exc.errors()})
    return JSONResponse(status_code=422, content=body)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception")
    body = _error_body("Internal server error", 500, "internal_error")
    return JSONResponse(status_code=500, content=body)


@app.get("/health")
def health():
    return {"status": "ok"}


def _normalize_image(image_bytes: bytes, mime: str) -> bytes:
    """
    Decode and re-encode to JPEG to normalize and strip EXIF by default.
    Sprint 0 keeps this simple.
    """
    try:
        with Image.open(io.BytesIO(image_bytes)) as im:
            im = im.convert("RGB")
            out = io.BytesIO()
            im.save(out, format="JPEG", quality=90, optimize=True)
            return out.getvalue()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")


@app.post("/v1/classify", response_model=ClassifyResponse, responses={400: {"model": ErrorBody}, 413: {"model": ErrorBody}, 415: {"model": ErrorBody}})
async def classify(
    image: UploadFile = File(...),
    jurisdiction_id: str = Form("CA_DEFAULT"),
    client_request_id: Optional[str] = Form(None),
    locale: Optional[str] = Form(None),
):
    request_id = f"req_{uuid.uuid4().hex[:12]}"

    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail=f"Unsupported media type: {image.content_type}. Use JPG or PNG for Sprint 0.")

    raw = await image.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_BYTES // (1024*1024)} MB.")

    normalized = _normalize_image(raw, image.content_type)

    provider = get_provider()
    try:
        # Use new ItemProfile-based flow
        profile = await provider.detect_item_profile(normalized, mime_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Vision provider error: {e}")

    result, needs_clarification, clarification, special_handling = decide_bin_from_profile(
        profile=profile,
        jurisdiction_id=jurisdiction_id
    )

    return ClassifyResponse(
        request_id=request_id,
        jurisdiction_id=jurisdiction_id,
        result=result,
        needs_clarification=needs_clarification,
        clarification=clarification,
        special_handling=special_handling
    )


class ClarifyRequest(BaseModel):
    request_id: str
    question_id: str
    answer: bool
    # For Sprint 0, the frontend will send back the last top_labels it received (optional)
    top_labels: Optional[List[LabelScore]] = None


@app.post("/v1/clarify", response_model=ClassifyResponse, responses={400: {"model": ErrorBody}})
def clarify(payload: ClarifyRequest):
    request_id = payload.request_id or f"req_{uuid.uuid4().hex[:12]}"
    jurisdiction_id = "CA_DEFAULT"

    prior = payload.top_labels or []
    result = apply_clarification(payload.question_id, payload.answer, prior_top_labels=prior)

    return ClassifyResponse(
        request_id=request_id,
        jurisdiction_id=jurisdiction_id,
        result=result,
        needs_clarification=False,
        clarification=None,
        special_handling=None
    )
