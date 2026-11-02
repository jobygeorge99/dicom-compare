import type { Role } from "../api/types";
import { useAuth } from "../auth/context";

// What each role can do, in plain words. Mirrors backend/app/core/permissions.py.
const ROLE_SUMMARY: Record<Role, string> = {
  admin: "You can manage users and see every comparison.",
  analyst: "You can upload two scans and compare them.",
  viewer: "You can view comparisons shared with you.",
};

export function HomePage() {
  const { user } = useAuth();
  if (user === null) {
    return null; // RequireAuth guarantees a user; this satisfies TypeScript
  }

  return (
    <section>
      <h1>Welcome</h1>
      <div className="card">
        <p>
          Signed in as <strong>{user.email}</strong> with the role{" "}
          <span className={`badge badge-${user.role}`}>{user.role}</span>.
        </p>
        <p>{ROLE_SUMMARY[user.role]}</p>
      </div>
      <div className="card muted">
        <h2>Coming in Phase 2</h2>
        <p>Upload a prior and a current scan to see what changed between them.</p>
      </div>
    </section>
  );
}
