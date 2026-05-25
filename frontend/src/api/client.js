// Thin wrapper around the Otto FastAPI backend.
//
// Two backend quirks drive this file:
//   1. The auth middleware expects `Authorization: Token <access_token>`
//      (a literal "Token " prefix, not "Bearer"), so we always send that.
//   2. There is no chat-history endpoint; conversation continuity is keyed on
//      the thread_id the /chat response returns, which the caller threads back
//      into the next request.

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api/v1';
const STORAGE_KEY = 'otto_auth';

// ---- token persistence -----------------------------------------------------

export function loadAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function saveAuth(auth) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
}

export function clearAuth() {
  localStorage.removeItem(STORAGE_KEY);
}

// Broadcast a forced logout (refresh failed) so the AuthContext can drop its
// React state without the client needing a direct reference to it.
function forceLogout() {
  clearAuth();
  window.dispatchEvent(new Event('auth:logout'));
}

// ---- request plumbing ------------------------------------------------------

async function parseError(res) {
  let detail = `Request failed (${res.status})`;
  try {
    const data = await res.json();
    if (data?.detail) {
      detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    }
  } catch {
    // Non-JSON body — keep the generic message.
  }
  return new Error(detail);
}

// Exchange the stored refresh token for a fresh access token. Returns the
// updated auth object on success, or null if there is nothing to refresh with
// or the backend rejects the refresh token.
async function refreshTokens() {
  const auth = loadAuth();
  if (!auth?.refresh_token) return null;

  const res = await fetch(`${API_BASE}/user/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: auth.refresh_token }),
  });
  if (!res.ok) return null;

  const tokens = await res.json();
  const updated = { ...auth, ...tokens };
  saveAuth(updated);
  return updated;
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const doFetch = () => {
    const headers = { 'Content-Type': 'application/json' };
    if (auth) {
      const current = loadAuth();
      if (current?.access_token) {
        headers.Authorization = `Token ${current.access_token}`;
      }
    }
    return fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  };

  let res = await doFetch();

  // On an expired/invalid access token, try one refresh-and-retry before
  // giving up and forcing the user back to the login screen.
  if (res.status === 401 && auth) {
    const refreshed = await refreshTokens();
    if (refreshed) {
      res = await doFetch();
    }
    if (res.status === 401) {
      forceLogout();
      throw await parseError(res);
    }
  }

  if (!res.ok) {
    throw await parseError(res);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

// ---- endpoints -------------------------------------------------------------

export function register(email, password) {
  return request('/user/register', { method: 'POST', body: { email, password }, auth: false });
}

export function login(email, password) {
  return request('/user/login', { method: 'POST', body: { email, password }, auth: false });
}

export function sendMessage(message, threadId) {
  const body = { message };
  if (threadId) body.thread_id = threadId;
  return request('/chat', { method: 'POST', body });
}

export function healthCheck() {
  return request('/', { auth: false });
}
