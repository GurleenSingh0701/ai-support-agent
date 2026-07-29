# Technical Architecture Specification: Autodesk AI Multi-Agent Support System

## 1. System Overview

The **Autodesk AI Support Ticketing System** is an enterprise-grade, multi-agent customer support architecture designed to automate issue classification, intent routing, domain-specific resolution, policy search, and seamless human escalation handoff.

```
                               ┌───────────────────────────┐
                               │     Customer / Client     │
                               └─────────────┬─────────────┘
                                             │ HTTP / REST
                                             ▼
                               ┌───────────────────────────┐
                               │   Streamlit Frontend App  │
                               │    (Session Persistence)  │
                               └─────────────┬─────────────┘
                                             │ JWT Authenticated API
                                             ▼
                               ┌───────────────────────────┐
                               │    FastAPI Application    │
                               └─────────────┬─────────────┘
                                             │
                                             ▼
                               ┌───────────────────────────┐
                               │  LangGraph RouterAgent    │
                               │   (StateGraph Core Engine)│
                               └─────────────┬─────────────┘
                                             │
      ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
      │                      │                               │                      │
      ▼                      ▼                               ▼                      ▼
┌─────────────┐        ┌─────────────┐                ┌─────────────┐        ┌──────────────┐
│ OrderAgent  │        │PaymentAgent │                │RefundAgent  │        │ KBRetriever  │
└──────┬──────┘        └──────┬──────┘                └──────┬──────┘        └──────┬───────┘
       │                      │                              │                      │
       └──────────────────────┴───────────────┬──────────────┴──────────────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │   Resolution Engine /     │
                                │   Escalation Payload      │
                                └─────────────┬─────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │   Redis Pub/Sub Channel   │
                                │  (Human Support Queue)    │
                                └───────────────────────────┘
```

---

## 2. Multi-Agent Orchestration with LangGraph

The central decision engine is implemented in [backend/router/router_agent.py](file:///d:/New%20folder/autodesk/backend/router/router_agent.py). It uses a LangGraph `StateGraph` object managing an explicit `AgentState` schema:

### `AgentState` Schema
```python
class AgentState(TypedDict):
    user_query: str
    intent: Optional[str]
    confidence: float
    urgency: str
    sentiment: str
    frustrated: bool
    entities: Dict[str, Any]
    response: Optional[str]
    next_node: Optional[str]
    escalated: bool
    escalation_reason: Optional[str]
```

### Graph Execution & Node Pipeline

1. **`router_node`**:
   - Analyzes raw customer queries via Gemini AI (`gemini-3.1-flash-lite`).
   - Extracts structured JSON containing `intent`, `confidence` score (0.00 to 1.00), `urgency`, `sentiment`, `frustrated` flag, and extracted `entities` (e.g. `order_id`).
2. **Conditional Edge Evaluator (`route_query`)**:
   - If `frustrated == True` OR `confidence < 0.70` OR `urgency == "CRITICAL"` $\rightarrow$ Routes immediately to `escalation_node`.
   - If `intent == "ORDER_STATUS"` $\rightarrow$ Routes to `order_agent_node`.
   - If `intent == "REFUND_REQUEST"` $\rightarrow$ Routes to `refund_agent_node`.
   - If `intent == "PAYMENT_ISSUE"` $\rightarrow$ Routes to `payment_agent_node`.
   - Otherwise $\rightarrow$ Routes to `kb_policy_node`.
3. **Domain Sub-Agent Execution Nodes**:
   - `order_agent_node`: Executes `OrderAgent`, validating order IDs, delivery status, and provisioning logs.
   - `refund_agent_node`: Executes `ReturnRefundAgent`, checking policy windows and refund amounts.
   - `payment_agent_node`: Executes `PaymentAgent`, checking gateway receipts and settlement flags.
   - `kb_policy_node`: Searches internal policy base for general documentation questions.
4. **`escalation_node`**:
   - Triggered on low confidence or customer distress.
   - Compiles structured escalation metadata and broadcasts an event payload over Redis Pub/Sub (`autodesk:escalations`).

---

## 3. Intent & Urgency Classification Pipeline

### Intent Classification Categories
- `ORDER_STATUS`: Inquiries regarding license delivery, serial numbers, shipping, or fulfillment.
- `REFUND_REQUEST`: Requests to return products, process chargebacks, or request refunds.
- `PAYMENT_ISSUE`: Payment failures, invoice queries, or billing discrepancies.
- `TECHNICAL_SUPPORT`: Software crashes, installation errors, or system compatibility.
- `GENERAL_INQUIRY`: General pricing, feature questions, or corporate information.

### Urgency & Sentiment Classification
- **Sentiment Scores**: `POSITIVE`, `NEUTRAL`, `NEGATIVE`, `VERY_NEGATIVE`.
- **Urgency Levels**: `LOW`, `MEDIUM`, `HIGH`, `CRITICAL`.
- **Frustration Detection**: Evaluates tone, urgency, repeated attempts, or angry phrasing.

---

## 4. Redis Escalation Engine

When an escalation triggers, `EscalationHandler` ([backend/escalation/escalation_handler.py](file:///d:/New%20folder/autodesk/backend/escalation/escalation_handler.py)) formats a JSON event payload:

```json
{
  "event": "HUMAN_ESCALATION_REQUIRED",
  "timestamp": "2026-07-29T12:00:00Z",
  "reason": "Customer expressed high frustration and AI confidence fell below 0.70",
  "confidence": 0.45,
  "urgency": "CRITICAL",
  "user_query": "My payment failed 3 times and I need my CAD license immediately!",
  "extracted_entities": {
    "order_id": "ORD-99120"
  }
}
```
This payload is published to the Redis channel `autodesk:escalations`, enabling human agent consoles, Slack bots, or CRM systems to ingest incoming tickets in real time.

---

## 5. Security & Authentication Model

### JWT Lifecycle & RBAC
- **Token Generation**: Access tokens expire in 60 minutes; Refresh tokens expire in 7 days.
- **Role-Based Access Control (RBAC)**: Supports roles `CUSTOMER`, `SUPPORT_AGENT`, and `ADMIN`. Endpoint protection is enforced via `require_role(["ADMIN", "SUPPORT_AGENT"])` FastAPI dependencies.
- **Password Hashing**: Uses `bcrypt` (`$2b$`) for password hashing.

### Authentication Persistence Across Refreshes
- On sign in, access and refresh tokens are set in `st.session_state` and stored in URL query parameters (`session_token`, `refresh_token`).
- When the page is refreshed (F5), `frontend/app.py` intercepts query parameters, validates the token against `GET /auth/me`, or refreshes it via `POST /auth/refresh`, maintaining the user session seamlessly.

---

## 6. Database Schema & ORM Model

The system uses SQLAlchemy ORM mapping over PostgreSQL (with SQLite fallback for lightweight development):

- **`users` Table**: `id`, `username`, `password` (hashed), `role`.
- **`tickets` Table**: `id`, `ticket_number`, `user_id`, `subject`, `status` (`OPEN`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`), `priority`, `created_at`, `updated_at`.
- **`chats` Table**: `id`, `conversation_id`, `user_id`, `role` (`user`/`assistant`), `content`, `timestamp`.
