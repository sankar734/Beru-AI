# NOVA X — COMPLETE PERSONAL INTELLIGENCE OPERATING SYSTEM
## Master Architectural Blueprint & System Specification
### Version 1.0.0 — Production Specification

---

## 1. COMPLETE ARCHITECTURE OVERVIEW

NOVA X is a unified Personal Intelligence Operating System designed under the core principle:
**"AI intelligence with human control."**

The platform decouples intelligence from execution through a multi-tier security boundary:
1. **Intelligence Tier (Cloud / Host AI Core)**: Generates plans, reasonings, queries, and tool proposals. It never possesses direct OS handles, shell privileges, or unauthenticated hardware access.
2. **Policy & Permission Tier (Gatekeeper Engine)**: Evaluates every tool proposal against strict capability schemas, folder allowlists, user risk preferences, and session tokens. Consequential or destructive actions require explicit user approval.
3. **Execution Tier (Local Companion & Isolated Sandboxes)**: Executes verified actions through system-native APIs, containerized runtimes, or sandboxed browser contexts.
4. **Verification & Audit Tier (Truth Engine)**: Actively inspects the real state of the target system (processes, filesystem, network sockets, DOM, database) post-action. It logs cryptographic audit events and reports true status back to the user.

```
USER
  │
  ▼
NOVA X CLIENTS (Web / Desktop / Mobile)
  │
  ▼ (TLS / JWT / Device Signature)
API GATEWAY (Rate Limiting, Auth, Request Tracing)
  │
  ▼
NOVA ORCHESTRATOR
  ├── Context Planner (History, Project Scope, Relevant Memories)
  ├── Intelligence Router (Intent, Cost/Latency/Privacy, Model Selection)
  └── Response Engine (Streaming, Artifact Dispatch, Tool Coordination)
        │
        ▼
   TOOL PROPOSAL (Structured JSON, Intent, Parameters)
        │
        ▼
  POLICY & PERMISSION ENGINE (Risk Classification 0-4, Scope Checks)
        │
   ┌────┴────────────────────────┬────────────────────────┐
   ▼                             ▼                        ▼
[LEVEL 0-1: Auto Safe]     [LEVEL 2: Safe Local]   [LEVEL 3-4: Consequential]
   │                             │                        │
   │                             │                 User Modal Prompt
   │                             │                 (Allow Once / Deny)
   └─────────────────────────────┼────────────────────────┘
                                 │
                                 ▼
                          TOOL EXECUTORS
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
    Search & RAG           Code Sandbox          Desktop Companion
   (Web, Doc, Vector)     (Isolated Subproc)    (OS, Apps, FS, Windows)
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                                 ▼
                         VERIFICATION ENGINE
        (Process Check, FS Check, Port Check, Hash Check)
                                 │
                                 ▼
                          AUDIT & MEMORY
        (Cryptographic Audit Log, Controlled Memory Store)
                                 │
                                 ▼
                        STREAMED RESULT TO UI
```

---

## 2. ARCHITECTURE DIAGRAM

