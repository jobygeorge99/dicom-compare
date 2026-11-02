// The shape of "who is logged in", shared with every component.
//
// Context = React's way to pass a value to deeply nested components
// without handing it down as a prop through every level in between.

import { createContext, useContext } from "react";

import type { User } from "../api/types";

export interface AuthState {
  user: User | null; // null = not logged in
  isLoading: boolean; // true while we check a stored token with the backend
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthState | null>(null);

// A custom hook: components call useAuth() instead of useContext(AuthContext).
export function useAuth(): AuthState {
  const auth = useContext(AuthContext);
  if (auth === null) {
    throw new Error("useAuth() must be used inside <AuthProvider>");
  }
  return auth;
}
