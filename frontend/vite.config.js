import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// During dev, requests to /api are proxied to the FastAPI backend so the
// browser never makes a cross-origin call. Override the target with
// VITE_PROXY_TARGET if the backend runs somewhere other than localhost:8000.
const target = process.env.VITE_PROXY_TARGET || 'http://localhost:8000';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target,
        changeOrigin: true,
      },
    },
  },
});
