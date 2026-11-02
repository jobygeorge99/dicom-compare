// Admin page: list users and create new ones.
// Shows the two TanStack Query building blocks:
//   useQuery    = READ data (GET), with loading/error/caching handled
//   useMutation = CHANGE data (POST/PUT/DELETE)

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { type FormEvent, useState } from "react";

import { api } from "../api/client";
import { ROLES, type Role } from "../api/types";

export function UsersPage() {
  const queryClient = useQueryClient();
  const users = useQuery({ queryKey: ["users"], queryFn: api.listUsers });

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<Role>("analyst");

  const createUser = useMutation({
    mutationFn: api.createUser,
    onSuccess: async () => {
      setEmail("");
      setPassword("");
      setRole("analyst");
      // The cached list is now out of date: mark it stale so it refetches.
      await queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    createUser.mutate({ email, password, role });
  }

  return (
    <section>
      <h1>Users</h1>

      <form className="card form-row" onSubmit={handleSubmit}>
        <h2>Create a user</h2>
        <label>
          Email
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label>
          Temporary password (12+ characters)
          <input
            type="password"
            autoComplete="new-password"
            required
            minLength={12}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        <label>
          Role
          <select value={role} onChange={(e) => setRole(e.target.value as Role)}>
            {ROLES.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" disabled={createUser.isPending}>
          {createUser.isPending ? "Creating…" : "Create user"}
        </button>
        {createUser.isError && (
          <p className="error" role="alert">
            {createUser.error.message}
          </p>
        )}
        {createUser.isSuccess && <p className="success">Created {createUser.data.email}.</p>}
      </form>

      <div className="card">
        {users.isPending && <p>Loading users…</p>}
        {users.isError && (
          <p className="error" role="alert">
            {users.error.message}
          </p>
        )}
        {users.data && (
          <table>
            <thead>
              <tr>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {/* `key` tells React which row is which, so it updates rows
                  instead of redrawing the whole table. Use a stable id. */}
              {users.data.map((u) => (
                <tr key={u.id}>
                  <td>{u.email}</td>
                  <td>
                    <span className={`badge badge-${u.role}`}>{u.role}</span>
                  </td>
                  <td>{u.is_active ? "Active" : "Deactivated"}</td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