```mermaid
graph TD
    subgraph Client Layer
        Web[Web Client - React / TS / Vite]
        Desk[Desktop Client - Tauri / React]
        Palette[Ctrl+K Command Palette]
        VoiceIn[Voice STT Stream]
    end

    subgraph Gateway & Security
        Gateway[API Gateway /api/v1]
        Auth[Auth & Session Manager]
        RateLimit[Redis Token Bucket]
        Audit[Audit & Event Logger]
    end

    subgraph Core Orchestration
        Orch[NOVA Orchestrator]
        Router[Intelligence Router]
        Planner[Context & Task Planner]
        MemoryManager[Controlled Memory System]
        ProjectScope[Project Context Engine]
    end

    subgraph Model Providers
        OpenAI[OpenAI Adapter]
        Anthropic[Anthropic Adapter]
        Google[Google AI Adapter]
        LocalLLM[Local / Ollama Adapter]
        MockLLM[Offline / Test Mock Provider]
    end

    subgraph Policy & Safety
        Policy[Policy & Permission Engine]
        RiskMatrix[Risk Classification 0 to 4]
        ConfirmModal[User Confirmation Barrier]
    end

    subgraph Tool & Execution Services
        SearchSvc[Search & Research Workers]
        RAGSvc[File Intelligence & Vector DB]
        CodeSandbox[Isolated Code Runner Sandbox]
        DesktopComp[NOVA Desktop Companion]
    end

    subgraph Desktop Companion (Host OS)
        WinAPI[OS Native APIs / Win32 / UIA]
        AppCtrl[App Launcher & Manager]
        FSFilter[Approved Folder Filesystem]
        DevServer[Dev Process Supervisor]
        ScreenPriv[Privacy-Preserving Screen Capture]
    end

    subgraph Verification & Storage
        Verifier[Verification Engine]
        Mongo[(MongoDB Primary DB)]
        Redis[(Redis Cache & Queue)]
        VectorDB[(Qdrant / Chroma / In-Memory)]
    end

    Web --> Gateway
    Desk --> Gateway
    Palette --> Desk
    VoiceIn --> Gateway

    Gateway --> Auth
    Auth --> RateLimit
    RateLimit --> Orch

    Orch --> Planner
    Planner --> MemoryManager
    Planner --> ProjectScope
    Orch --> Router

    Router --> OpenAI
    Router --> Anthropic
    Router --> Google
    Router --> LocalLLM
    Router --> MockLLM

    Orch --> Policy
    Policy --> RiskMatrix
    RiskMatrix -->|Consequential| ConfirmModal
    RiskMatrix -->|Safe or Approved| SearchSvc
    RiskMatrix -->|Safe or Approved| RAGSvc
    RiskMatrix -->|Safe or Approved| CodeSandbox
    RiskMatrix -->|Safe or Approved| DesktopComp

    DesktopComp --> WinAPI
    DesktopComp --> AppCtrl
    DesktopComp --> FSFilter
    DesktopComp --> DevServer
    DesktopComp --> ScreenPriv

    SearchSvc --> Verifier
    RAGSvc --> Verifier
    CodeSandbox --> Verifier
    DesktopComp --> Verifier

    Verifier --> Audit
    Verifier --> Mongo
    Verifier --> Redis
    Verifier --> VectorDB
    Verifier --> Orch
```

---

## 3. MONOREPO STRUCTURE

```
nova-x/
├── apps/
│   ├── web/                    # React 19 + TypeScript + Vite + Tailwind CSS
│   ├── desktop/                # Desktop shell application (Tauri / Electron wrapper)
│   └── api/                    # FastAPI primary backend application
│
├── services/
│   ├── ai-core/                # Orchestrator, Router, Prompts, Model Adapters
│   ├── research-worker/        # Deep research planning, scraping, citation graph
│   ├── file-worker/            # Ingestion, OCR, chunking, embedding generation
│   ├── code-runner/            # Isolated code execution sandbox with CPU/RAM limits
│   ├── workflow-worker/        # DAG execution engine for automation & recurring triggers
│   └── desktop-companion/      # Local Python daemon for secure host OS operations
│
├── packages/
│   ├── ui/                     # Design system, theme tokens, reusable React components
│   ├── shared-types/           # TypeScript & Pydantic shared schemas & contracts
│   ├── config/                 # System constants, model registries, default policies
│   └── sdk/                    # Client SDK for API & WebSocket streaming
│
├── infrastructure/
│   ├── docker/                 # Container definitions for services
│   ├── nginx/                  # Gateway & reverse proxy configs
│   └── scripts/                # Development setup, db seed, test runner scripts
│
├── docs/                       # Architectural specifications & technical manuals
├── tests/                      # Unit, integration, E2E, and security test suites
├── docker-compose.yml          # Multi-container local deployment
├── .env.example                # Sample environment configurations
├── package.json                # Root monorepo workspace configuration
└── README.md                   # Getting started & operation instructions
```

---

## 4. TECHNOLOGY DECISIONS

| Layer | Selected Tech | Justification |
| :--- | :--- | :--- |
| **Frontend Framework** | React 19 + TypeScript + Vite | Exceptional rendering performance, modern hooks, instant HMR, strong typing. |
| **Styling** | Vanilla CSS Tokens + Tailwind CSS | Rapid layout development with rich custom design system tokens, avoiding generic UI look. |
| **State Management** | Zustand + TanStack Query v5 | Lightweight predictable stores for UI/Chat, robust caching/revalidation for server state. |
| **Code Editor** | Monaco Editor | Industry-standard developer experience with syntax highlighting, diff viewer, and AST support. |
| **Backend Framework** | Python 3.14 + FastAPI | High-concurrency async runtime, automatic OpenAPI generation, native Pydantic v2 validation. |
| **Primary Database** | MongoDB (Motor / PyMongo) | Flexible document schema for conversations, rich artifacts, research trees, and audit logs. |
| **Cache & Real-time** | Redis + fakeredis fallback | Fast session cache, token bucket rate limiting, pub/sub for SSE/WebSocket, reliable background queues. |
| **Task Queue** | Arq (AsyncIO + Redis) | Lightweight, native Python async task queue without Celery's overhead; zero-dependency fallback for dev. |
| **Vector Database** | Qdrant + Chroma + In-Memory Provider | Multi-provider vector abstraction allowing cloud Qdrant or offline zero-dependency in-memory cosine search. |
| **Desktop Companion** | Local Python 3 Service (Loopback) | Direct access to OS APIs (Win32, psutil, pywinauto) over TLS/HMAC authenticated loopback interface. |
| **Browser Automation**| Playwright | Reliable DOM extraction, headless/headed browser control, resilient network interception. |

