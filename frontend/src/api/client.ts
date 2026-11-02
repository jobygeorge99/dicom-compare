// The ONE place the frontend talks to the backend.
// Every call goes through request(), which adds the token, turns error
// responses into ApiError, and reports 401s so the app can log out.
// Pages never call fetch() directly.

import { getToken } from "../auth/token";
import type { Token, User, UserCreate } from "./types";

export class ApiError extends Error {
  readonly status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// AuthProvider registers its logout function here, so a 401 from ANY call
// (for example an expired token) logs the user out everywhere.
let onUnauthorized: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  onUnauthorized = handler;
}

// FastAPI errors look like {"detail": "text"}, or for 422 validation errors
// {"detail": [{"msg": "...", ...}, ...]}. Turn either into one readable line.
function readErrorMessage(body: unknown, fallback: string): string {
  if (typeof body !== "object" || body === null || !("detail" in body)) {
    return fallback;
  }
  const { detail } = body as { detail: unknown };
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((item: unknown) =>
        typeof item === "object" && item !== null && "msg" in item
          ? String((item as { msg: unknown }).msg)
          : String(item),
      )
      .join("; ");
  }
  return fallback;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  // A relative URL: in dev the Vite proxy forwards it to FastAPI.
  const response = await fetch(`/api/v1${path}`, { ...init, headers });

  if (!response.ok) {
    const body: unknown = await response.json().catch(() => null);
    // Only a REJECTED token means "log out". A failed login attempt
    // (no token sent) is just a wrong password.
    if (response.status === 401 && token) {
      onUnauthorized?.();
    }
    throw new ApiError(response.status, readErrorMessage(body, response.statusText));
  }

  return (await response.json()) as T;
}

export const api = {
  // OAuth2 login is a FORM post. URLSearchParams sends it as
  // application/x-www-form-urlencoded, which is what FastAPI expects.
  login: (email: string, password: string): Promise<Token> =>
    request<Token>("/auth/login", {
      method: "POST",
      body: new URLSearchParams({ username: email, password }),
    }),

  getMe: (): Promise<User> => request<User>("/users/me"),

  listUsers: (): Promise<User[]> => request<User[]>("/admin/users"),

  createUser: (body: UserCreate): Promise<User> =>
    request<User>("/admin/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }),
};
