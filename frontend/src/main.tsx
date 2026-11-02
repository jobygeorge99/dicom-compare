// Entry point: index.html loads this file. It wraps the app in its
// "providers", the shared services every component can use.

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";

import { App } from "./App";
import { AuthProvider } from "./auth/AuthProvider";
import "./index.css";

const queryClient = new QueryClient();

const rootElement = document.getElementById("root");
if (rootElement === null) {
  throw new Error("index.html is missing <div id='root'>");
}

createRoot(rootElement).render(
  // StrictMode: in development only, runs some code twice on purpose to
  // expose bugs. If you see a request twice in dev, this is why.
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <App />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
