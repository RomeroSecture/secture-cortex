# Secture Cortex — Roadmap

## Phase 1: MVP (Hackathon) ✅ COMPLETE

### Implemented (22/22 stories)
- Auth (register, login, JWT) + user profile with role selection
- Project CRUD (create, edit, delete) + RBAC (5 roles)
- Member management (assign users, role-based access, project isolation)
- Context file management (upload, delete, re-index, status tracking)
- Auto-indexing: chunking 512 tokens + Jina v3 embeddings + pgvector HNSW
- Real-time transcription: Deepgram Nova-3 Multilingual + speaker diarization
- RAG pipeline: Jina embed → pgvector top-5 → Groq Qwen3 32B → insight JSON
- Live dashboard: 2-panel (transcription + insights), color-coded types
- 3 insight types: alerts (red), scope classification (blue), suggestions (green)
- User feedback on insights (useful/not_useful/dismissed) → feeds RAG prompt
- Meeting history: list + full review (transcription + insights)
- Cumulative memory: meeting transcriptions → pgvector for future meetings
- Admin panel: user management
- AI disclaimer on all insights
- WebSocket JWT authentication
- Custom exception handler (OWASP compliant)
- Docker Compose deployment (3 services)
- CI: GitHub Actions (ruff + pytest + eslint + vitest + next build)
- 59 tests (45 backend + 14 frontend)
- 14 frontend routes, 25 backend endpoints

### Technical highlights
- Async end-to-end (FastAPI + asyncpg + websockets)
- Raw async WebSocket to Deepgram (bypassed SDK sync issues)
- PCM linear16 @ 48kHz from browser AudioContext (not MediaRecorder WebM)
- Pydantic validation on LLM JSON output
- SQLAlchemy enum values_callable for PostgreSQL native enums
- pytest-asyncio session-scoped event loop for SQLAlchemy compatibility

## Phase 2: Growth

- Role-based views (Tech Lead, PM, Commercial) with different insight priorities
- Web search integration for real-time context enrichment
- Meeting analytics: graphs, trends, insight accuracy over time
- Export to PDF/Markdown (transcription + insights)
- Onboarding from Git repositories (auto-index codebase)
- Improved diarization with speaker name assignment
- Meeting notes/summary generation post-meeting
- Conversation search within meetings

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
