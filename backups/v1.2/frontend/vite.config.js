import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3001,
    proxy: {
      '/api': {
        target: 'http://localhost:5002',
        changeOrigin: true,
      },
      // '/api/auth/login': {
      //   target: 'http://localhost:5002',
      //   changeOrigin: true,
      //   rewrite: (path) => path.replace(/^\/api\/auth\/login/, '/login'),
      // },
      '/logout': {
        target: 'http://localhost:5002',
        changeOrigin: true,
      },
    },
  },
}) 