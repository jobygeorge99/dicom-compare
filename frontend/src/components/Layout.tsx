// The frame around every logged-in page: header, navigation, user menu.
// <Outlet /> is where React Router draws the current page.

import { NavLink, Outlet, useNavigate } from "react-router";

import { useAuth } from "../auth/context";

export function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app">
      <header className="app-header">
        <span className="brand">DICOM Compare</span>
        <nav>
          <NavLink to="/" end>
            Home
          </NavLink>
          {/* Only show admin links to admins. The backend still enforces it. */}
          {user?.role === "admin" && <NavLink to="/admin/users">Users</NavLink>}
        </nav>
        <div className="user-menu">
          <span>{user?.email}</span>
          <span className={`badge badge-${user?.role ?? ""}`}>{user?.role}</span>
          <button type="button" className="button-secondary" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
