# Secture Cortex

> AI copilot for client meetings — real-time transcription meets project context.

**"El copiloto que escucha, cruza y responde. Porque 'dejame mirarlo' ya no es opcion."**

Secture Cortex captures audio from video calls, transcribes in real-time with speaker identification, and crosses the conversation with your project's technical context to generate live insights: technical alerts, scope classification, and contextual suggestions.

Unlike Fireflies, Otter, or Granola (post-meeting summarizers), Cortex provides intelligence **during** the meeting — in real-time.

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/RomeroSecture/secture-cortex.git && cd secture-cortex
cp .env.example .env
# Edit .env with your API keys (Deepgram, Groq, Jina)

# 2. Start everything
docker compose up

# 3. Open
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

## Stack

| Layer | Technology | Cost |
|---|---|---|
| Backend | FastAPI (Python 3.12) — async end-to-end | $0 |
| Frontend | Next.js 16 + React 19 + shadcn/ui + Tailwind CSS v4 | $0 |
| Database | PostgreSQL 16 + pgvector (HNSW, 1024 dims) | $0 |
| ORM | SQLAlchemy 2.0+ async (asyncpg) + Alembic migrations | $0 |
| Transcription | Deepgram Nova-3 Multilingual (WebSocket, diarization) | $0 (free credits) |
| LLM | Groq — Qwen3 32B primary, Llama 3.1 8B fallback | $0 (free tier) |
| Embeddings | Jina v3 — 1024 dims (OpenAI-compatible) | $0 (1M tokens/month) |
| Multi-Agent | LangGraph StateGraph (supervisor + 4 specialist agents) | $0 |
| Real-time | WebSocket (raw async, JWT auth) | $0 |
| Deploy | Docker Compose (3 services) | $0 |
| CI | GitHub Actions (ruff + pytest + eslint + vitest) | $0 |

**Total infrastructure cost: $0** (all APIs have free tiers)

## Architecture

```
Browser (getUserMedia + getDisplayMedia)
  | Raw PCM linear16 @ 48kHz via WebSocket
  v
FastAPI Backend
  | Forward to Deepgram Nova-3 (async WebSocket)
  v
Deepgram — Transcription + speaker diarization
  | Buffer ~30s / >50 words
  v
Jina v3 — Embed transcription (1024 dims)
  | pgvector cosine search top-5 context chunks
  v
Groq Qwen3 32B — Generate insight JSON
  | Validate with Pydantic + store in PostgreSQL
  v
WebSocket broadcast → Dashboard updates in real-time
```

### Multi-Agent Pipeline (LangGraph)

```
Transcription buffer
  |
  v
Supervisor Agent — Topic classification + routing
  |
  +---> Tech Lead Agent (technical conflicts, architecture)
  +---> PM Agent (scope, timeline, dependencies)
  +---> Developer Agent (implementation, code references)
  +---> Commercial Agent (pricing, SLA impact)
  +---> Conversation Intel (decisions, action items, questions)
  |
  v
Synthesizer — Conflict resolution + role-aware delivery
  |
  v
Filtered insights per user role + confidence threshold
```

## Features

### Core

- **Real-time transcription** — Deepgram Nova-3, speaker diarization, multilingual (Spanish primary)
- **RAG copilot** — crosses transcription with project context via pgvector + Groq LLM
- **3 insight types** — alerts (technical conflicts), scope (in/out classification), suggestions
- **Multi-agent pipeline** — LangGraph with supervisor routing to 4 specialist agents
- **Role-aware delivery** — filters insights by user role + configurable confidence thresholds
- **Live dashboard** — 2-panel: transcription chat + AI insights, color-coded by type
- **Audio capture** — mic (getUserMedia) + tab audio (getDisplayMedia), raw PCM linear16
- **Cumulative memory** — each meeting enriches pgvector for future meetings
- **Conversation intelligence** — automatic detection of decisions, action items, open questions
- **Post-meeting synthesis** — summaries, minutes, handoff documents
- **User feedback** — useful/not_useful/dismissed per insight

