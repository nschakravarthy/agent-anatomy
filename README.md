# AI Agent Anatomy — Learning Project

A small but architecturally honest AI agent built to explore the core concepts of agent design hands-on. The goal isn't to ship a product — it's to make each piece of the "anatomy of an agent" concrete enough to reason about.

Built with **FastAPI**, **LangGraph**, **SQLModel**, **Alembic**, and **Postgres + pgvector**.

## The anatomy this project explores

### Core capabilities
- **Instructions** — system prompt defining the agent's role and behaviour
- **Knowledge** — user-scoped notes stored as embeddings in pgvector
- **Tools** — atomic actions the agent can take (`web_search`, `save_note`, `retrieve_notes`)
- **Skills** — compositions of tools with their own control flow (research a topic, answer from notes)
- **Memory** — short-term (LangGraph checkpointer in Postgres) and long-term (the notes store)

### Environment interaction
- **Triggers** — FastAPI endpoints that kick off agent runs
- **Surfaces** — REST API (and Swagger UI at `/docs`)
- **Permissions** — JWT auth, per-user data scoping, per-tool authorization

### Observability & improvement
- **Activity** — every tool call logged to Postgres via a LangGraph callback handler
- **Analytics** — `/stats` endpoint surfaces per-user metrics
- **Evals** — pytest-based scenarios that assert on tool choice and response content

## Architecture

```
┌─────────────┐
│  FastAPI    │  auth, /chat, /stats
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  StateGraph │  router → (search → summarise → save) | (retrieve → synthesise) → respond
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Postgres                           │
│   ├─ users, notes, activity_log     │  ← SQLModel + Alembic
│   ├─ checkpoints, checkpoint_writes │  ← LangGraph AsyncPostgresSaver
│   └─ vector extension (pgvector)    │
└─────────────────────────────────────┘
```

### Graph shape

```
            ┌─────────┐
            │  router │
            └────┬────┘
                 │
          ┌──────┴──────┐
          ▼             ▼
     ┌─────────┐   ┌──────────┐
     │ search  │   │ retrieve │
     └────┬────┘   └────┬─────┘
          ▼             ▼
     ┌─────────┐   ┌────────────┐
     │summarise│   │ synthesise │
     └────┬────┘   └────┬───────┘
          ▼             │
     ┌─────────┐        │
     │save_note│        │
     └────┬────┘        │
          └──────┬──────┘
                 ▼
            ┌─────────┐
            │ respond │
            └─────────┘
```

### State

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: int
    thread_id: str
    route: str | None
    search_results: list | None
    retrieved_notes: list | None
```

`user_id` flows through the graph so tool nodes can enforce authorization themselves, not just at the API edge.

## Stack

| Layer            | Choice                                        |
| ---------------- | --------------------------------------------- |
| API              | FastAPI                                       |
| Agent framework  | LangGraph (`StateGraph`)                      |
| ORM              | SQLModel                                      |
| Migrations       | Alembic                                       |
| Database         | Postgres 16                                   |
| Vector store     | pgvector (same Postgres instance)             |
| Short-term memory| `AsyncPostgresSaver` (LangGraph checkpointer) |
| Auth             | JWT (access + refresh tokens)                 |

## Project layout

```
.
├── api/                       # FastAPI application
│   ├── main.py                # app factory, CORS + auth middleware, lifespan
│   ├── core/
│   │   ├── config.py          # Settings, DB connection string, public-path whitelist
│   │   ├── db.py              # async engine + session factory
│   │   ├── models.py          # base SQLModel mixins (UUID, timestamps), HealthCheck
│   │   ├── middleware.py      # JWT auth middleware
│   │   └── routes.py          # root router, health check, mounts user routes
│   └── user/
│       ├── routes.py          # /register, /login, /refresh
│       ├── services.py        # user creation, login, token refresh
│       ├── schemas.py         # request/response Pydantic models
│       ├── models.py          # User SQLModel
│       └── utils.py           # password hashing (Argon2), JWT create/verify
├── workflow/                  # LangGraph agent
│   ├── state.py               # AgentState TypedDict
│   └── models.py              # Note SQLModel (pgvector embedding)
├── migrations/                # Alembic
│   ├── versions/              # migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── README
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── pyproject.toml
├── poetry.lock
├── test.db                    # local SQLite fallback (used when DB_NAME is unset)
└── README.md
```

## Getting started

### Prerequisites
- Docker + Docker Compose
- An LLM API key (Anthropic or OpenAI)
- An embedding API key (OpenAI for `text-embedding-3-small`)
- A web search API key (Tavily free tier works)

### 1. Environment

Create `.env`:

```
DATABASE_URL=postgresql+psycopg://postgres:dev@db:5432/agent
JWT_SECRET=change-me
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...        # for embeddings
TAVILY_API_KEY=...        # for web search
```

A single `DATABASE_URL` works for both SQLModel and the LangGraph checkpointer when using the `psycopg` driver.

### 2. Bring it up

```bash
docker compose up -d db
alembic upgrade head
docker compose up api
```

The Alembic migration creates the `vector` extension, the app tables, and an HNSW index on `notes.embedding`. The LangGraph checkpointer creates its own tables on app startup via `AsyncPostgresSaver.setup()` (idempotent).

### 3. Try it

```bash
# Register
curl -X POST localhost:8000/auth/register \
  -H 'content-type: application/json' \
  -d '{"email":"me@example.com","password":"hunter2"}'

