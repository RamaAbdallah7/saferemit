import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Run the FastAPI backend on :8000 (uvicorn backend.app:app --reload)
      // and this dev server proxies /api calls to it, so App.jsx can just
      // fetch('/api/...') in both dev and the built production bundle.
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
  },
})
