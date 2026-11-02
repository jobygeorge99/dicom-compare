import { Link } from "react-router";

export function NotFoundPage() {
  return (
    <div className="page-message">
      <h1>Page not found</h1>
      <Link to="/">Go to the home page</Link>
    </div>
  );
}
