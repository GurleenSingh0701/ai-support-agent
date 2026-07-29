import pytest
from unittest.mock import MagicMock, patch
from classifier.intent_classifier import classify_intent

def test_classify_intent_no_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    
    # Without an API key the rule-based fallback still classifies confidently
    # enough to avoid forcing an unnecessary human escalation.
    result = classify_intent("Where is my order?")
    
    assert result["intent"] == "ORDER_INQUIRY"
    assert result["confidence"] >= 0.70
    assert result["is_multi_intent"] is False


def test_classify_intent_no_api_key_truly_ambiguous(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    # A message with no recognizable keywords still correctly falls back to OTHER/0.0,
    # which is the signal the router uses to escalate to a human.
    result = classify_intent("asdkjhasd qweqwe")

    assert result["intent"] == "OTHER"
    assert result["confidence"] == 0.0


def test_rule_based_order_id_extraction(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    result = classify_intent("Where is my order #12345?")
    assert result["entities"]["order_id"] == "ORD-12345"

@patch("classifier.intent_classifier.genai.Client")
def test_classify_intent_success(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key_123")
    
    mock_response = MagicMock()
    mock_response.text = '{"intent": "ORDER_INQUIRY", "confidence": 0.95, "entities": {"order_id": "999"}, "is_multi_intent": false}'
    
    mock_instance = MagicMock()
    mock_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_instance
    
    result = classify_intent("Where is my order #999?")
    
    assert result["intent"] == "ORDER_INQUIRY"
    assert result["confidence"] == 0.95
    assert result["entities"] == {"order_id": "999"}
    assert result["is_multi_intent"] is False

@patch("classifier.intent_classifier.genai.Client")
def test_classify_intent_with_markdown_fences(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key_123")
    
    mock_response = MagicMock()
    mock_response.text = '```json\n{"intent": "RETURN_REFUND", "confidence": 0.88, "entities": {}, "is_multi_intent": false}\n```'
    
    mock_instance = MagicMock()
    mock_instance.models.generate_content.return_value = mock_response
    mock_genai_client.return_value = mock_instance
    
    result = classify_intent("I want to return my purchase")
    
    assert result["intent"] == "RETURN_REFUND"
    assert result["confidence"] == 0.88

@patch("classifier.intent_classifier.genai.Client")
def test_classify_intent_exception_fallback(mock_genai_client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_key_123")
    mock_genai_client.side_effect = Exception("API connection error")
    
    result = classify_intent("Hello support")
    
    assert result["intent"] == "OTHER"
    assert result["confidence"] == 0.0
