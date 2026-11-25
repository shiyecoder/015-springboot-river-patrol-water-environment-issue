import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 前端端口 5174（通道 5），接口与上传静态资源都代理到本通道后端 8084
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5174,
    host: '127.0.0.1',
    proxy: {
      '/api': { target: 'http://127.0.0.1:8084', changeOrigin: true },
      '/uploads': { target: 'http://127.0.0.1:8084', changeOrigin: true }
    }
  },
  build: { outDir: 'dist', chunkSizeWarningLimit: 1600 }
})
