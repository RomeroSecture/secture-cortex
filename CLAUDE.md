# Secture Cortex

Copiloto IA para reuniones con clientes. Cruza transcripción en tiempo real con contexto técnico del proyecto.

> "El copiloto que escucha, cruza y responde. Porque 'déjame mirarlo' ya no es opción."

## Contexto

Hackathon Secture 2026. Equipo: Antonio + Gonzalo. 24h para demo funcional.
El jurado técnico es una IA que evalúa: calidad del desarrollo, seguridad, y continuidad.

## Planificación

Toda la planificación está en `_bmad-output/planning-artifacts/`. Lee estos documentos ANTES de implementar:

- `prd.md` — 48 FRs, 18 NFRs, user journeys, scope
- `architecture.md` — Stack, patterns, structure, decisions, validation
- `epics.md` — 22 stories en 6 épicas con acceptance criteria

## Stack

| Capa | Tecnología |
|---|---|
| Backend | FastAPI (Python) — async end-to-end |
| Frontend | Next.js 15 + shadcn/ui + Tailwind CSS |
| DB | PostgreSQL 16 + pgvector (Docker) |
| ORM | SQLAlchemy 2.0+ async (asyncpg) |
| Migrations | Alembic |
| RAG | LangChain + pgvector |
| Transcripción | Deepgram Nova-3 Multilingual (Python SDK, WebSocket) |
| LLM | Groq — Qwen3 32B primary, Llama 3.1 8B fallback (OpenAI-compatible) |
| Embeddings | Jina v3 API — 1024 dims (OpenAI-compatible) |
| Auth | NextAuth.js v5 (frontend) + FastAPI JWT middleware (backend) |
| Real-time | FastAPI WebSocket nativo |
| Deploy | Docker Compose |
| Testing | pytest (backend) + vitest (frontend) |
| CI | GitHub Actions (ruff + pytest + eslint + vitest) |

## Estructura del monorepo

```
secture-cortex/
├── docker-compose.yml
├── .env.example
├── .github/workflows/ci.yml
├── frontend/          # Next.js 15
│   └── src/
│       ├── app/       # App Router (pages)
│       ├── components/ # Por feature: dashboard/, insights/, transcription/, projects/
│       ├── hooks/     # use-websocket.ts, use-audio.ts, use-meeting.ts
│       ├── lib/       # api.ts, auth.ts, utils.ts
│       └── types/     # meeting.ts, project.ts, websocket.ts
├── backend/           # FastAPI
│   └── app/
│       ├── api/v1/    # REST endpoints
│       ├── ws/        # WebSocket handlers (transcription, insights)
│       ├── models/    # SQLAlchemy models
│       ├── schemas/   # Pydantic v2 schemas
│       ├── services/  # Business logic (deepgram, rag, llm, embeddings, meeting_manager)
│       ├── repositories/ # DB access
│       └── core/      # security.py, logging.py
└── db/
    └── init.sql       # CREATE EXTENSION vector;
```

## Orden de implementación

Ejecutar stories en orden secuencial: 1.1 → 1.2 → ... → 6.4. Ver `epics.md` para detalle.

1. **Epic 1**: Auth + proyectos (Docker, FastAPI boilerplate, login, CRUD projects, RBAC)
2. **Epic 2**: Contexto (upload files, chunking, Jina embeddings, pgvector indexing)
3. **Epic 3**: Transcripción (meetings, audio capture, Deepgram WebSocket, live dashboard)
4. **Epic 4**: Copiloto IA (RAG pipeline, insight types, insights panel, feedback)
5. **Epic 5**: Memoria (save meetings, history, context acumulativo)
6. **Epic 6**: Producción (tests, CI, docs)

## Reglas obligatorias

### Backend Python

1. **Type hints** en toda función — sin excepción
2. **Pydantic v2** para todo input/output de API — nunca dicts crudos
3. **Async/await** en todo — nunca sync
4. **Docstrings** en funciones públicas
5. **structlog** para logging — nunca `print()`
6. **Separación de capas**: api/ → services/ → repositories/ → models/

### Frontend TypeScript

7. **Strict mode** — nunca `any`
8. **Interfaces** para props/objetos, **types** para unions
9. **Server Components** por defecto — `"use client"` solo cuando necesario

### API Design

10. **REST**: plural, lowercase, kebab-case (`/api/v1/context-files`)
11. **Status codes**: 200 GET, 201 POST, 204 DELETE, 400/401/403/404/422/500
12. **Response format**: `{ "data": ... }` éxito, `{ "error": { "code", "message" } }` error
13. **WebSocket format**: `{ "type": "...", "payload": { ... }, "timestamp": "ISO8601" }`

### Security (OWASP)

14. **Pydantic validation** en TODOS los endpoints
15. **SQLAlchemy ORM** — nunca raw SQL con f-strings
16. **JWT** con expiración + middleware en todas las rutas
17. **CORS** whitelist explícita — nunca `*`
18. **Secrets** en `.env` + pydantic Settings — `.env` en `.gitignore`
19. **File upload**: validar tipo y tamaño
20. **Nunca** stacktrace al client
21. **Nunca** queries sin `project_id` filter (multi-tenancy)

### Naming

| Contexto | Convención | Ejemplo |
|---|---|---|
| DB tables | plural, snake_case | `users`, `context_files` |
| DB columns | snake_case | `created_at`, `project_id` |
| DB FKs | `{singular}_id` | `meeting_id` |
| Python files | snake_case.py | `meeting_manager.py` |
| Python classes | PascalCase | `MeetingManager` |
| Python functions | snake_case | `get_project_context()` |
| TS files | kebab-case.tsx | `insight-card.tsx` |
| TS components | PascalCase | `InsightCard` |
| TS functions | camelCase | `handleFeedback()` |
| API endpoints | plural, kebab-case | `/api/v1/context-files` |
| JSON fields | snake_case | `{ "meeting_id": 1 }` |
| Fechas JSON | ISO 8601 | `2026-03-27T10:30:00Z` |

## Environment variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://cortex:cortex_dev@db:5432/cortex

# Deepgram
DEEPGRAM_API_KEY=your_deepgram_key

# LLM (Groq — OpenAI compatible)
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=gsk_your_groq_key
LLM_MODEL=qwen/qwen3-32b
LLM_FALLBACK_MODEL=llama-3.1-8b-instant

# Embeddings (Jina — OpenAI compatible)
EMBEDDINGS_BASE_URL=https://api.jina.ai/v1
EMBEDDINGS_API_KEY=jina_your_key
EMBEDDINGS_MODEL=jina-embeddings-v3

# Auth
JWT_SECRET=your_jwt_secret
NEXTAUTH_SECRET=your_nextauth_secret
NEXTAUTH_URL=http://localhost:3000

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

## Key architectural decisions

- **Audio**: getUserMedia (mic) + getDisplayMedia (tab audio) — dos canales separados
- **Transcripción**: Deepgram via WebSocket, diarización por speaker, español
- **RAG**: Buffer ~30s transcripción → Jina embed → pgvector top-5 → Groq LLM → insight JSON
- **pgvector**: HNSW index, 1024 dims, chunks 512 tokens, overlap 50
- **WebSocket protocol**: `audio_chunk`, `transcription`, `insight`, `meeting_status`, `error`, `feedback`
- **DB tables created per-story**: no big bang schema — cada story crea solo lo que necesita