---

## 5. FRONTEND ARCHITECTURE

1. **Atomic Design System (`packages/ui`)**:
   - Modern, professional dark/light palette with glassmorphism touches (`var(--nova-bg)`, `var(--nova-surface)`, `var(--nova-accent)`).
   - Component primitives: Button, Modal, Drawer, Dropdown, Tabs, Badge, Progress, Toast, Tooltip.
   - Interactive Monaco Editor component with diff support.
2. **State Store Organization (`apps/web/src/stores`)**:
   - `useAuthStore`: User identity, JWT tokens, active permissions.
   - `useChatStore`: Active conversation, branching threads, streaming token buffer, pinned items.
   - `useDesktopStore`: Paired device status, latency, active permissions, audit events, emergency stop.
   - `useStudioStore`: Active artifact (Document, Code, Diagram, Presentation), version history, diff viewer.
   - `useWorkflowStore`: Visual DAG editor nodes, edges, validation state.
3. **Real-time Streaming Engine (`apps/web/src/services/stream.ts`)**:
   - Unified SSE & WebSocket reader supporting chunked text, tool calls, live thought processes, status badges, and cancellation signals.

---

## 6. BACKEND ARCHITECTURE

1. **FastAPI Application Architecture (`apps/api`)**:
   - Multi-router modular layout (`/api/v1/{module}`).
   - Middleware chain:
     1. `RequestTraceMiddleware`: Injects correlation ID `x-request-id` into all logs.
     2. `RateLimitMiddleware`: Redis token bucket per IP/User.
     3. `AuthMiddleware`: Bearer JWT token validation with role-based scopes.
     4. `SecurityHeadersMiddleware`: CSP, HSTS, frame-ancestors, CORS isolation.
2. **Dependency Injection**:
   - Database sessions (`get_db`), current user (`get_current_user`), model provider (`get_model_provider`), desktop gateway (`get_desktop_gateway`).
3. **Graceful Degradation**:
   - Automatic fallback to in-memory vector database and embedded storage when external services are unconfigured.

---

## 7. AI CORE ARCHITECTURE

The AI Core pipeline orchestrates user requests across 7 deterministic stages:
1. **Input Normalization**: Sanitizes input, extracts file attachments, identifies explicit mode overrides.
2. **Context Assembly**: Queries relevant project context, short-term conversational context, and approved user memory.
3. **Planning & Intelligence Routing**: Decomposes complex goals into sequential sub-tasks; chooses the optimal model provider.
4. **Tool Call Formulation**: Restricts tool choices strictly to the allowlisted registry matching current permissions.
5. **Policy Verification Barrier**: Checks risk level; holds execution if Level 3 or 4 until user approval signature is received.
6. **Execution & State Observation**: Runs tools and pipes raw outputs through prompt injection sanitizers.
7. **Synthesis & Response Generation**: Streams structured responses with verified citation references and artifact updates.

---

## 8. PROVIDER ABSTRACTION

Unified interface `ModelProvider`:
```python
class ModelCapability(str, Enum):
    CHAT = "CHAT"
    REASONING = "REASONING"
    VISION = "VISION"
    EMBEDDINGS = "EMBEDDINGS"
    IMAGE = "IMAGE"
    SPEECH_TO_TEXT = "SPEECH_TO_TEXT"
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"
    TOOL_CALLING = "TOOL_CALLING"
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"

class ModelProvider(ABC):
    @abstractmethod
    async def chat_stream(self, messages: list[ChatMessage], tools: list[ToolDefinition] = None) -> AsyncIterator[ChatChunk]: ...
    @abstractmethod
    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]: ...
    @abstractmethod
    async def transcribe_audio(self, audio_bytes: bytes) -> str: ...
    @abstractmethod
    async def synthesize_speech(self, text: str) -> bytes: ...
    @abstractmethod
    def supported_capabilities(self) -> set[ModelCapability]: ...
```

