import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
// Import from vitest/config, not vite: the `test` block below is only typed there.
import { defineConfig } from "vitest/config";

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      "tests": path.resolve(__dirname, "./tests"),
    },
  },
  optimizeDeps: {
    include: ["sonner"],
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./tests/setup.ts"],
    dir: 'tests',
    globals: true
  }
});
