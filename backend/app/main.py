from __future__ import annotations
from pathlib import Path
import logging
import os

import io
import uuid
from typing import Optional, List

from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from PIL import Image

from .schemas import ClassifyResponse, ErrorBody, LabelScore
from .vision_provider import get_provider
from .rules import decide_bin_from_profile, apply_clarification


MAX_BYTES = 8 * 1024 * 1024  # 8MB
ALLOWED_MIME = {"image/jpeg", "image/png"}  # Stage 1 Phase 1: JPG/PNG support


app = FastAPI(title="Waste Classification API", version="1.0.0")
logger = logging.getLogger("waste_app")

# Configure CORS to allow mobile app requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for mobile app access
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Mount static files from web directory
# Directory structure: backend/app/main.py -> parents[2] -> project root -> web/
WEB_DIR = Path(__file__).resolve().parents[2] / "web"
if WEB_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and store request_id in request.state for tracing."""
    async def dispatch(self, request: Request, call_next):
        request.state.request_id = f"req_{uuid.uuid4().hex[:12]}"
        response = await call_next(request)
        return response


# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

@app.on_event("startup")
def log_provider_config() -> None:
    provider = os.getenv("VISION_PROVIDER", "stub").strip().lower()
    logger.info("VISION_PROVIDER=%s", provider)
    if provider == "openai":
        logger.info("OPENAI_MODEL=%s", os.getenv("OPENAI_MODEL", "unset"))


def _error_body(message: str, status_code: int, error_type: str, request_id: Optional[str] = None, details: Optional[dict] = None) -> dict:
    """
    Generate error response body with request_id from request state if available.
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_type: Type of error (e.g., "http_error", "validation_error")
        request_id: Request ID to use (from request.state). Falls back to generating a new one if None.
        details: Optional error details dictionary
    """
    body = {
        "request_id": request_id or f"req_{uuid.uuid4().hex[:12]}",
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
    request_id = getattr(request.state, "request_id", None)
    body = _error_body(str(exc.detail), exc.status_code, "http_error", request_id=request_id)
    return JSONResponse(status_code=exc.status_code, content=body)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", None)
    body = _error_body("Validation error", 422, "validation_error", request_id=request_id, details={"errors": jsonable_encoder(exc.errors())})
    return JSONResponse(status_code=422, content=body)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", None)
    logger.exception("Unhandled exception", extra={"request_id": request_id})
    body = _error_body("Internal server error", 500, "internal_error", request_id=request_id)
    return JSONResponse(status_code=500, content=body)


@app.get("/")
async def root():
    """Serve the index.html from the web directory."""
    index_path = WEB_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend index.html file not found. Ensure the web directory exists at the project root.")


@app.get("/manifest.json")
async def manifest():
    """Serve the PWA manifest file."""
    manifest_path = WEB_DIR / "manifest.json"
    if manifest_path.exists():
        return FileResponse(manifest_path, media_type="application/json")
    raise HTTPException(status_code=404, detail="manifest.json not found")


@app.get("/sw.js")
async def service_worker():
    """Serve the service worker file."""
    sw_path = WEB_DIR / "sw.js"
    if sw_path.exists():
        return FileResponse(sw_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="sw.js not found")


@app.get("/icon-{size}.png")
async def icon(size: str):
    """Serve PWA icons."""
    # Validate size parameter to prevent path traversal
    if size not in ["192", "512"]:
        raise HTTPException(status_code=404, detail="Icon size not found")
    
    icon_path = WEB_DIR / f"icon-{size}.png"
    if icon_path.exists():
        return FileResponse(icon_path, media_type="image/png")
    raise HTTPException(status_code=404, detail=f"icon-{size}.png not found")


@app.get("/favicon.ico")
async def favicon():
    """Return 204 No Content for favicon requests to avoid 404 errors in logs."""
    return Response(status_code=204)


@app.get("/health")
def health():
    return {"status": "ok"}


def _normalize_image(image_bytes: bytes, mime: str) -> bytes:
    """
    Decode and re-encode to JPEG to normalize and strip EXIF by default.
    Stage 1 Phase 1 implementation.
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
    request: Request,
    image: UploadFile = File(...),
    jurisdiction_id: str = Form("CA_DEFAULT"),
    client_request_id: Optional[str] = Form(None),
    locale: Optional[str] = Form(None),
):
    request_id = getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")

    if image.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=415, detail=f"Unsupported media type: {image.content_type}. Use JPG or PNG.")

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
    # Optional: frontend sends back the last top_labels from previous classification
    top_labels: Optional[List[LabelScore]] = None


@app.post("/v1/clarify", response_model=ClassifyResponse, responses={400: {"model": ErrorBody}})
def clarify(request: Request, payload: ClarifyRequest):
    # Use request_id from payload if provided, otherwise use the one from request.state
    request_id = payload.request_id or getattr(request.state, "request_id", f"req_{uuid.uuid4().hex[:12]}")
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
