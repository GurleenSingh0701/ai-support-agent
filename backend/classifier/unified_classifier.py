import os
import json
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from google import genai

logging.basicConfig(level=logging.INFO)

class EntitySchema(BaseModel):
    order_id: Optional[str] = Field(default=None, description="Extracted order ID normalized to ORD-XXXXX format")
    product_name: Optional[str] = Field(default=None, description="Name of mentioned product or software")
    tracking_number: Optional[str] = Field(default=None, description="Shipment tracking number")
    amount: Optional[str] = Field(default=None, description="Monetary value or charge amount")

class ClassificationResult(BaseModel):
    primary_intent: str = Field(description="ORDER_INQUIRY | RETURN_REFUND | PAYMENT_ISSUE | POLICY_QUESTION | TECHNICAL_SUPPORT | HUMAN_ESCALATION | OTHER")
    secondary_intents: List[str] = Field(default_factory=list)
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")
    entities: EntitySchema
    sentiment: str = Field(description="VERY_POSITIVE | POSITIVE | NEUTRAL | NEGATIVE | VERY_NEGATIVE")
    urgency_score: int = Field(description="Urgency score from 1 to 100 based on frustration and business impact")
    priority: str = Field(description="LOW | MEDIUM | HIGH | CRITICAL")
    requires_escalation: bool = Field(description="True if sentiment is VERY_NEGATIVE, human is demanded, or query is ambiguous")
    escalation_reason: Optional[str] = Field(default=None)

def analyze_user_request(
    user_message: str,
    user_tier: str = "STANDARD",
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> ClassificationResult:
    """
    Unified Classifier Engine: Uses structured outputs to extract intent,
    entities, sentiment, and priority in a single model call.
    """
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

    if not api_key:
        logging.warning("GEMINI_API_KEY missing. Returning safe fallback classification.")
        return ClassificationResult(
            primary_intent="OTHER",
            confidence=0.0,
            entities=EntitySchema(),
            sentiment="NEUTRAL",
            urgency_score=50,
            priority="MEDIUM",
            requires_escalation=True,
            escalation_reason="API_KEY_MISSING"
        )

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
You are the Lead Support Intelligence Engine for Autodesk Customer Support.
Your job is to analyze incoming customer messages and output highly accurate, structured diagnostic data.

### ANALYSIS RULES:
1. **Intent Detection:** Determine the `primary_intent`. If the user asks about multiple unrelated things (e.g., "Where is my order and what is your return policy?"), put the secondary topics in `secondary_intents`. If the request is highly ambiguous or outside standard e-commerce bounds, classify as `OTHER`.
2. **Entity Extraction:** Extract IDs, products, and amounts. If a user asks about an order but does not provide an ID, leave `order_id` as `null`. **Do not hallucinate entities.**
3. **Sentiment & Urgency:** 
   - Analyze tone objectively. Words like "scam," "fraud," "sue," or ALL CAPS indicate `VERY_NEGATIVE` sentiment and `CRITICAL` priority.
   - If `User Tier` is "VIP", automatically add +20 to the `urgency_score` and bump the `priority` level up one tier.
4. **Escalation Triggers (`requires_escalation` = true):**
   - The user explicitly asks to speak to a human, manager, or agent.
   - The sentiment is `VERY_NEGATIVE` or contains legal/fraud threats.
   - The query is too ambiguous to answer safely (confidence below 0.70).

### INPUT CONTEXT:
- Customer Message: "{user_message}"
- Customer Tier: "{user_tier}"
- Recent Conversation History: {json.dumps(conversation_history or [])}
"""

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": ClassificationResult,
            }
        )

        if response and response.text:
            return ClassificationResult.model_validate_json(response.text)

    except Exception as e:
        logging.error(f"Error during unified classification: {e}")

    return ClassificationResult(
        primary_intent="OTHER",
        confidence=0.0,
        entities=EntitySchema(),
        sentiment="NEUTRAL",
        urgency_score=50,
        priority="MEDIUM",
        requires_escalation=True,
        escalation_reason="LLM_PROCESSING_ERROR"
    )