Concrete Adapters:
- `OpenAIProvider`: Supports GPT-4o, o1, o3-mini, text-embedding-3-small, whisper-1, tts-1.
- `AnthropicProvider`: Supports Claude 3.5 Sonnet, Claude 3.7 Sonnet (thinking mode), Claude 3.5 Haiku.
- `GoogleProvider`: Supports Gemini 2.0 Flash, Gemini 1.5 Pro, Imagen 3.
- `LocalProvider`: Connects to Ollama / vLLM OpenAI-compatible endpoints.
- `MockProvider`: Deterministic offline provider for unit tests and local self-contained runs.

---

## 9. INTELLIGENCE ROUTER

Dynamic rule-based and classification router:
- **Query Complexity Score**: Calculates token length, technical keywords, math/logic requirements, tool requirements.
- **Routing Rules**:
  - `CODE` / `ANALYZE` -> High reasoning model with code specialization.
  - `QUICK` / Simple conversational -> Low-latency cost-effective model.
  - `THINK` / Deep multi-step reasoning -> Extended reasoning model.
  - `VISION` -> Vision-enabled model with image understanding.
- **Privacy Constraint**: If user privacy policy specifies `LOCAL_ONLY`, routes strictly to local models or offline mock.

---

## 10. SEARCH ARCHITECTURE

Grounded Search Pipeline:
1. **Query Deconstruction**: Expands user query into 1-3 targeted search queries.
2. **Provider Dispatch**: Interfaces with SearXNG, Tavily, DuckDuckGo, or Bing API.
3. **Result Filtering & Ranking**: Deduplicates URLs, scores domain authority, removes paywalls.
4. **Parallel Scrape & Extraction**: Extracts clean markdown/text content using BeautifulSoup and Readability.
5. **Fact & Citation Verification**: Cross-references claims against source snippets; generates cryptographic citation anchors (`[1]`, `[2]`).

---

## 11. DEEP RESEARCH ARCHITECTURE

Multi-stage Autonomous Research Engine:
1. **Goal Breakdown**: Research Planner produces a research tree with 3-7 subquestions.
2. **Iterative Search Waves**: Dispatches concurrent search workers across web, academic, and technical documentation.
3. **Evidence Graph**: Extracts supporting and contradicting evidence with provenance timestamps.
4. **Contradiction Resolution**: Synthesizer identifies discrepancies and schedules targeted follow-up queries.
5. **Comprehensive Synthesis**: Compiles an exhaustive, cited report with executive summary, methodology, evidence tables, and verified bibliography.

---

## 12. RAG (RETRIEVAL-AUGMENTED GENERATION) ARCHITECTURE

1. **Document Ingestion**:
   - Format parsers: PDF (PyMuPDF), DOCX (python-docx), XLSX/CSV (pandas), TXT/MD/JSON (native).
   - Structural cleaning: Strips headers/footers, preserves table structures as Markdown tables.
2. **Semantic Chunking**:
   - Sliding window chunking (500 tokens, 100 token overlap) with section header preservation.
3. **Hybrid Retrieval**:
   - Dense vector retrieval (Cosine similarity) + Sparse lexical retrieval (BM25).
   - Reciprocal Rank Fusion (RRF) combines scores.
4. **Reranking**:
   - Cross-encoder reranks top 20 candidates down to top 5 grounded chunks.
5. **Citation Anchoring**:
   - Every chunk injected into context carries `file_id`, `file_name`, `page_number`, `chunk_index`.

---

## 13. PROJECT ARCHITECTURE

Projects act as isolated contextual workspaces:
- Fields: `id`, `name`, `description`, `system_instructions`, `custom_rules`, `files`, `artifacts`, `tasks`.
- Scoped Retrieval: Search & RAG queries within a project automatically filter retrieval vectors by `project_id`.
- Context Budgeting: Projects enforce a token budget for persistent instructions, preventing context window bloat.

---

## 14. MEMORY ARCHITECTURE

Controlled Multi-Tier Memory System:
1. **Memory Types**:
   - `PREFERENCE`: Coding styles, preferred frameworks, communication tones.
   - `FACT`: Stable personal or organization information.
   - `WORKFLOW`: Repeated procedural routines.
2. **Storage**: Stored in `memories` collection with semantic vector embeddings.
3. **Privacy Controls**:
   - User can inspect every memory, edit text, toggle active/disabled, delete individual entries, or wipe all memories.
   - "Incognito / Ephemeral Chat" mode completely bypasses memory storage and retrieval.

---

## 15. KNOWLEDGE GRAPH DESIGN

