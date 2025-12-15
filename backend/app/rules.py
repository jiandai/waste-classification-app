from __future__ import annotations
from typing import List, Optional, Tuple

from .schemas import (
    Result, RationaleItem, LabelScore, SpecialHandling, Clarification
)


def _confidence_bucket(score: float) -> str:
    if score >= 0.85:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    return "LOW"


def decide_bin_from_labels(
    labels: List[LabelScore],
    jurisdiction_id: str = "CA_DEFAULT"
) -> Tuple[Result, bool, Optional[Clarification], Optional[SpecialHandling]]:
    """
    Sprint 0 rules: simple and intentionally conservative.
    """
    rationale: List[RationaleItem] = []
    top = labels[:5]

    if not labels:
        res = Result(
            bin="UNKNOWN",
            bin_label="Not sure yet",
            confidence="LOW",
            confidence_score=0.0,
            rationale=[RationaleItem(type="SYSTEM", text="No labels returned")],
            top_labels=[]
        )
        clarification = Clarification(
            question_id="q_try_again_01",
            question_text="Could you retake the photo with one item and better lighting?",
            answer_type="BOOLEAN",
            options=[{"value": True, "label": "OK"}],
        )
        return res, True, clarification, None

    best = labels[0]
    rationale.append(RationaleItem(type="DETECTED_ITEM", text=f"Top match: {best.label}"))

    # Special handling first
    if best.label in {"battery"}:
        special = SpecialHandling(
            category="BATTERY",
            instructions="Do not place in curbside bins. Take to a household hazardous waste drop-off or a retailer collection point.",
            links=[]
        )
        res = Result(
            bin="SPECIAL",
            bin_label="Special handling",
            confidence=_confidence_bucket(best.score),
            confidence_score=float(best.score),
            rationale=rationale + [RationaleItem(type="SAFETY", text="Batteries require special disposal")],
            top_labels=top
        )
        return res, False, None, special

    # Clear organics
    if best.label in {"banana peel", "food"}:
        res = Result(
            bin="GREEN",
            bin_label="Organics",
            confidence=_confidence_bucket(best.score),
            confidence_score=float(best.score),
            rationale=rationale + [RationaleItem(type="RULE", text="Food and food scraps go in organics")],
            top_labels=top
        )
        return res, False, None, None

    # Clear recycling
    if best.label in {"plastic bottle", "aluminum can", "glass bottle"}:
        res = Result(
            bin="BLUE",
            bin_label="Recycling",
            confidence=_confidence_bucket(best.score),
            confidence_score=float(best.score),
            rationale=rationale + [RationaleItem(type="RULE", text="Rigid containers like bottles/cans typically go in recycling")],
            top_labels=top
        )
        return res, False, None, None

    # Likely trash: plastic film/bags are commonly trash curbside
    if best.label in {"plastic bag"}:
        res = Result(
            bin="GRAY",
            bin_label="Landfill (Trash)",
            confidence=_confidence_bucket(best.score),
            confidence_score=float(best.score),
            rationale=rationale + [RationaleItem(type="RULE", text="Plastic film/bags are usually not accepted in curbside recycling")],
            top_labels=top
        )
        return res, False, None, None

    # Ambiguous: paper box could be blue if clean, green/gray if food-soiled
    if best.label in {"paper box"}:
        clarification = Clarification(
            question_id="q_food_soiled_01",
            question_text="Is it food-soiled (grease/food residue)?",
            answer_type="BOOLEAN",
            options=[{"value": True, "label": "Yes"}, {"value": False, "label": "No"}]
        )
        res = Result(
            bin="UNKNOWN",
            bin_label="Not sure yet",
            confidence=_confidence_bucket(best.score),
            confidence_score=float(best.score),
            rationale=rationale + [RationaleItem(type="RULE", text="Paper can be recycling if clean; organics/trash if food-soiled")],
            top_labels=top
        )
        return res, True, clarification, None

    # Default conservative: unknown → clarification
    clarification = Clarification(
        question_id="q_unknown_01",
        question_text="I’m not confident. Is the item mostly food/plant-based?",
        answer_type="BOOLEAN",
        options=[{"value": True, "label": "Yes"}, {"value": False, "label": "No"}]
    )
    res = Result(
        bin="UNKNOWN",
        bin_label="Not sure yet",
        confidence=_confidence_bucket(best.score),
        confidence_score=float(best.score),
        rationale=rationale + [RationaleItem(type="SYSTEM", text="Falling back to clarification for safety")],
        top_labels=top
    )
    return res, True, clarification, None


def apply_clarification(question_id: str, answer: bool, prior_top_labels: List[LabelScore]) -> Result:
    """
    Sprint 0: simple clarification handler.
    """
    base_rationale = [RationaleItem(type="USER_INPUT", text=f"Answered {question_id} = {answer}")]

    if question_id == "q_food_soiled_01":
        if answer is True:
            return Result(
                bin="GREEN",
                bin_label="Organics",
                confidence="MEDIUM",
                confidence_score=0.70,
                rationale=base_rationale + [RationaleItem(type="RULE", text="Food-soiled paper goes in organics (where accepted)")],
                top_labels=prior_top_labels[:5],
            )
        return Result(
            bin="BLUE",
            bin_label="Recycling",
            confidence="MEDIUM",
            confidence_score=0.70,
            rationale=base_rationale + [RationaleItem(type="RULE", text="Clean paper/cardboard typically goes in recycling")],
            top_labels=prior_top_labels[:5],
        )

    if question_id == "q_unknown_01":
        return Result(
            bin="GREEN" if answer else "GRAY",
            bin_label="Organics" if answer else "Landfill (Trash)",
            confidence="LOW",
            confidence_score=0.55,
            rationale=base_rationale + [RationaleItem(type="RULE", text="Heuristic decision based on your answer")],
            top_labels=prior_top_labels[:5],
        )

    return Result(
        bin="UNKNOWN",
        bin_label="Not sure yet",
        confidence="LOW",
        confidence_score=0.0,
        rationale=base_rationale + [RationaleItem(type="SYSTEM", text="Unknown clarification question")],
        top_labels=prior_top_labels[:5],
    )

