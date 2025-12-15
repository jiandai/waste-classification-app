from pydantic import BaseModel, Field
from typing import List, Optional, Literal


BinType = Literal["BLUE", "GREEN", "GRAY", "SPECIAL", "UNKNOWN"]
Confidence = Literal["HIGH", "MEDIUM", "LOW"]


class LabelScore(BaseModel):
    label: str
    score: float = Field(ge=0.0, le=1.0)


class RationaleItem(BaseModel):
    type: Literal["DETECTED_ITEM", "RULE", "USER_INPUT", "SAFETY", "SYSTEM"]
    text: str


class SpecialHandling(BaseModel):
    category: Literal["BATTERY", "E_WASTE", "HHW", "SHARPS", "UNKNOWN"]
    instructions: str
    links: List[str] = []


class Clarification(BaseModel):
    question_id: str
    question_text: str
    answer_type: Literal["BOOLEAN"]
    options: List[dict]


class Result(BaseModel):
    bin: BinType
    bin_label: str
    confidence: Confidence
    confidence_score: float = Field(ge=0.0, le=1.0)
    rationale: List[RationaleItem]
    top_labels: List[LabelScore] = []


class ClassifyResponse(BaseModel):
    request_id: str
    jurisdiction_id: str
    result: Result
    needs_clarification: bool
    clarification: Optional[Clarification]
    special_handling: Optional[SpecialHandling]


class ErrorBody(BaseModel):
    request_id: str
    error: dict

