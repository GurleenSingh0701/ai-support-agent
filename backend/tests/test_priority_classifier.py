import pytest
from classifier.priority_classifier import calculate_priority

def test_priority_very_negative():
    res = calculate_priority("This service is a total scam! I am angry and furious!")
    assert res["sentiment"] == "VERY_NEGATIVE"
    assert res["urgency_score"] >= 85
    assert res["priority"] == "CRITICAL"

def test_priority_negative_urgency():
    res = calculate_priority("I need help asap with my broken item", user_tier="STANDARD")
    assert res["sentiment"] == "NEGATIVE"
    assert res["urgency_score"] == 75
    assert res["priority"] == "HIGH"

def test_priority_neutral():
    res = calculate_priority("Please help me find the size chart")
    assert res["sentiment"] == "NEUTRAL"
    assert res["urgency_score"] == 50
    assert res["priority"] == "MEDIUM"

def test_priority_positive():
    res = calculate_priority("Thank you for your great recommendations")
    assert res["sentiment"] == "POSITIVE"
    assert res["urgency_score"] == 30
    assert res["priority"] == "LOW"

def test_vip_user_boost():
    standard_res = calculate_priority("I need help asap with my broken item", user_tier="STANDARD")
    vip_res = calculate_priority("I need help asap with my broken item", user_tier="VIP")
    
    assert standard_res["urgency_score"] == 75
    assert vip_res["urgency_score"] == 95
    assert standard_res["priority"] == "HIGH"
    assert vip_res["priority"] == "CRITICAL"