# Login
TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -H 'content-type: application/json' \
  -d '{"email":"me@example.com","password":"hunter2"}' | jq -r .access_token)

# Chat
curl -X POST localhost:8000/chat \
  -H "authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"message":"Research the LangGraph checkpointer and save the key points."}'
```

Or use Swagger at <http://localhost:8000/docs>.

## How each concept lives in the code

| Concept       | Where to look                                                              |
| ------------- | -------------------------------------------------------------------------- |
| Instructions  | `app/nodes.py` — system prompt in the `respond` node                       |
| Knowledge     | `notes` table + `app/memory.py`                                            |
| Tools         | `app/tools.py`                                                             |
| Skills        | `app/graph.py` — the branches off the router                               |
| Memory        | Short-term: `AsyncPostgresSaver` in `main.py` lifespan; Long-term: `notes` |
| Triggers      | `app/routes/chat.py` — synchronous HTTP trigger                            |
| Surfaces      | FastAPI + `/docs`                                                          |
| Permissions   | `app/auth.py` for the edge; `user_id` checks inside tool nodes             |
| Activity      | `app/callbacks.py` writes to `activity_log`                                |
| Analytics     | `app/routes/stats.py`                                                      |
| Evals         | `tests/evals.py`                                                           |

## Design notes & gotchas

- **`metadata` is reserved by SQLAlchemy** — the column on `Note` is named `meta` in Python.
- **Alembic doesn't autogenerate the pgvector extension or HNSW indexes** — these are hand-written in the first migration.
- **The pgvector dimension is fixed at table creation** — currently `1536` for OpenAI `text-embedding-3-small`. Changing models means a migration.
- **`thread_id` is namespaced server-side** as `f"{user_id}:{client_thread_id}"` so users can't read each other's conversation state from the checkpointer.
- **Per-tool permissions** are enforced inside tool nodes, not just at the API boundary — this is what makes the permissions concept visible in agent behaviour rather than just HTTP responses.
- **Activity logging uses a LangGraph callback handler** rather than per-node logging, so observability is architecturally separate from business logic.

## Evals

```bash
pytest tests/evals.py -v
```

Each eval is a scenario: a fixed input, a test thread, and assertions about which tools were called and what the response contains. Not LangSmith-grade, but enough to notice regressions while iterating on prompts or graph shape.

## What this is not

- Production-ready (no rate limiting, minimal error handling, single-process)
- A general-purpose agent framework (it's deliberately small)
- Optimised (pgvector with HNSW is plenty fast for this scale, but no caching, no streaming yet)

The goal was to fit one honest version of each concept into a couple of hours. Extending any of them — multi-turn evals, streaming responses, a real frontend, scheduled triggers, multi-agent orchestration — is the natural next step.