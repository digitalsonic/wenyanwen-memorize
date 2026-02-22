import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [vue()],
    // 生产环境部署在 /wenyanwen/ 路径下
    base: mode === 'production' ? '/wenyanwen/' : '/',
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    // 开发服务器配置（仅 npm run dev 时生效）
    server: {
      port: 5173,
      proxy: {
        '/api': {
          // 将 /api 请求代理到后端开发服务器
          target: env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
        },
      },
    },
    test: {
      globals: true,
      environment: 'jsdom',
      coverage: {
        provider: 'v8',
        reporter: ['text', 'html', 'json'],
        exclude: ['node_modules/', 'tests/'],
      },
    },
  }
})