Entity-Relation Graph for complex projects:
- **Entities**: `Project`, `File`, `Concept`, `Technology`, `Artifact`, `Task`.
- **Relations**: `USES`, `DEPENDS_ON`, `REFERENCES`, `CONTAINS`, `RELATED_TO`, `CREATED_FROM`.
- Graph traversal enables answering architectural questions such as "Which files depend on the Auth module?" or "Which tasks relate to the Database migration?"

---

## 16. STUDIO ARCHITECTURE

Interactive Artifact Workspace:
- Artifact Types: `DOCUMENT`, `REPORT`, `CODE`, `WEB_APP`, `DIAGRAM`, `CHART`, `SPREADSHEET`, `PRESENTATION`, `IMAGE`.
- Split Layout: Left side chat conversation; Right side real-time live preview/editor.
- Version History: Immutable snapshots for every edit with visual side-by-side diffing and 1-click rollback.

---

## 17. CODE SANDBOX ARCHITECTURE

Safe Code Execution Sandbox:
- Execution occurs in dedicated runner process with strict OS resource constraints:
  - Max CPU time: 5.0 seconds.
  - Max RAM: 256 MB.
  - Max output buffer: 64 KB.
  - Network access: Completely disabled / blocked loopback.
  - Filesystem: Isolated temporary directory, wiped upon process termination.
- Environment variables containing host secrets (API keys, DB URLs) are strictly stripped from execution environment.

---

## 18. LEARNING ARCHITECTURE

Personalized Learning Operating System:
- **Study Plan Generator**: Parses syllabus/textbooks into structured curriculum milestones.
- **Socratic AI Tutor**: Interactively tests understanding through guided questioning rather than giving answers.
- **Interactive Quiz Engine**: Evaluates MCQ, True/False, and Coding challenges with automated grading and mastery tracking.
- **Aptitude Bank**: Quantitative, Logical, and Verbal reasoning tests with timed sessions and detailed solution steps.

---

## 19. TOOL ARCHITECTURE & REGISTRY

Strict schema-driven Tool System:
```python
class ToolRisk(str, Enum):
    LEVEL_0 = "INFORMATIONAL"    # Safe read of public information (time, search)
    LEVEL_1 = "SAFE_READ"        # Read user data within approved boundaries
    LEVEL_2 = "REVERSIBLE_WRITE" # Create/edit local file with automatic backup
    LEVEL_3 = "CONSEQUENTIAL"    # Network calls, external mutations, dev server operations
    LEVEL_4 = "PRIVILEGED"       # Deletions, shell commands, settings changes

@dataclass
class ToolDefinition:
    id: str
    name: str
    description: str
    parameters_schema: dict
    risk_level: ToolRisk
    required_scope: str
    handler: Callable
```

---

## 20. AGENT ARCHITECTURE

Autonomous Goal Execution Loop:
1. **Goal Specification**: User defines high-level objective (e.g. "Audit security vulnerabilities in `src/auth`").
2. **Plan Synthesis**: Decomposes objective into an ordered list of verifiable steps.
3. **Step Execution**:
   - Selects tool and constructs proposal.
   - Evaluates risk against policy.
   - Prompts user confirmation if risk >= Level 3.
   - Executes tool, verifies output, updates state.
4. **Safety Boundaries**: Hard limits on maximum steps (default 15), maximum runtime (300s), and cancellation token monitoring.

---

## 21. WORKFLOW ARCHITECTURE

Visual Directed Acyclic Graph (DAG) Engine:
- **Node Types**: `TriggerNode`, `AINode`, `SearchNode`, `CodeNode`, `ConditionNode`, `NotificationNode`, `DesktopActionNode`.
- **Execution Engine**: Topological sort with concurrent branch execution and state accumulation.

---

## 22. AUTOPILOT ARCHITECTURE

Flagship Long-Horizon Guidance System:
- Coordinates multi-week or multi-month goals (e.g. "Prepare for Senior Python Developer Interviews").
- Deconstructs goals into weekly milestones and daily 15-minute action sessions.
- Automatically adjusts pacing based on quiz scores and project completion metrics.

---

## 23. DESKTOP ARCHITECTURE

Hybrid Desktop Architecture:
- Desktop UI (Tauri / Web) communicates with central API for AI orchestration.
- Central API dispatches signed action proposals to the **NOVA Desktop Companion** running locally on the user's host machine.
- All desktop communications happen over authenticated loopback or encrypted WebSockets using asymmetric HMAC signatures.

---

## 24. DESKTOP COMPANION ARCHITECTURE