### Management

- **Project CRUD** — create, edit, delete with confirmation
- **Context files** — upload (txt/md/json/csv/pdf/docx), auto-index, delete, re-index, status tracking
- **Meeting management** — start, end, list, review past meetings with full transcription + insights
- **Meeting analytics** — KPIs (insights, decisions, actions), conversation events
- **Project analytics** — KB health scoring, freshness tracking, coverage reports
- **Member management** — assign users to projects with roles
- **RBAC** — 5 roles (admin, tech_lead, developer, pm, commercial), project-level isolation
- **Admin panel** — list all users (admin only)

### Security (OWASP Top 10)

- JWT with expiration + mandatory secret (no insecure default)
- WebSocket JWT authentication via query param
- CORS whitelist (never `*`)
- Pydantic validation on all endpoints
- SQLAlchemy ORM (never raw SQL)
- Custom exception handler (never stacktraces to client)
- Project-level data isolation (all queries filtered by `project_id`)
- File upload validation (type + size, max 10MB)
- Password hashing with bcrypt

## Project Structure

```
secture-cortex/
├── docker-compose.yml              # 3 services: db, backend, frontend
├── .env.example                    # All environment variables
├── .github/workflows/ci.yml        # GitHub Actions CI
├── frontend/                       # Next.js 16 + React 19 + shadcn/ui
│   └── src/
│       ├── app/                    # 13 routes (App Router)
│       │   ├── login/              # Auth (login + register)
│       │   ├── projects/           # List, create, detail, context, meetings
│       │   ├── meeting/[id]/       # Live dashboard
│       │   ├── profile/            # User profile
│       │   └── admin/              # Admin panel
│       ├── components/             # 28 components (feature + shadcn/ui)
│       ├── hooks/                  # useWebSocket, useAudio
│       ├── lib/                    # API client, auth, utils
│       └── types/                  # TypeScript interfaces
├── backend/                        # FastAPI (Python 3.12) async
│   └── app/
│       ├── main.py                 # App entrypoint + middleware
│       ├── config.py               # Pydantic Settings (19 env vars)
│       ├── api/v1/                 # 9 routers, 25 REST endpoints
│       ├── ws/                     # WebSocket handler (transcription + insights)
│       ├── models/                 # 12 SQLAlchemy models + pgvector
│       ├── schemas/                # 9 Pydantic v2 schemas
│       ├── services/               # 17 service modules
│       │   ├── deepgram.py         # Real-time transcription client
│       │   ├── rag.py              # RAG pipeline (buffer + search + LLM)
│       │   ├── llm.py              # Groq LLM client
│       │   ├── embeddings.py       # Jina v3 embeddings
│       │   ├── agent_pipeline.py   # LangGraph multi-agent orchestration
│       │   ├── agents/             # 7 specialist agents
│       │   └── agent_tools/        # Tool implementations
│       ├── repositories/           # 4 data access modules
│       └── core/                   # Security (JWT, bcrypt), structured logging
├── db/
│   └── init.sql                    # CREATE EXTENSION vector + uuid-ossp
├── video/                          # Remotion demo video project
├── docs/
│   ├── roadmap.md                  # Phase 1-4 plans
│   └── demo/                       # Demo scripts + sample context files (PDF + MD)
└── _bmad-output/                   # BMAD-S methodology artifacts
    ├── planning-artifacts/         # PRD (48 FRs), architecture, epics (22 stories)
    └── execution-log.yaml          # Full execution history
```

## API Endpoints (25+)

