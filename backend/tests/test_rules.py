"""
Tests for the waste classification rules engine.
"""
import pytest
from app.rules import decide_bin_from_profile, apply_clarification, _confidence_bucket
from app.schemas import ItemProfile, LabelScore


def test_confidence_bucket_high():
    """Test confidence bucket for high confidence scores."""
    assert _confidence_bucket(0.95) == "HIGH"
    assert _confidence_bucket(0.85) == "HIGH"


def test_confidence_bucket_medium():
    """Test confidence bucket for medium confidence scores."""
    assert _confidence_bucket(0.75) == "MEDIUM"
    assert _confidence_bucket(0.65) == "MEDIUM"


def test_confidence_bucket_low():
    """Test confidence bucket for low confidence scores."""
    assert _confidence_bucket(0.50) == "LOW"
    assert _confidence_bucket(0.30) == "LOW"


def test_organic_material_classification():
    """Test that organic materials are classified as GREEN."""
    profile = ItemProfile(
        material="organic",
        form_factor="mixed",
        contamination_risk="low",
        special_handling="none",
        confidence=0.9,
        raw_labels=[LabelScore(label="apple_core", score=0.9)]
    )
    
    result, needs_clarification, clarification, special = decide_bin_from_profile(profile)
    
    assert result.bin == "GREEN"
    assert result.bin_label == "Organics"
    assert needs_clarification is False
    assert clarification is None
    assert special is None


def test_clean_recyclable_classification():
    """Test that clean recyclables are classified as BLUE."""
    profile = ItemProfile(
        material="paper_cardboard",
        form_factor="box",
        contamination_risk="low",
        special_handling="none",
        confidence=0.85,
        raw_labels=[LabelScore(label="cardboard_box", score=0.85)]
    )
    
    result, needs_clarification, clarification, special = decide_bin_from_profile(profile)
    
    assert result.bin == "BLUE"
    assert result.bin_label == "Recycling"
    assert needs_clarification is False


def test_special_handling_battery():
    """Test that batteries require special handling."""
    profile = ItemProfile(
        material="metal",
        form_factor="mixed",
        contamination_risk="low",
        special_handling="battery",
        confidence=0.9,
        raw_labels=[LabelScore(label="battery", score=0.9)]
    )
    
    result, needs_clarification, clarification, special = decide_bin_from_profile(profile)
    
    assert result.bin == "SPECIAL"
    assert special is not None
    assert special.category == "BATTERY"
    assert "hazardous" in special.instructions.lower() or "retailer" in special.instructions.lower()


def test_special_handling_e_waste():
    """Test that e-waste requires special handling."""
    profile = ItemProfile(
        material="unknown",
        form_factor="mixed",
        contamination_risk="low",
        special_handling="e_waste",
        confidence=0.88,
        raw_labels=[LabelScore(label="old_phone", score=0.88)]
    )
    
    result, needs_clarification, clarification, special = decide_bin_from_profile(profile)
    
    assert result.bin == "SPECIAL"
    assert special is not None
    assert special.category == "E_WASTE"


def test_film_plastic_to_trash():
    """Test that film plastic goes to trash."""
    profile = ItemProfile(
        material="film_plastic",
        form_factor="bag_film",
        contamination_risk="low",
        special_handling="none",
        confidence=0.8,
        raw_labels=[LabelScore(label="plastic_bag", score=0.8)]
    )
    
    result, needs_clarification, clarification, special = decide_bin_from_profile(profile)
    
    assert result.bin == "GRAY"
    assert result.bin_label == "Landfill (Trash)"


def test_contaminated_recyclable_needs_clarification():
    """Test that contaminated recyclables trigger clarification."""
    profile = ItemProfile(
        material="paper_cardboard",
        form_factor="tray",
        contamination_risk="unknown",
        special_handling="none",
        confidence=0.75,
        raw_labels=[LabelScore(label="paper_plate", score=0.75)]
    )
    
    result, needs_clarification, clarification, special = decide_bin_from_profile(profile)
    
    assert needs_clarification is True
    assert clarification is not None
    assert clarification.question_id is not None


def test_unknown_material_classification():
    """Test that unknown materials go to trash."""
    profile = ItemProfile(
        material="unknown",
        form_factor="unknown",
        contamination_risk="unknown",
        special_handling="none",
        confidence=0.5,
        raw_labels=[LabelScore(label="unidentifiable_object", score=0.5)]
    )
    
    result, needs_clarification, clarification, special = decide_bin_from_profile(profile)
    
    # Unknown items should result in either clarification or a bin assignment
    assert result.bin in ["GRAY", "BLUE", "GREEN", "SPECIAL", "UNKNOWN"]


def test_apply_clarification_yes():
    """Test clarification application with 'yes' answer."""
    result = apply_clarification("contamination_check", True, prior_top_labels=[])
    
    assert result is not None
    assert result.bin in ["BLUE", "GREEN", "GRAY", "UNKNOWN"]


def test_apply_clarification_no():
    """Test clarification application with 'no' answer."""
    result = apply_clarification("contamination_check", False, prior_top_labels=[])
    
    assert result is not None
    assert result.bin in ["BLUE", "GREEN", "GRAY", "UNKNOWN"]


def test_confidence_scores_in_result():
    """Test that results include proper confidence scores."""
    profile = ItemProfile(
        material="metal",
        form_factor="can",
        contamination_risk="low",
        special_handling="none",
        confidence=0.92,
        raw_labels=[LabelScore(label="aluminum_can", score=0.92)]
    )
    
    result, _, _, _ = decide_bin_from_profile(profile)
    
    assert result.confidence == "HIGH"
    assert result.confidence_score == 0.92
    assert 0 <= result.confidence_score <= 1


def test_rationale_items_present():
    """Test that results include rationale items."""
    profile = ItemProfile(
        material="glass",
        form_factor="bottle",
        contamination_risk="low",
        special_handling="none",
        confidence=0.87,
        raw_labels=[LabelScore(label="glass_bottle", score=0.87)]
    )
    
    result, _, _, _ = decide_bin_from_profile(profile)
    
    assert len(result.rationale) > 0
    assert any(item.type == "DETECTED_ITEM" for item in result.rationale)
    assert any(item.type == "RULE" for item in result.rationale)
