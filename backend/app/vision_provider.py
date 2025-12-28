from __future__ import annotations

import base64
import os
import random
from dataclasses import dataclass
from typing import List, Optional

import httpx
from openai import AsyncOpenAI

from pydantic import BaseModel, Field

from .schemas import LabelScore, ItemProfile


class VisionLabels(BaseModel):
    """
    Structured output schema for OpenAI vision classification.
    DEPRECATED: Kept for backward compatibility during transition.
    """
    labels: List[LabelScore] = Field(default_factory=list)


@dataclass
class VisionProvider:
    """
    Adapter interface for vision AI providers.
    
    Modes:
      - "stub"  : deterministic mock data for testing (Stage 1 Phase 1)
      - "openai": real OpenAI vision API calls
    """
    mode: str = "stub"

    async def detect_labels(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> List[LabelScore]:
        """
        DEPRECATED: Use detect_item_profile instead.
        Kept for backward compatibility.
        """
        if self.mode == "openai":
            return await self._detect_labels_openai(image_bytes=image_bytes, mime_type=mime_type)
        return self._detect_labels_stub(image_bytes=image_bytes)

    async def detect_item_profile(self, image_bytes: bytes, mime_type: str = "image/jpeg") -> ItemProfile:
        """
        Main method: returns ItemProfile using structured outputs from OpenAI.
        """
        if self.mode == "openai":
            return await self._detect_item_profile_openai(image_bytes=image_bytes, mime_type=mime_type)
        return self._detect_item_profile_stub(image_bytes=image_bytes)

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

    def _detect_item_profile_stub(self, image_bytes: bytes) -> ItemProfile:
        """
        Stub implementation that returns ItemProfile for testing.
        """
        # Deterministic-ish behavior for testing:
        seed = sum(image_bytes[:2048]) % 10_000 if image_bytes else 0
        rng = random.Random(seed)

        # Map stub labels to ItemProfile
        label_pool = [
            ("plastic bottle", "rigid_plastic", "bottle", "low", "none", 0.85),
            ("paper box", "paper_cardboard", "box", "unknown", "none", 0.75),
            ("food", "organic", "unknown", "low", "none", 0.80),
            ("banana peel", "organic", "unknown", "low", "none", 0.90),
            ("battery", "unknown", "unknown", "low", "battery", 0.95),
            ("aluminum can", "metal", "can", "low", "none", 0.88),
            ("plastic bag", "film_plastic", "bag_film", "low", "none", 0.82),
            ("glass bottle", "glass", "bottle", "low", "none", 0.87),
        ]

        choice = rng.choice(label_pool)
        label_name, material, form_factor, contamination, special, confidence = choice

        # Generate some raw labels for debugging
        raw_labels = [
            LabelScore(label=label_name, score=confidence),
            LabelScore(label="other item", score=rng.uniform(0.3, 0.5)),
        ]

        return ItemProfile(
            material=material,
            form_factor=form_factor,
            contamination_risk=contamination,
            special_handling=special,
            confidence=confidence,
            raw_labels=raw_labels
        )

    async def _detect_item_profile_openai(self, image_bytes: bytes, mime_type: str) -> ItemProfile:
        """
        Uses OpenAI structured outputs to directly return ItemProfile.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set")

        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        timeout_s = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "20"))
        max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))
        base_url = os.getenv("OPENAI_BASE_URL")

        timeout = httpx.Timeout(timeout_s, connect=min(5.0, timeout_s), read=timeout_s, write=timeout_s, pool=min(5.0, timeout_s))

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        b64 = base64.b64encode(image_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64}"

        # Prompt: ask for structured ItemProfile
        prompt = (
            "You are a computer vision classifier for consumer waste items.\n"
            "Analyze the image and classify the waste item into a structured profile.\n\n"
            "Material options: paper_cardboard, rigid_plastic, film_plastic, metal, glass, organic, textile, unknown\n"
            "Form factor options: bottle, can, box, bag_film, cup, tray, utensil, sheet, mixed, unknown\n"
            "Contamination risk: low (clean/dry), medium (some residue), high (heavily soiled), unknown\n"
            "Special handling: battery, e_waste, hhw (household hazardous waste), sharps, none\n\n"
            "Provide your best classification with a confidence score between 0 and 1.\n"
            "If uncertain about any attribute, use 'unknown' rather than guessing.\n\n"
            "In the raw_labels field, include 2-5 descriptive labels (e.g., 'plastic bottle', 'aluminum can', 'paper box') "
            "with confidence scores between 0 and 1. This helps with debugging and transparency.\n"
        )

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
            text_format=ItemProfile,
            store=False,
            max_output_tokens=500,
        )

        parsed: Optional[ItemProfile] = getattr(resp, "output_parsed", None)
        if not parsed:
            # Fallback: return unknown profile
            return ItemProfile(
                material="unknown",
                form_factor="unknown",
                contamination_risk="unknown",
                special_handling="none",
                confidence=0.0,
                raw_labels=[]
            )

        # Normalize confidence to [0,1]
        if parsed.confidence < 0.0:
            parsed.confidence = 0.0
        if parsed.confidence > 1.0:
            parsed.confidence = 1.0

        return parsed


def get_provider() -> VisionProvider:
    mode = os.getenv("VISION_PROVIDER", "stub").strip().lower()
    return VisionProvider(mode=mode)
