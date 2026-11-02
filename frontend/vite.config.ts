// Vite: the dev server (npm run dev) and the production bundler (npm run build).
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()], // JSX/TSX support + instant reload of components on save
  server: {
    port: 5173,
    // The proxy: the browser calls http://localhost:5173/api/..., and Vite
    // forwards it to FastAPI on port 8000. To the browser everything is ONE
    // origin, so CORS never comes up during development.
    proxy: {
      "/api": "http://localhost:8000",
      "/health": "http://localhost:8000",
    },
  },
});
