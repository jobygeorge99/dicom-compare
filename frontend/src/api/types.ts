// TypeScript versions of the backend's Pydantic schemas.
// Field names stay snake_case to match the JSON exactly.

export type Role = "admin" | "analyst" | "viewer";

export const ROLES: readonly Role[] = ["admin", "analyst", "viewer"];

// Matches UserRead in backend/app/schemas/user.py.
export interface User {
  id: number;
  email: string;
  role: Role;
  is_active: boolean;
  created_at: string; // ISO date string: JSON has no date type
}

// Matches Token in backend/app/schemas/auth.py.
export interface Token {
  access_token: string;
  token_type: "bearer";
}

// Matches UserCreate in backend/app/schemas/user.py.
export interface UserCreate {
  email: string;
  password: string;
  role: Role;
}
