# Product Requirements Document (PRD)

## Product Name: Autodesk AI Support & Multi-Agent Ticketing System
**Version**: 2.2.0  
**Status**: Production-Ready  
**Target Audience**: Autodesk Enterprise Customers, Customer Support Agents, System Administrators

---

## 1. Executive Summary & Vision

The **Autodesk AI Support & Multi-Agent Ticketing System** automates first-line support for Autodesk software customers. By deploying an autonomous multi-agent orchestration architecture powered by **LangGraph** and **Google Gemini 3.1 Flash-Lite**, the system handles common order queries, payment issues, and policy questions in real time while routing complex or high-frustration cases directly to human support teams with complete contextual payloads.

---

## 2. Key Objectives & Key Results (OKRs)

- **Objective 1**: Reduce average resolution time for tier-1 support requests from 4 hours to under 30 seconds.
  - *KR1*: Achieve $> 85\%$ resolution accuracy on automated order, refund, and payment inquiries.
  - *KR2*: Maintain zero automated false positives on high-frustration customer complaints by enforcing AI confidence gating ($< 0.70 \rightarrow$ Escalation).
- **Objective 2**: Provide continuous, seamless customer portal experience.
  - *KR1*: $100\%$ session retention across browser reloads via query-parameter & JWT token refresh lifecycles.
  - *KR2*: $< 100\text{ms}$ local database query latency and $< 2\text{s}$ full LLM agent routing latency.

---

## 3. Detailed Feature Requirements

### 3.1 Authentication & Profile Management
- **User Registration & Login**: Support registration with username and password. Password hashed using `bcrypt`.
- **JWT Session Tokens**: Short-lived access token (60 min) and long-lived refresh token (7 days).
- **Persistent Auth**: Intercepts `session_token` and `refresh_token` from URL parameters on Streamlit page reloads to maintain state without forced re-login.
- **Role-Based Access Control (RBAC)**: Distinguishes between `CUSTOMER`, `SUPPORT_AGENT`, and `ADMIN`.

### 3.2 NLP Intent & Priority Triage Engine
- **Intent Classifier**: Categorizes queries into `ORDER_STATUS`, `REFUND_REQUEST`, `PAYMENT_ISSUE`, `TECHNICAL_SUPPORT`, or `GENERAL_INQUIRY`.
- **Entity Extraction**: Automatically extracts structural attributes such as `order_id` (e.g. `ORD-88492`).
- **Urgency & Sentiment Analysis**: Detects customer sentiment (`POSITIVE`, `NEUTRAL`, `NEGATIVE`, `VERY_NEGATIVE`) and urgency level (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- **Frustration Detection**: Sets `frustrated=True` when tone indicates customer distress, triggering immediate human agent handoff.

### 3.3 LangGraph Multi-Agent Routing
- **StateGraph Orchestrator**: Maintains structured execution graph with explicit state tracking.
- **Domain Sub-Agents**:
  - `OrderAgent`: Resolves order tracking, license key delivery, and fulfillment status.
  - `PaymentAgent`: Resolves billing receipts, card authorization errors, and settlement status.
  - `ReturnRefundAgent`: Resolves refund requests against company policy constraints.
  - `KBPolicyRetriever`: Evaluates policy documents for general inquiries.

### 3.4 Context-Rich Human Escalation Engine
- **Confidence Threshold**: Any AI agent confidence evaluation below `0.70` automatically triggers escalation.
- **Redis Pub/Sub Event Broadcast**: Emits a structured JSON payload containing user query, extracted entities, frustration markers, and confidence score to the `autodesk:escalations` channel.

### 3.5 Support Console & Analytics Dashboard
- **Summary Metrics**: Real-time breakdown of Total Tickets, Pending Responses, Resolved Tickets, and Average Response Time.
- **Ticket Management**: Create, view, filter, and track support ticket statuses (`OPEN`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`).
- **Interactive AI Support Chat**: Interactive conversation interface with memory and ticket context.

---

## 4. Non-Functional Requirements

- **Security**: Strict CORS headers, environment variable isolation, encrypted JWT signatures, SQL injection protection via SQLAlchemy ORM.
- **Reliability**: Graceful fallback to SQLite when PostgreSQL drivers are missing; automatic token refresh on 401 Unauthorized errors.
- **Maintainability**: Comprehensive pytest suite (`backend/tests/`) covering classifiers, handlers, sub-agents, router, and authentication logic.
- **Portability**: Containerized using standard `Dockerfile` and `docker-compose.yml` for deployment on single-host VPS, Railway, Render, AWS, or GCP.
