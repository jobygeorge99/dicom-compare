// A route guard: wrap any page that needs a logged-in user (and optionally a role).
//
// IMPORTANT: this is for user experience only. Anyone can edit JavaScript in
// their own browser, so the frontend can NEVER be the security boundary.
// The backend's require_permission is what actually protects the data; this
// just avoids showing people screens that would only give them 401/403.

import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router";

import type { Role } from "../api/types";
import { useAuth } from "./context";

interface Props {
  children: ReactNode;
  roles?: Role[]; // omit = any logged-in user
}

export function RequireAuth({ children, roles }: Props) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <p className="page-message">Loading…</p>;
  }

  if (user === null) {
    // Remember where they were going, so login can send them back there.
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (roles !== undefined && !roles.includes(user.role)) {
    return (
      <div className="page-message">
        <h1>Not allowed</h1>
        <p>Your role ({user.role}) can't open this page.</p>
      </div>
    );
  }

  return <>{children}</>;
}
