# Autodesk AI Support & Multi-Agent Orchestration System

[![Python Version](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.140-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-1.2-orange.svg)](https://www.langchain.com/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.60-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)](https://www.docker.com/)

An enterprise-grade, autonomous **Multi-Agent Customer Support & Ticketing System** engineered for Autodesk support workflows. Powered by **FastAPI**, **LangGraph**, **Google Gemini 3.1 Flash-Lite**, **PostgreSQL**, **Redis**, and **Streamlit**.

---

## 🌟 Key Architecture & Highlights

- **LangGraph StateGraph Orchestrator**: Uses stateful graph workflows (`RouterAgent`) to perform zero-shot NLP intent classification, sentiment analysis, policy search, and conditional routing to specialized domain sub-agents.
- **Autonomous Intent & Urgency Triage**: Automatically categorizes customer inquiries into `ORDER_STATUS`, `REFUND_REQUEST`, `PAYMENT_ISSUE`, `TECHNICAL_SUPPORT`, or `GENERAL_INQUIRY` with confidence scoring.
- **Domain Sub-Agents**:
  - `OrderAgent`: Resolves order tracking, license provisioning, and delivery issues.
  - `PaymentAgent`: Handles invoice queries, payment gateways, and billing updates.
  - `ReturnRefundAgent`: Evaluates eligibility for software returns and processes refunds.
  - `KBPolicyRetriever`: Queries vector policy store for general customer questions.
- **Context-Rich Escalation Engine**: Broadcasts payloads via **Redis Pub/Sub** to human support queues when AI confidence drops below `0.70` or customer frustration/urgency is high (`PRIORITY: HIGH / CRITICAL`).
- **Persistent Authentication**: Complete JWT session management (access & refresh tokens) with seamless browser URL query-parameter restoration across page refreshes.
- **Production-Ready Containerization**: Full `docker-compose` configuration with PostgreSQL, Redis, FastAPI, Streamlit, and pgAdmin.

---

## 🏗️ System Architecture

```
                                  ┌──────────────────────────┐
                                  │   Streamlit Frontend     │
                                  │  (Support Dashboard UI)  │
                                  └────────────┬─────────────┘
                                               │ (HTTP REST / JWT)
                                               ▼
                                  ┌──────────────────────────┐
                                  │   FastAPI Backend API    │
                                  └────────────┬─────────────┘
                                               │
                                               ▼
                               ┌───────────────────────────────┐
                               │     LangGraph Router Agent    │
                               │    (NLP Intent & Urgency)     │
                               └───────┬───────────────┬───────┘
                                       │               │
                 ┌─────────────────────┼───────────────┼─────────────────────┐
                 │ Confidence >= 0.70  │               │ Frustration / < 0.70│
                 ▼                     ▼               ▼                     ▼
        ┌─────────────────┐   ┌─────────────────┐   ┌──────────────────┐  ┌───────────────────┐
        │   OrderAgent    │   │  PaymentAgent   │   │ ReturnRefundAgent│  │ EscalationEngine  │
        └─────────────────┘   └─────────────────┘   └──────────────────┘  │  (Redis Pub/Sub)  │
                                                                          └───────────────────┘
```

Detailed architectural documentation: [architecture.md](file:///d:/New%20folder/autodesk/architecture.md)  
Product Requirements Document: [prd.md](file:///d:/New%20folder/autodesk/prd.md)

---

## 🛠️ Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend** | Streamlit, HTML5/CSS3 | Modern dashboard, interactive chat, persistent session state |
| **Backend Framework** | FastAPI, Pydantic v2 | High-performance asynchronous API service |
| **Multi-Agent Engine** | LangGraph, LangChain | StateGraph multi-agent routing & conditional execution |
| **LLM Provider** | Google Gemini (`gemini-3.1-flash-lite`) | Natural language understanding, entity extraction & generation |
| **Database** | PostgreSQL (psycopg3) / SQLite | Relational ORM storage for users, tickets, and messages |
| **Pub/Sub & Caching** | Redis 7 | Event broadcasting for human agent escalation payloads |
| **Security** | PyJWT, Bcrypt, OAuth2 | Password hashing, role-based access control (RBAC) |
| **Containerization** | Docker, Docker Compose | Multi-container setup for local & cloud deployments |

---

## 🚀 Quick Start (Local Setup)

### Option A: Running with Docker Compose (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/autodesk-support-system.git
   cd autodesk-support-system
   ```

2. Create a `.env` file in the root directory:
   ```bash
   cp .env.prod .env
   # Add your GEMINI_API_KEY inside .env
   ```

3. Build and launch all services:
   ```bash
   docker-compose up --build
   ```

4. Access the web applications:
   - **Frontend Support Portal**: `http://localhost:8502`
   - **FastAPI API Documentation**: `http://localhost:8000/docs`
   - **pgAdmin**: `http://localhost:5050`

---

### Option B: Local Python Development

1. Create and activate a Python 3.12 virtual environment:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the FastAPI Backend:
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

4. In a separate terminal, run the Streamlit Frontend:
   ```bash
   streamlit run frontend/app.py
   ```

---

## 🧪 Testing & CLI Demo Runner

### Interactive CLI Test Runner
Test intent classification, sentiment analysis, LangGraph agent routing, and escalation payloads interactively:
```bash
python backend/tests/run_demo.py
```

### Automated Pytest Suite
Run the full unit and integration test suite:
```bash
pytest backend/tests/
```

---

## 📁 Repository Structure

```
autodesk/
├── backend/
│   ├── main.py                     # FastAPI application entrypoint
│   ├── config.py                   # Pydantic environment configuration
│   ├── database.py                 # SQLAlchemy engine & DB sessions
│   ├── classifier/                 # NLP Intent & Priority classifiers
│   │   ├── intent_classifier.py
│   │   └── priority_classifier.py
│   ├── router/                     # LangGraph Router Orchestrator
│   │   └── router_agent.py
│   ├── sub_agents/                 # Domain resolution agents
│   │   ├── order_agent.py
│   │   ├── payment_agent.py
│   │   └── return_refund_agent.py
│   ├── escalation/                 # Redis Pub/Sub escalation handler
│   │   └── escalation_handler.py
│   ├── resolution/                 # Unified resolution engine
│   │   └── resolution_engine.py
│   ├── kb/                         # Knowledge Base policy retriever
│   │   └── kb_retriever.py
│   ├── users/                      # Authentication & User CRUD
│   ├── tickets/                    # Ticket CRUD & Management
│   ├── chat/                       # Chat history CRUD
│   └── tests/                      # Automated test suite & CLI runner
├── frontend/
│   ├── app.py                      # Streamlit entrypoint & page router
│   ├── config.py                   # Frontend backend URL resolution
│   ├── pages/                      # Application pages (Dashboard, Auth, Chat)
│   ├── components/                 # Reusable UI components (Sidebar)
│   └── utils/                      # API client & auth persistence
├── docker-compose.yml              # Multi-container orchestration
├── .env.prod                       # Production environment template
├── architecture.md                 # Detailed architecture documentation
├── prd.md                          # Product Requirements Document
└── README.md                       # Repository guide
```

---

## 🌐 Deployment Guides

- **Railway & Render Guide**: [railway_render_deployment_guide.md](file:///C:/Users/gurle/.gemini/antigravity-ide/brain/83811134-6411-4f2a-a593-a85211a28106/railway_render_deployment_guide.md)
- **VPS / EC2 Docker Guide**: [deployment_guide.md](file:///C:/Users/gurle/.gemini/antigravity-ide/brain/83811134-6411-4f2a-a593-a85211a28106/deployment_guide.md)

---

## 📜 License

This project is licensed under the MIT License - see the `LICENSE` file for details.
