import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_BACKEND_URL || 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: 5173,
      proxy: {
        // Backend FastAPI đặt prefix /api cho mọi router → KHÔNG rewrite bỏ /api
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
          configure: (proxy) => {
            proxy.on('error', (err) => {
              console.error('[proxy error]', err.message)
              console.error(`  → Backend không chạy tại ${backendUrl}`)
              console.error('  → Khởi động backend: cd backend && uvicorn main:app --reload --port 8000')
            })
          },
        },
      },
    },
  }
})