Local Host Service (`services/desktop-companion`):
- Runs with standard user privileges (never elevated administrator).
- Binds strictly to `127.0.0.1` with a unique session authentication token generated on startup.
- Manages host OS capabilities: Window enumeration, application launching, approved filesystem operations, developer processes.

---

## 25. DESKTOP PERMISSION ARCHITECTURE

Zero-Trust Desktop Control:
- Default posture: Everything is `DENIED` or `ASK`.
- Specific Directory Whitelisting: Only explicitly granted directories (e.g., `D:\Projects\MyProject`) can be read or modified.
- High-risk actions (`DELETE_FILE`, `CLOSE_APP`, `KILL_PROCESS`) always trigger a frontend confirmation modal.

---

## 26. SYSTEM-CONTROL ARCHITECTURE

Deterministic OS Automation:
- Primary mechanism: Standard OS APIs (Win32 API via `ctypes` / `pywin32`, `psutil`, URL protocols).
- Deep Links: Launches system settings via Windows URI schemes (e.g. `ms-settings:bluetooth`, `ms-settings:display`).
- Volume & Media: Controlled through Windows Core Audio APIs without screen clicking.

---

## 27. SCREEN-INTELLIGENCE ARCHITECTURE

Privacy-Preserving Screen Understanding:
- Capture is strictly on-demand (no background surveillance or periodic scraping).
- User chooses scope: `Active Window Only` or `Entire Screen`.
- Client-side redaction heuristics blur detected password input fields and sensitive regex patterns before transmission.

---

## 28. BROWSER-AGENT ARCHITECTURE

Safe Web Automation via Playwright:
- Operates in dedicated clean browser profiles.
- URL Allowlisting: Restricts navigation away from untrusted or malicious origins.
- Security Rule: Browser agent NEVER interacts with password inputs or stores authentication credentials.

---

## 29. DEVELOPER-AGENT ARCHITECTURE

Intelligent Local Development Supervisor:
- Project Inspection: Auto-detects frameworks (Vite, Next.js, FastAPI, Django, Cargo).
- Safe Command Runner: Resolves dev commands strictly from `package.json` / `pyproject.toml` scripts.
- Log Streaming: Monitors stdout/stderr, detects build errors, and highlights exact stack traces.
- Automated Repair: Generates unified diffs, creates automated backup checkpoints, applies changes upon approval, and verifies server restart.

---

## 30. VOICE-CONTROL ARCHITECTURE

Full-Duplex Voice Interaction:
1. Microphone Audio Stream -> WebSocket chunking.
2. Fast STT (Whisper API / local Whisper).
3. Intent Classifier -> Identifies desktop commands vs conversational questions.
4. Execution & Verification.
5. Voice Response Synthesis (TTS) streamed back to client audio buffer.

---

## 31. MONGODB SCHEMAS

30+ Production Collections:
- Core: `users`, `sessions`, `conversations`, `messages`, `attachments`.
- Projects: `projects`, `project_members`, `project_context`.
- Files & RAG: `files`, `file_chunks`, `embeddings_meta`.
- Artifacts: `artifacts`, `artifact_versions`.
- Memory & Graph: `memories`, `knowledge_entities`, `knowledge_relations`.
- Research: `research_jobs`, `research_sources`, `research_evidence`.
- Tools & Safety: `tool_registry`, `tool_runs`, `audit_logs`.
- Agents & Workflows: `agents`, `agent_runs`, `workflows`, `workflow_runs`.
- Productivity: `tasks`, `reminders`, `goals`.
- Learning: `learning_profiles`, `courses`, `quizzes`, `quiz_attempts`.
- Desktop: `desktop_devices`, `desktop_permissions`, `desktop_actions`.

---

## 32. REDIS DESIGN

- Key Namespaces:
  - `session:{token}` -> User session metadata (TTL 24h).
  - `ratelimit:{ip/user}:{endpoint}` -> Sliding window counter.
  - `desktop:status:{device_id}` -> Heartbeat (TTL 30s).
  - `stream:{channel_id}` -> Pub/Sub for real-time SSE/WebSocket fan-out.
  - `queue:tasks` -> Background task dispatch.

---

## 33. VECTOR DB DESIGN

- Collections: `nova_rag_chunks`, `nova_memories`, `nova_research_evidence`.
- Vectors: 1536-dim (OpenAI) or 768-dim (Local/Gemini) normalized cosine embeddings.
- Filter Payload:
  - `user_id`: UUID
  - `project_id`: UUID (optional)
  - `file_id`: UUID (optional)
  - `source_type`: 'file' | 'web' | 'memory'

