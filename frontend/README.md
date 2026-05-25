# Otto Frontend

A React (Vite) single-page app for the Otto backend: users can register, log
in, and chat with the research-assistant agent.

## What's wired up

| Backend endpoint            | Where it's used                                            |
| --------------------------- | --------------------------------------------------------- |
| `POST /api/v1/user/register` | Sign-up form on the login screen                          |
| `POST /api/v1/user/login`    | Log-in form                                               |
| `POST /api/v1/user/refresh`  | Automatic — the API client refreshes an expired access token and retries the request before forcing logout |
| `POST /api/v1/chat`          | Chat screen; the returned `thread_id` is threaded back into each message to keep the conversation going |
| `GET /api/v1/`               | `healthCheck()` helper in the API client                  |

Auth note: the backend expects `Authorization: Token <access_token>` (a literal
`Token ` prefix, not `Bearer`). The client sends exactly that.

## Run it

### Whole system with Docker (recommended)

From the repo root, this builds and starts the database, backend, and frontend
together:

```bash
export ANTHROPIC_API_KEY=sk-...   # required by the backend
docker compose up --build
```

Then open **http://localhost**. The frontend container serves the built SPA and
reverse-proxies `/api` to the backend, so everything is on a single origin.

### Frontend only (local dev with hot reload)

The backend must be running first (default `http://localhost:8000`).

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api/*` to the backend,
so there are no cross-origin issues.

## Configuration

Copy `.env.example` to `.env` to override defaults:

- `VITE_API_BASE` — API base path (default `/api/v1`). Set to an absolute URL to
  bypass the dev proxy.
- `VITE_PROXY_TARGET` — where the dev server forwards `/api` (default
  `http://localhost:8000`).

## Build for production

```bash
npm run build      # outputs to dist/
npm run preview    # serve the production build locally
```

## Project layout

```
src/
  api/client.js          fetch wrapper: token storage, auto-refresh, endpoints
  auth/AuthContext.jsx   login/register/logout state, persisted to localStorage
  components/
    LoginPage.jsx        email/password form, toggles login <-> sign up
    ChatPage.jsx         message list + composer, manages thread_id
  App.jsx                routes between login and chat based on auth state
  main.jsx               entry point
  styles.css             styling
```
