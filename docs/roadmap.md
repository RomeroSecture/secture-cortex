# Secture Cortex — Roadmap

## Phase 1: MVP (Hackathon) ✅ COMPLETE

### Implemented (30/30 stories across 7 epics)

**Epic 1: Acceso y gestión de proyectos**
- Auth (register, login, JWT) + user profile with role selection
- Project CRUD (create, edit, delete) + RBAC (5 roles: admin, tech_lead, developer, pm, commercial)
- Member management (assign users by email, role-based access, project isolation)
- Admin panel: user management

**Epic 2: Carga y gestión de contexto**
- Context file management (upload, delete, re-index, status tracking)
- Auto-indexing: chunking 512 tokens + Jina v3 embeddings + pgvector HNSW
- PDF/DOCX text extraction (PyMuPDF + python-docx)

**Epic 3: Reunión en vivo con transcripción**
- Real-time transcription: Deepgram Nova-3 Multilingual + speaker diarization
- Dual-channel audio capture (mic + tab audio via getUserMedia/getDisplayMedia)
- Live dashboard: 2-panel (transcription + insights), color-coded types

**Epic 4: Copiloto inteligente**
- RAG pipeline: Jina embed → pgvector top-5 → Groq Qwen3 32B → insight JSON
- 3 insight types: alerts (red), scope classification (blue), suggestions (green)
- User feedback on insights (useful/not_useful/dismissed) → feeds RAG prompt
- AI disclaimer on all insights

**Epic 5: Memoria y contexto acumulativo**
- Meeting history: list + full review (transcription + insights)
- Cumulative memory: meeting transcriptions → pgvector for future meetings

**Epic 6: Producción y continuidad**
- 105 backend tests (pytest) + 14 frontend tests (vitest)
- CI: GitHub Actions (ruff + pytest + eslint + vitest + next build)
- Docker Compose deployment (3 services)
- Documentation: CLAUDE.md, AGENTS.md, .env.example, Swagger /docs

**Epic 7: Pipeline multi-agente role-aware con LangGraph**
- LangGraph Supervisor pipeline: topic classification → specialist agent routing
- 4 specialist agents: Tech Lead (6 tools), Dev (5 tools), PM (6 tools), Commercial (5 tools)
- 22 agent tools total (vector search, scope classification, effort estimation, etc.)
- Insight synthesis: conflict detection, compound insights, role-aware confidence filtering
- Role-filtered WebSocket delivery (per-role confidence thresholds)
- Conversation intelligence: decision detection, action items, questions, sentiment, jargon translation
- Post-meeting intelligence: 6 outputs (structured minutes, handoff package, sprint impact, client email draft, internal briefing, retrospective)
- Advanced dashboard: KPI bar, Copiloto/Inteligencia tabs, conversation tracker
- Project analytics: KB health score, context freshness, knowledge gap detection

### Technical highlights
- Async end-to-end (FastAPI + asyncpg + websockets)
- Raw async WebSocket to Deepgram (bypassed SDK sync issues)
- PCM linear16 @ 48kHz from browser AudioContext (not MediaRecorder WebM)
- Pydantic validation on LLM JSON output
- Groq compatibility: response_format json_object + manual parse (not with_structured_output)
- SQLAlchemy enum values_callable for PostgreSQL native enums
- pytest-asyncio session-scoped event loop for SQLAlchemy compatibility
- UI: "Quiet Intelligence" warm dark theme, Geist font, Motion animations

### Numbers
- 41 REST endpoints + 1 WebSocket
- 15 DB tables + pgvector HNSW index
- 11 Alembic migrations
- 15 frontend routes, 22 components, 2 custom hooks
- 105 backend tests + 14 frontend tests = 119 total
- 19 backend services, 22 agent tools
- 48 BMAD-S execution log entries, 0 pending

## Phase 2: Growth

- Web search integration for real-time context enrichment
- Meeting analytics: graphs, trends, insight accuracy over time
- Export to PDF/Markdown (transcription + insights + outputs)
- Onboarding from Git repositories (auto-index codebase)
- Improved diarization with speaker name assignment
- Conversation search within meetings
- Multi-meeting trend analysis and client profiling

## Phase 3: Expansion

- Client portal (read-only meeting summaries for clients)
- Integrations: Jira, Linear, Notion, Slack
- Browser extension for one-click meeting capture
- In-person meeting support (mobile mic capture)
- Multi-language support (currently Spanish-optimized)
- Custom insight types per project
- Keyboard shortcuts for power users

## Phase 4: SaaS

- Multi-tenant platform for software consultancies
- Subscription billing (Stripe)
- Admin dashboard with usage analytics
- SSO (SAML/OIDC) for enterprise clients
- On-premise deployment option
- SLA and support tiers
- SOC 2 compliance
