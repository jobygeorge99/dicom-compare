import { type FormEvent, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router";

import { ApiError } from "../api/client";
import { useAuth } from "../auth/context";

export function LoginPage() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // "Controlled inputs": React state is the single source of truth for
  // what's typed; each keystroke updates state, state fills the input.
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Where RequireAuth sent us from; default to the home page.
  const from = (location.state as { from?: string } | null)?.from ?? "/";

  if (user !== null) {
    return <Navigate to={from} replace />; // already logged in
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); // stop the browser's old-style full-page form submit
    setError(null);
    setSubmitting(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not reach the server.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <form className="card login-card" onSubmit={handleSubmit}>
        <h1>DICOM Compare</h1>
        <p className="muted">Sign in with the account your administrator gave you.</p>

        <label>
          Email
          <input
            type="email"
            autoComplete="username"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </label>

        <label>
          Password
          <input
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>

        {/* role="alert" makes screen readers announce the error. */}
        {error !== null && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <button type="submit" disabled={submitting}>
          {submitting ? "Signing in…" : "Sign in"}
        </button>

        <p className="muted small">For learning and measurement only. Not for diagnosis.</p>
      </form>
    </div>
  );
}
