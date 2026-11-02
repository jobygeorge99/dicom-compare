// The route table: which URL shows which page, and who may see it.

import { Route, Routes } from "react-router";

import { RequireAuth } from "./auth/RequireAuth";
import { Layout } from "./components/Layout";
import { HomePage } from "./pages/HomePage";
import { LoginPage } from "./pages/LoginPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { UsersPage } from "./pages/UsersPage";

export function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      {/* Everything inside needs a logged-in user, and shares the Layout. */}
      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<HomePage />} />
        <Route
          path="admin/users"
          element={
            <RequireAuth roles={["admin"]}>
              <UsersPage />
            </RequireAuth>
          }
        />
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
