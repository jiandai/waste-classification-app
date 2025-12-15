from __future__ import annotations

import base64
import os
import random
from dataclasses import dataclass
from typing import List, Optional

import httpx
from openai import AsyncOpenAI

from pydantic import BaseModel, Field

from .schemas import LabelScore


class VisionLabels(BaseModel):
    """
    Structured output schema for OpenAI vision classification.
    """
    labels: List[LabelScore] = Field(default_factory=list)


@dataclass
class VisionProvider:
    """
    Adapter interface.
    mode:
      - "stub"  : deterministic-ish labels (Sprint 0)
      - "openai": real OpenAI vision call
    """
    mode: str = "stub"

    async def detect_labels(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> List[LabelScore]:
        if self.mode == "openai":
            return await self._detect_labels_openai(image_bytes=image_bytes, mime_type=mime_type)
        return self._detect_labels_stub(image_bytes=image_bytes)

    def _detect_labels_stub(self, image_bytes: bytes) -> List[LabelScore]:
        # Deterministic-ish behavior for testing:
        seed = sum(image_bytes[:2048]) % 10_000 if image_bytes else 0
        rng = random.Random(seed)

        label_pool = [
            ("plastic bottle", 0.70, 0.95),
            ("paper box", 0.55, 0.90),
            ("food", 0.40, 0.85),
            ("banana peel", 0.55, 0.95),
            ("battery", 0.60, 0.98),
            ("aluminum can", 0.65, 0.95),
            ("plastic bag", 0.55, 0.90),
            ("glass bottle", 0.60, 0.95),
        ]

        k = rng.choice([2, 3])
        choices = rng.sample(label_pool, k=k)
        labels = [LabelScore(label=name, score=rng.uniform(lo, hi)) for (name, lo, hi) in choices]
        labels.sort(key=lambda x: x.score, reverse=True)
        return labels

    async def _detect_labels_openai(self, image_bytes: bytes, mime_type: str) -> List[LabelScore]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            # Fail fast with clear error; caller can convert to HTTP error.
            raise RuntimeError("OPENAI_API_KEY is not set")

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")  # vision-capable example in SDK docs :contentReference[oaicite:4]{index=4}
        timeout_s = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))
        max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))
        base_url = os.getenv("OPENAI_BASE_URL")  # optional override, e.g. proxy; supported by SDK :contentReference[oaicite:5]{index=5}

        # Safe, bounded timeout. The SDK supports float or httpx.Timeout. :contentReference[oaicite:6]{index=6}
        timeout = httpx.Timeout(timeout_s, connect=min(5.0, timeout_s), read=timeout_s, write=timeout_s, pool=min(5.0, timeout_s))

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"

        # Prompt: keep it narrow and machine-consumable.
        prompt = (
            "You are a computer vision classifier for consumer waste items.\n"
            "Return 2-5 short, concrete labels describing the primary item in the photo.\n"
            "Examples of labels: 'plastic bottle', 'aluminum can', 'paper box', 'battery', 'glass bottle', 'plastic bag', 'food'.\n"
            "Also return a confidence score for each label between 0 and 1.\n"
            "If the photo is unclear, still return your best guess labels.\n"
        )

        # Responses API supports images via content array items with type input_image. :contentReference[oaicite:7]{index=7}
        # Structured outputs: responses.parse + text_format (Pydantic). :contentReference[oaicite:8]{index=8}
        resp = await client.responses.parse(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {"type": "input_image", "image_url": data_url},
                    ],
                }
            ],
            text_format=VisionLabels,
            # Recommended for stateless prototypes unless you explicitly want server-side storage. :contentReference[oaicite:9]{index=9}
            store=False,
            # Keep response small and bounded
            max_output_tokens=300,
        )

        parsed: Optional[VisionLabels] = getattr(resp, "output_parsed", None)
        if not parsed or not parsed.labels:
            # Fallback: empty list, caller will handle.
            return []

        # Normalize: cap scores into [0,1] and sort desc
        cleaned = []
        for ls in parsed.labels:
            score = float(ls.score)
            if score < 0.0:
                score = 0.0
            if score > 1.0:
                score = 1.0
            cleaned.append(LabelScore(label=ls.label.strip().lower(), score=score))

        cleaned.sort(key=lambda x: x.score, reverse=True)
        return cleaned


def get_provider() -> VisionProvider:
    mode = os.getenv("VISION_PROVIDER", "stub").strip().lower()
    return VisionProvider(mode=mode)