---

## 34. API MAP (REST `/api/v1`)

- `/auth`: `login`, `register`, `me`, `refresh`, `logout`.
- `/chat`: `conversations`, `messages`, `stream`, `branch`, `regenerate`.
- `/search`: `query`, `sources`.
- `/research`: `jobs`, `jobs/{id}`, `jobs/{id}/cancel`.
- `/files`: `upload`, `list`, `delete`, `{id}/chunks`.
- `/projects`: CRUD, context injection, instructions.
- `/artifacts`: CRUD, versions, diff, export.
- `/desktop`: `connect`, `capabilities`, `permissions`, `apps`, `files`, `screen`, `actions`, `actions/{id}/approve`.
- `/developer`: `detect`, `run`, `stop`, `logs`, `repair`.
- `/agents`: `create`, `run`, `status`, `cancel`.
- `/workflows`: CRUD, execute, trigger.
- `/learning`: `courses`, `quizzes`, `submit`, `mastery`.
- `/tasks`: CRUD, status update, priority.

---

## 35. WEBSOCKET & SSE DESIGN

- Endpoints:
  - `/api/v1/chat/stream`: Server-Sent Events (SSE) for conversational tokens and tool progress.
  - `/api/v1/desktop/ws`: Bidirectional authenticated WebSocket for host companion communication.
  - `/api/v1/developer/logs/stream`: WebSocket for live dev server log streaming.

---

## 36. SECURITY THREAT MODEL

- **Prompt Injection Defense**: All retrieved external documents, web scrapes, and terminal outputs are treated as raw data within isolated XML tags (`<untrusted_content>`). The LLM is structurally instructed never to execute instructions inside untrusted tags.
- **Confused Deputy Defense**: Tool authorization depends solely on authenticated user identity and explicit confirmation, never on LLM assertion.
- **Path Traversal Defense**: All file paths are strictly resolved against canonical whitelisted roots using `os.path.realpath` checks.
- **Secret Redaction**: Regex filter masks API keys (`sk-...`, `ghp-...`, JWTs) from terminal logs and UI outputs.

---

## 37. PERMISSION & RISK MATRIX

| Tool / Action | Risk Level | User Confirmation Required | Allowable Folders / Scope |
| :--- | :--- | :--- | :--- |
| `search_web` | Level 0 | No | Public Internet |
| `read_file` | Level 1 | No (if within allowed folder) | Whitelisted Project Folders |
| `create_file` | Level 2 | No (creates version backup) | Whitelisted Project Folders |
| `open_app` | Level 2 | No (if on allowed app list) | Allowed Apps (e.g. VS Code, Chrome) |
| `start_dev_server` | Level 3 | Yes | Whitelisted Project Directory |
| `run_code_sandbox` | Level 3 | No (isolated container) | Temp Sandbox Only |
| `delete_file` | Level 4 | Always (Explicit Prompt) | Recycle Bin fallback |
| `kill_process` | Level 4 | Always (Explicit Prompt) | User Owned Processes Only |

---

## 38. DOCKER ARCHITECTURE

Multi-container setup in `docker-compose.yml`:
- `nova-web`: Nginx serving built Vite React bundle.
- `nova-api`: Uvicorn running FastAPI backend.
- `nova-mongodb`: MongoDB 7.0 database.
- `nova-redis`: Redis 7.2 alpine cache.
- `nova-research-worker`: Python worker for deep web scraping.
- `nova-code-runner`: Isolated container with resource limits for sandbox execution.

---

## 39. TESTING STRATEGY

1. **Unit Tests (`tests/unit`)**:
   - Model Provider mocks, Intelligence Router classification, Token calculation, Policy Engine risk evaluation, Safe path validation.
2. **Integration Tests (`tests/integration`)**:
   - Auth lifecycle, Chat streaming, RAG chunking and retrieval, Desktop action approval pipeline.
3. **Security Test Suite (`tests/security`)**:
   - Prompt injection resistance, Path traversal attempts (`../../windows/system32`), Secret redaction from stdout, Unapproved folder blocking.
4. **End-to-End Tests (`tests/e2e`)**:
   - Full flow testing from web UI to backend API to desktop companion verification.

---

## 40. FULL IMPLEMENTATION ROADMAP & STATUS (100% COMPLETE)

All 28 master phases of the NOVA X Personal Intelligence Operating System are completely implemented, integrated, and verified:

