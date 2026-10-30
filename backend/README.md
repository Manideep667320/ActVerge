# ActVerge Backend — LangGraph Agent & Outcome-Verification Engine

[![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2-FF6F00?logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![SQLModel](https://img.shields.io/badge/SQLModel-0.0.19-blue)](https://sqlmodel.tiangolo.com)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-Universal%20Gateway-green)](https://litellm.ai)

The ActVerge backend is a high-performance Python 3.12 service powered by **FastAPI** and **LangGraph**. It coordinates autonomous web execution, multi-modal evidence collection (DOM, screenshots, console telemetry, AOM, network logs), adversarial outcome verification, and cyclical self-healing.

---

## 🏛️ LangGraph Pipeline Architecture

ActVerge implements a stateful cyclical agent graph (`actverge/agents/graph.py`) using `LangGraph`:

```mermaid
flowchart TD
    Start([Task Enqueued]) --> TaskInterp["1. Task Interpreter<br/>(Decomposes goal & assesses risk)"]
    TaskInterp --> Executor["2. Dual-Mode Playwright Executor<br/>(Executes browser actions)"]
    Executor --> Observer["3. State Observer<br/>(Captures post-action DOM & CDP telemetry)"]
    Observer --> Evidence["4. Evidence Collector<br/>(Compiles 6-stream evidence package)"]
    Evidence --> Verifier{"5. Outcome Verifier Node<br/>(LLM + Ground Truth Discriminator)"}
    
    Verifier -- "SUCCESS" --> Complete([Task Complete])
    Verifier -- "PARTIAL / FAILED" --> Recovery["6. Cyclical Recovery Agent"]
    
    Recovery -- "Safe Retry (Count <= 2)" --> Observer
    Recovery -- "High Risk / Max Retries" --> Escalation["7. Human Escalation"]
    Escalation --> Complete
```

### Agent Nodes Explained:
1. **Task Interpreter (`task_interpreter.py`)**: Converts raw user goals into structured, verifiable outcome specifications with defined side-effect risk ratings (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
2. **Dual-Mode Executor (`browser_agent.py`)**: Drives browser actions via Playwright in headed or headless mode, supporting actions like `navigate`, `fill`, `click`, `scroll`, and `wait`.
3. **State Observer (`state_observer.py`)**: Collects rich post-action telemetry (DOM snapshots, CDP network events, console logs).
4. **Evidence Collector (`evidence_collector.py`)**: Packages multi-modal streams into a structured `EvidencePackage`.
5. **Outcome Verifier (`outcome_verifier.py`)**: Independent discriminator using `openai/gpt-4o-mini` with constrained JSON output and negative-evidence penalties.
6. **Recovery Agent (`recovery_agent.py`)**: Detects modal occlusions and hydration lags, auto-dismissing popups and retrying up to 2 safe iterations.
7. **Human Escalation (`human_escalation.py`)**: Halts execution and notifies human supervisors when high-risk actions fail.

---

## 🧠 Model Routing & LiteLLM Gateway

ActVerge uses a unified LiteLLM configuration (`litellm_config.yaml`) mapped to **OpenRouter**:

| Alias | Model | Purpose | Latency |
| :--- | :--- | :--- | :---: |
| **`actverge/verifier`** | `openai/gpt-4o-mini` | Independent outcome verification & hallucination check | **~1.2s** |
| **`actverge/interpreter`** | `openai/gpt-4o-mini` | Task decomposition & verifiable condition planning | **~1.1s** |
| **`actverge/multimodal`** | `google/gemini-2.0-flash-001` | Vision & visual layout verification | **~1.4s** |
| **`actverge/fallback`** | `openai/gpt-4o-mini` | High-speed cost-efficient fallback | **~0.9s** |

---

## 🚀 Setup & Local Execution

### 1. Prerequisites
- Python 3.12+
- Docker (for PostgreSQL, Redis, MinIO)

### 2. Environment Configuration
Create `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://actverge:actverge@localhost:5432/actverge
REDIS_URL=redis://localhost:6379/0
ARQ_REDIS_URL=redis://localhost:6379/1
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=actverge-artifacts

OPENROUTER_API_KEY=sk-or-v1-your-key-here
PLAYWRIGHT_HEADLESS=false
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### 3. Install & Run
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate      # Linux/macOS: source .venv/bin/activate
pip install -e .
pip install playwright
playwright install chromium

# Start FastAPI API server
uvicorn actverge.api.main:app --reload --port 8000
```

In a second terminal, start the background ARQ worker:
```powershell
cd backend
.\.venv\Scripts\activate
python -m arq actverge.workers.queue.WorkerSettings
```

---

## 📡 API Endpoints

- `POST /api/tasks`: Creates and enqueues a new autonomous execution job.
- `GET /api/tasks/{id}`: Returns task status, timestamps, and metadata.
- `GET /api/tasks/{id}/stream`: Real-time Server-Sent Events (SSE) streaming node state updates.
- `GET /api/tasks/{id}/verdict`: Returns the final verified verdict, reasoning, and confidence.
- `GET /api/tasks/{id}/evidence`: Returns the 6-stream multi-modal evidence package.
- `POST /api/tasks/verify`: **Direct External State Oracle** used by the Chrome Companion Extension.
