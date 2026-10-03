# NOVA X — Personal Intelligence Operating System
> **Think. Search. Research. Create. Code. Learn. Act.**

NOVA X is a unified, production-oriented Personal Intelligence Operating System that combines conversational AI, autonomous research, hybrid RAG file intelligence, multi-modal studio artifacts, safe code execution, and privacy-first local desktop automation with human-in-the-loop control.

---

## Key Differentiators
1. **Human-in-the-loop Policy Engine**: Consequential and destructive actions (Levels 3 & 4) strictly require user confirmation before execution.
2. **True Verification Engine**: Never trusts prompt output alone. Verifies actual OS processes, files, ports, and DOM states post-action.
3. **Desktop Companion Security Boundary**: Operates as a separate authenticated loopback daemon; no direct unauthenticated shell access for the cloud AI.
4. **Resilient Provider Abstraction**: Supports OpenAI, Anthropic, Google Gemini, local models (Ollama/vLLM), and offline mock testing without vendor lock-in.

---

## Monorepo Layout
```
nova-x/
├── apps/
│   ├── web/                    # React 19 + TypeScript + Vite + Tailwind CSS
│   ├── desktop/                # Desktop shell application (Tauri / Electron wrapper)
│   └── api/                    # FastAPI primary backend application
├── services/
│   ├── ai-core/                # Orchestrator, Router, Prompts, Model Adapters
│   ├── research-worker/        # Deep research planning, scraping, citation graph
│   ├── file-worker/            # Ingestion, OCR, chunking, embedding generation
│   ├── code-runner/            # Isolated code execution sandbox with CPU/RAM limits
│   ├── workflow-worker/        # DAG execution engine for automation & recurring triggers
│   └── desktop-companion/      # Local Python daemon for secure host OS operations
├── packages/
│   ├── ui/                     # Design system, theme tokens, reusable React components
│   ├── shared-types/           # TypeScript & Pydantic shared schemas & contracts
│   ├── config/                 # System constants, model registries, default policies
│   └── sdk/                    # Client SDK for API & WebSocket streaming
├── docs/                       # Architecture, manuals, security specs
└── tests/                      # Unit, integration, E2E, and security test suites
```

---

## Quickstart Guide

### 1. Prerequisites
- Node.js >= 20 (v24 recommended)
- Python >= 3.11 (3.14 supported)
- MongoDB & Redis (or automated in-memory development fallback)

### 2. Setup Environment
```bash
cp .env.example .env
npm install
```

### 3. Start Backend Services
```bash
# In one terminal
python -m pip install -r apps/api/requirements.txt
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload
```

### 4. Start Web Application
```bash
npm run dev --workspace=apps/web
```

### 5. Start Desktop Companion (Optional Host Integration)
```bash
python services/desktop-companion/main.py
```
