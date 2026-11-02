// Holds the login state and offers login() / logout() to the whole app.

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { type ReactNode, useCallback, useEffect, useMemo, useState } from "react";

import { api, setUnauthorizedHandler } from "../api/client";
import { type AuthState, AuthContext } from "./context";
import { clearToken, getToken, setToken } from "./token";

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();

  // The token in React state, so changing it re-renders the app.
  // The function form reads sessionStorage once, on first render only.
  const [token, setTokenState] = useState<string | null>(() => getToken());

  const logout = useCallback(() => {
    clearToken();
    setTokenState(null);
    queryClient.clear(); // forget every cached response from the old user
  }, [queryClient]);

  // useEffect = "do this after rendering". Here: register logout() with the
  // API client, and unregister it if this component ever goes away.
  useEffect(() => {
    setUnauthorizedHandler(logout);
    return () => setUnauthorizedHandler(null);
  }, [logout]);

  // Ask the backend who this token belongs to. TanStack Query handles the
  // loading/error states and caching. `enabled` = only when we have a token.
  // The token is part of the key, so a new token means a fresh request.
  const me = useQuery({
    queryKey: ["me", token],
    queryFn: api.getMe,
    enabled: token !== null,
    retry: false, // a rejected token won't get better by retrying
  });

  const login = useCallback(async (email: string, password: string) => {
    const { access_token } = await api.login(email, password); // throws ApiError on 401
    setToken(access_token);
    setTokenState(access_token); // triggers the "me" query above
  }, []);

  // useMemo: build a new object only when something in it changed, so
  // components using useAuth() don't re-render for no reason.
  const value = useMemo<AuthState>(
    () => ({
      user: token !== null ? (me.data ?? null) : null,
      isLoading: token !== null && me.isPending,
      login,
      logout,
    }),
    [token, me.data, me.isPending, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