| Area | Endpoints |
|---|---|
| Auth | `POST /register`, `POST /login`, `GET /me`, `PATCH /me`, `GET /users` |
| Projects | `POST /`, `GET /`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}` |
| Members | `POST /members`, `GET /members` |
| Context Files | `POST /context-files` (upload), `GET /`, `DELETE /{id}`, `POST /{id}/reindex` |
| Meetings | `POST /meetings`, `POST /{id}/end`, `GET /`, `GET /{id}`, `GET /{id}/full`, `PATCH /{id}` |
| Insights | `GET /insights`, `POST /{id}/feedback` |
| Analytics | `GET /analytics`, `GET /meetings/{id}/analytics/kpis`, `GET /meetings/{id}/outputs`, `GET /meetings/{id}/events` |
| WebSocket | `WS /ws/meeting/{id}` (audio + transcription + insights) |
| Health | `GET /health` |

## Data Models (12 tables)

| Model | Purpose |
|---|---|
| `users` | Account (email, name, hashed_password, role enum) |
| `projects` | Client project (name, description) |
| `project_users` | Membership with RBAC role |
| `meetings` | Session (project_id, status, timestamps) |
| `transcriptions` | Segments (speaker, text, is_final) |
| `context_files` | Uploaded files (filename, size, status enum, raw_content) |
| `context_chunks` | Vector chunks (content, embedding pgvector 1024d, HNSW index) |
| `insights` | AI insights (type, content, confidence, sources, agent_source, target_roles) |
| `insight_feedback` | User ratings (useful/not_useful/dismissed) |
| `meeting_outputs` | Post-meeting artifacts (summaries, minutes, handoffs) |
| `conversation_events` | Detected patterns (decisions, action items, questions) |
| `agent_configs` | Per-project agent settings (prompts, thresholds, tools) |

## Environment Variables

See [`.env.example`](.env.example) for all variables. Key ones:

| Variable | Required | Description |
|---|---|---|
| `DEEPGRAM_API_KEY` | Yes | Real-time transcription |
| `LLM_API_KEY` | Yes | Groq API key |
| `LLM_MODEL` | No | Default: `qwen/qwen3-32b` |
| `LLM_FALLBACK_MODEL` | No | Default: `llama-3.1-8b-instant` |
| `EMBEDDINGS_API_KEY` | Yes | Jina v3 embeddings |
| `JWT_SECRET` | Yes | JWT signing key (no default) |
| `AGENT_PIPELINE_ENABLED` | No | Default: `true` — multi-agent pipeline |
| `CONFIDENCE_*` | No | Per-role confidence thresholds |

## Development

### Prerequisites

- Docker & Docker Compose
- Node 22 (frontend local dev)
- Python 3.12 (backend local dev)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
ruff check app/ tests/       # Lint
pytest tests/ -v             # 45+ tests
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev                  # Dev server at :3000
npm test                     # 14+ vitest tests
npm run lint                 # ESLint
npm run build                # Production build + type check
```

### Docker (full stack)

```bash
docker compose up            # All 3 services
docker compose up -d         # Detached
docker compose logs -f       # Follow logs
```

## Performance Targets

| Metric | Target |
|---|---|
| Transcription latency | < 2s (Deepgram Nova-3) |
| Insight generation | < 10s (embed + search + LLM) |
| Vector search | < 500ms (pgvector HNSW, 50k chunks) |
| WebSocket broadcast | < 100ms |
| Concurrent meetings | 3+ simultaneous |

## Testing

| Suite | Tests | Tool |
|---|---|---|
| Backend unit + integration | 45+ | pytest + pytest-asyncio |
| Frontend components + hooks | 14+ | vitest + testing-library |
| Linting (backend) | - | ruff |
| Linting (frontend) | - | ESLint |
| CI | Auto | GitHub Actions on push/PR |

## Methodology

Built with **BMAD-S** (Breakthrough Method of Agile AI-Driven Development — Secture edition):

- **48 functional requirements** + **18 non-functional requirements** in PRD
- **22 stories** across **6 epics** + Epic 7 (multi-agent pipeline)
- **VRG protocol** (Verify/Refine/Generate) on every story
- **Context7 + web search** for documentation verification before every implementation
- **Adversarial code review** on critical paths
- **Execution log** tracking every step in `_bmad-output/execution-log.yaml`

## Team

**Antonio + Gonzalo** — Hackathon Secture 2026

## License

Proprietary — Secture S.L.
