import { loadEnv } from 'vite'
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const frontendPort = Number(env.VITE_FRONTEND_PORT || '5180')

  return {
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: frontendPort,
    },
    preview: {
      host: '0.0.0.0',
      port: frontendPort,
    },
    test: {
      environment: 'jsdom',
      setupFiles: ['./src/test/setup.ts'],
    },
  }
})
