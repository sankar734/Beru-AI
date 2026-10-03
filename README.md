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

### 5. Run Full Architectural Test Suite (All 28 Phases)
```bash
python -m pytest tests/
```

### 6. Production Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

---

## Master Architecture & Phase Status (28 / 28 Completed)

| Phase | Subsystem | Status | Verification Suite |
| :--- | :--- | :--- | :--- |
| **0** | Monorepo, FastAPI Gateway, Tracing, DB & Cache | ✅ Done | `tests/test_phase0.py` |
| **1** | JWT Auth, Security Models, Zustand, UI Shell | ✅ Done | `tests/test_phase1.py` |
| **2** | Universal Chat, SSE Streaming, Message Branching | ✅ Done | `tests/test_phase2.py` |
| **3** | Multi-Provider Adapters & Intelligence Router | ✅ Done | `tests/test_phase3.py` |
| **4** | Grounded AI Search & NLI Citation Verification | ✅ Done | `tests/test_phase4.py` |
| **5** | File Intelligence & Hybrid Dense/BM25 RAG | ✅ Done | `tests/test_phase5.py` |
| **6** | Deep Research Engine & Contradiction Analysis | ✅ Done | `tests/test_phase6.py` |
| **7** | Projects Workspace & Controlled Memory | ✅ Done | `tests/test_phase7.py` |
| **8** | Multimodal Vision OCR & Voice Subsystems | ✅ Done | `tests/test_phase8.py` |
| **9** | Sandboxed Code Execution & Workspace Workbench | ✅ Done | `tests/test_phase9.py` |
| **10** | NOVA Studio & Versioned Artifact System | ✅ Done | `tests/test_phase10.py` |
| **11** | Learning OS, Diagnostics Quizzes & Spaced Repetition | ✅ Done | `tests/test_phase11.py` |
| **12** | Custom AI Domain Experts & Advisory Consultations | ✅ Done | `tests/test_phase12.py` |
| **13** | Tool Registry & Zero-Trust Policy Barrier (Levels 0-4) | ✅ Done | `tests/test_phase13.py` |
| **14** | Autonomous Multi-Step Agent Execution Loop | ✅ Done | `tests/test_phase14.py` |
| **15** | Visual Workflow Automation DAG Engine | ✅ Done | `tests/test_phase15.py` |
| **16** | Strategic Goals & Prioritized Task Management | ✅ Done | `tests/test_phase16.py` |
| **17** | NOVA Autopilot & Proactive Intelligence Monitors | ✅ Done | `tests/test_phase17.py` |
| **18** | Desktop Companion Daemon & Hardware Vitals | ✅ Done | `tests/test_phase18.py` |
| **19** | Desktop Window Automation & Foreground Focus | ✅ Done | `tests/test_phase19.py` |
| **20** | Desktop Local File Intelligence & Allowed Roots | ✅ Done | `tests/test_phase20.py` |
| **21** | Screen Intelligence & Visual Error Diagnostics | ✅ Done | `tests/test_phase21.py` |
| **22** | Browser Automation & Web Agent with SSRF Guard | ✅ Done | `tests/test_phase22.py` |
| **23** | Developer Agent & Service Supervisor | ✅ Done | `tests/test_phase23.py` |
| **24** | Voice Desktop Control & Speech-to-Action | ✅ Done | `tests/test_phase24.py` |
| **25** | Connected Apps & Model Context Protocol (MCP) | ✅ Done | `tests/test_phase25.py` |
| **26** | Security Hardening & Cryptographic Audit Ledger | ✅ Done | `tests/test_phase26.py` |
| **27** | Observability, Prometheus Metrics & Telemetry | ✅ Done | `tests/test_phase27.py` |
| **28** | Production Deployment & End-to-End System Verification | ✅ Done | `tests/test_phase28.py` |

