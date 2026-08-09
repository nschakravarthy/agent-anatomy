import { createContext, useCallback, useContext, useEffect, useState } from 'react';
import {
  clearAuth,
  loadAuth,
  login as apiLogin,
  register as apiRegister,
  saveAuth,
} from '../api/client.js';

const AuthContext = createContext(null);

// Roles the backend can hand back; mirrors api/user/models.py::UserRole.
export const ROLES = { USER: 'user', ADMIN: 'admin' };

export function AuthProvider({ children }) {
  // Seed from localStorage so a refresh keeps the user logged in. The role
  // arrives in the login/register response and is stored alongside the tokens,
  // so it survives a reload without another round trip.
  const [auth, setAuth] = useState(() => loadAuth());

  // The API client dispatches "auth:logout" when a token refresh fails; mirror
  // that into React state so the UI falls back to the login screen.
  useEffect(() => {
    const onLogout = () => setAuth(null);
    window.addEventListener('auth:logout', onLogout);
    return () => window.removeEventListener('auth:logout', onLogout);
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password);
    saveAuth(data);
    setAuth(data);
    return data;
  }, []);

  const register = useCallback(async (email, password) => {
    const data = await apiRegister(email, password);
    saveAuth(data);
    setAuth(data);
    return data;
  }, []);

  const logout = useCallback(() => {
    clearAuth();
    setAuth(null);
  }, []);

  // Anything not explicitly "admin" is treated as a plain user, so a missing or
  // unrecognised role fails closed.
  const role = auth?.role === ROLES.ADMIN ? ROLES.ADMIN : ROLES.USER;

  const value = {
    auth,
    userId: auth?.user_id ?? null,
    role,
    isAdmin: role === ROLES.ADMIN,
    isAuthenticated: Boolean(auth?.access_token),
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
