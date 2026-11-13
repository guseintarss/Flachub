import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BACKEND = 'http://127.0.0.1:8000'

// Dev-сервер живёт на отдельном порту, а Django проверяет Origin для CSRF.
// Приводим Origin/Referer к backend, чтобы вход не зависел от порта Vite
// (5173, 5174, ...). В production фронтенд отдаётся с того же origin.
function isLocalOrigin(value) {
  if (!value) return false
  try {
    const { hostname } = new URL(value)
    return ['localhost', '127.0.0.1', '[::1]'].includes(hostname)
  } catch {
    return false
  }
}

function backendProxy(options = {}) {
  const { configure, ...rest } = options
  return {
    target: BACKEND,
    changeOrigin: true,
    ...rest,
    configure(proxy) {
      proxy.on('proxyReq', proxyReq => {
        const origin = proxyReq.getHeader('origin')
        if (isLocalOrigin(origin)) {
          proxyReq.setHeader('Origin', BACKEND)
        }
        const referer = proxyReq.getHeader('referer')
        if (isLocalOrigin(referer)) {
          proxyReq.setHeader('Referer', `${BACKEND}/`)
        }
      })
      configure?.(proxy)
    },
  }
}

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'build',
    manifest: true,
  },
  server: {
    port: 5173,
    proxy: {
      '/api': backendProxy(),
      '/admin/': backendProxy(),
      '/users': backendProxy(),
      '/media': backendProxy(),
      '/static': backendProxy(),
      '/health': backendProxy(),
      '/ajax': backendProxy(),
      '/ws': backendProxy({ ws: true }),
      '/edit': backendProxy(),
      '/upload': backendProxy(),
      '/ckeditor5': backendProxy(),
      '/app': backendProxy(),
    },
  },
})
