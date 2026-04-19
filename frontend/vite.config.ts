import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: true,
    // Proxy /api/* → backend (uvicorn locally, API Gateway in prod via VITE_API_URL)
    proxy: {
      '/api': {
        target: 'https://hazard-dislodge-trouble.ngrok-free.dev',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
