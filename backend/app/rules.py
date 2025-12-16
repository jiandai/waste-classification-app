from __future__ import annotations
from typing import List, Optional, Tuple

from .schemas import (
    Result, RationaleItem, LabelScore, SpecialHandling, Clarification, ItemProfile
)


def _confidence_bucket(score: float) -> str:
    if score >= 0.85:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    return "LOW"


def decide_bin_from_profile(
    profile: ItemProfile,
    jurisdiction_id: str = "CA_DEFAULT"
) -> Tuple[Result, bool, Optional[Clarification], Optional[SpecialHandling]]:
    """
    Decision table-based rules operating on ItemProfile.
    Scales because it operates on classes, not specific label instances.
    """
    rationale: List[RationaleItem] = []
    
    # Store raw labels for debugging if available
    top_labels = profile.raw_labels[:5] if profile.raw_labels else []
    
    # Build rationale from profile
    rationale.append(RationaleItem(
        type="DETECTED_ITEM",
        text=f"Material: {profile.material}, Form: {profile.form_factor}, Contamination: {profile.contamination_risk}"
    ))

    # Decision Table Logic (order matters)

    # 1. Special handling first
    if profile.special_handling != "none":
        special_category_map = {
            "battery": "BATTERY",
            "e_waste": "E_WASTE",
            "hhw": "HHW",
            "sharps": "SHARPS"
        }
        category = special_category_map.get(profile.special_handling, "UNKNOWN")
        
        instructions_map = {
            "battery": "Do not place in curbside bins. Take to a household hazardous waste drop-off or a retailer collection point.",
            "e_waste": "Do not place in curbside bins. Take to an e-waste collection facility or retailer drop-off.",
            "hhw": "Do not place in curbside bins. Take to a household hazardous waste collection facility.",
            "sharps": "Do not place in curbside bins. Use a sharps container and take to a designated collection site."
        }
        instructions = instructions_map.get(profile.special_handling, "Requires special disposal. Check local guidelines.")
        
        special = SpecialHandling(
            category=category,
            instructions=instructions,
            links=[]
        )
        res = Result(
            bin="SPECIAL",
            bin_label="Special handling",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="SAFETY", text=f"{profile.special_handling.replace('_', ' ').title()} requires special disposal")],
            top_labels=top_labels
        )
        return res, False, None, special

    # 2. Organics
    if profile.material == "organic":
        res = Result(
            bin="GREEN",
            bin_label="Organics",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="RULE", text="Organic materials go in organics")],
            top_labels=top_labels
        )
        return res, False, None, None

    # 3. Clear recycling: clean rigid containers
    recyclable_materials = {"paper_cardboard", "metal", "glass", "rigid_plastic"}
    if profile.material in recyclable_materials and profile.contamination_risk == "low":
        res = Result(
            bin="BLUE",
            bin_label="Recycling",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="RULE", text="Clean recyclable materials go in recycling")],
            top_labels=top_labels
        )
        return res, False, None, None

    # 4. Film plastic → trash (typically not accepted curbside)
    if profile.material == "film_plastic":
        res = Result(
            bin="GRAY",
            bin_label="Landfill (Trash)",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="RULE", text="Plastic film/bags are usually not accepted in curbside recycling")],
            top_labels=top_labels
        )
        return res, False, None, None

    # 5. Paper/cardboard with unknown contamination → ask clarification
    if profile.material == "paper_cardboard" and profile.contamination_risk == "unknown":
        clarification = Clarification(
            question_id="q_food_soiled_01",
            question_text="Is it food-soiled (grease/food residue)?",
            answer_type="BOOLEAN",
            options=[{"value": True, "label": "Yes"}, {"value": False, "label": "No"}]
        )
        res = Result(
            bin="UNKNOWN",
            bin_label="Not sure yet",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="RULE", text="Paper can be recycling if clean; organics/trash if food-soiled")],
            top_labels=top_labels
        )
        return res, True, clarification, None

    # 6. Paper/cardboard with high contamination → organics or trash (policy-dependent)
    if profile.material == "paper_cardboard" and profile.contamination_risk == "high":
        # Default to organics where accepted, otherwise trash
        res = Result(
            bin="GREEN",
            bin_label="Organics",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="RULE", text="Food-soiled paper goes in organics (where accepted)")],
            top_labels=top_labels
        )
        return res, False, None, None

    # 7. Paper/cardboard with medium contamination → ask or default to organics
    if profile.material == "paper_cardboard" and profile.contamination_risk == "medium":
        res = Result(
            bin="GREEN",
            bin_label="Organics",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="RULE", text="Moderately soiled paper typically goes in organics")],
            top_labels=top_labels
        )
        return res, False, None, None

    # 8. Recyclable materials with contamination → trash
    if profile.material in recyclable_materials and profile.contamination_risk in {"medium", "high"}:
        res = Result(
            bin="GRAY",
            bin_label="Landfill (Trash)",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="RULE", text="Contaminated recyclables typically go in trash")],
            top_labels=top_labels
        )
        return res, False, None, None

    # 9. Unknown material or form factor → clarification
    if profile.material == "unknown" or profile.form_factor == "unknown":
        clarification = Clarification(
            question_id="q_unknown_01",
            question_text="I'm not confident. Is the item mostly food/plant-based?",
            answer_type="BOOLEAN",
            options=[{"value": True, "label": "Yes"}, {"value": False, "label": "No"}]
        )
        res = Result(
            bin="UNKNOWN",
            bin_label="Not sure yet",
            confidence=_confidence_bucket(profile.confidence),
            confidence_score=float(profile.confidence),
            rationale=rationale + [RationaleItem(type="SYSTEM", text="Falling back to clarification for safety")],
            top_labels=top_labels
        )
        return res, True, clarification, None

    # 10. Default fallback
    clarification = Clarification(
        question_id="q_unknown_01",
        question_text="I'm not confident. Is the item mostly food/plant-based?",
        answer_type="BOOLEAN",
        options=[{"value": True, "label": "Yes"}, {"value": False, "label": "No"}]
    )
    res = Result(
        bin="UNKNOWN",
        bin_label="Not sure yet",
        confidence=_confidence_bucket(profile.confidence),
        confidence_score=float(profile.confidence),
        rationale=rationale + [RationaleItem(type="SYSTEM", text="Unable to determine classification")],
        top_labels=top_labels
    )
    return res, True, clarification, None


def decide_bin_from_labels(
    labels: List[LabelScore],
    jurisdiction_id: str = "CA_DEFAULT"
) -> Tuple[Result, bool, Optional[Clarification], Optional[SpecialHandling]]:
    """
    DEPRECATED: Legacy function kept for backward compatibility.
    Use decide_bin_from_profile instead.
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
        question_text="I'm not confident. Is the item mostly food/plant-based?",
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