- [x] **Phase 0**: Monorepo scaffolding, FastAPI gateway, tracing, resilient DB & cache, React 19/Vite 6 client (`tests/test_phase0.py`).
- [x] **Phase 1**: Authentication, JWT token lifecycle, bcrypt, Zustand store, full application UI shell (`tests/test_phase1.py`).
- [x] **Phase 2**: Universal Chat with SSE streaming, conversation branching, pinning, composer, reasoning chain (`tests/test_phase2.py`).
- [x] **Phase 3**: Multi-provider adapters (Mock, OpenAI, Anthropic, Gemini, Ollama) and Intelligence Router (`tests/test_phase3.py`).
- [x] **Phase 4**: Grounded AI Search with SearXNG, NLI citation verifier, and interactive UI (`tests/test_phase4.py`).
- [x] **Phase 5**: File Intelligence and Hybrid RAG (Dense embeddings + Lexical BM25 with Reciprocal Rank Fusion) (`tests/test_phase5.py`).
- [x] **Phase 6**: Deep Research System with subquestion decomposition and skeptic contradiction analysis (`tests/test_phase6.py`).
- [x] **Phase 7**: Projects and Controlled Memory with fact extraction and user memory management (`tests/test_phase7.py`).
- [x] **Phase 8**: Vision and Voice subsystems (OCR, credential masking, STT, TTS audio synthesis) (`tests/test_phase8.py`).
- [x] **Phase 9**: Code Workspace and Isolated Execution Sandbox with secret redaction (`tests/test_phase9.py`).
- [x] **Phase 10**: NOVA Studio and Artifact Workspace (DOCUMENT, REPORT, CODE, WEB_APP, DIAGRAM) (`tests/test_phase10.py`).
- [x] **Phase 11**: Learning OS (Adaptive study plans, diagnostic quizzes, Socratic coaching, spaced repetition flashcards) (`tests/test_phase11.py`).
- [x] **Phase 12**: Custom AI Experts (Systems Architect, Security Auditor, Performance Engineer, AI/ML Scientist) (`tests/test_phase12.py`).
- [x] **Phase 13**: Tool Registry and Zero-Trust Policy Barrier (Risk Levels 0-4, human authorization tokens) (`tests/test_phase13.py`).
- [x] **Phase 14**: Autonomous Agent System (`Goal -> Plan -> Risk -> Tools -> Observe -> Verify`) (`tests/test_phase14.py`).
- [x] **Phase 15**: Visual Workflow Automation Engine with DAG node pipelines (`tests/test_phase15.py`).
- [x] **Phase 16**: Tasks, Reminders, and Goals with Kanban backlog and agent delegation (`tests/test_phase16.py`).
- [x] **Phase 17**: NOVA Autopilot & Proactive Intelligence with telemetry monitors and 1-click execution (`tests/test_phase17.py`).
- [x] **Phase 18**: Desktop Companion Foundation (Hardware vitals, processes, whitelisted app launcher) (`tests/test_phase18.py`).
- [x] **Phase 19**: Desktop Window Automation (Win32 window enumeration, focus foreground, text injection) (`tests/test_phase19.py`).
- [x] **Phase 20**: Desktop File Intelligence (Path traversal protection, allowed roots, local search) (`tests/test_phase20.py`).
- [x] **Phase 21**: Screen Intelligence and Visual Understanding (Screen capture, credential masking, visual error analysis) (`tests/test_phase21.py`).
- [x] **Phase 22**: Browser Automation and Web Agent with SSRF protection and DOM parsing (`tests/test_phase22.py`).
- [x] **Phase 23**: Developer Agent & Process Supervisor (Process manager, multi-file AST diffs, auto-diagnostics) (`tests/test_phase23.py`).
- [x] **Phase 24**: Voice Desktop Control & Speech-to-Action with audio synthesis and confirmation barrier (`tests/test_phase24.py`).
- [x] **Phase 25**: Connected Apps & MCP Protocol (Model Context Protocol JSON-RPC servers, dynamic discovery) (`tests/test_phase25.py`).
- [x] **Phase 26**: Security Hardening & Zero-Trust Audit Subsystem (Security headers, rate limiting, SHA-256 ledger) (`tests/test_phase26.py`).
- [x] **Phase 27**: Observability & Telemetry Subsystem with Prometheus exporter and latency percentiles (`tests/test_phase27.py`).
- [x] **Phase 28**: Production Deployment & Verification (Docker Compose, Nginx reverse proxy, 88/88 test pass) (`tests/test_phase28.py`).

**Cumulative Verification Status**: 88/88 Pytest Suites Passing • 100% Production Web Bundle Build Success.

