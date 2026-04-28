import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: '127.0.0.1',
    open: false,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        secure: false,
        ws: true,
        timeout: 180000,  // 3分钟超时
        proxyTimeout: 180000,
        // 禁用缓冲,支持流式响应
        buffer: false,
        // 保持连接活跃
        followRedirects: true,
        headers: {
          Connection: 'keep-alive',
          'Keep-Alive': 'timeout=180000'
        },
        configure: (proxy, _options) => {
          proxy.on('error', (err, req, res) => {
            console.error('代理错误:', err.message, req.url)
            if (res && !res.headersSent) {
              res.writeHead(502, { 'Content-Type': 'application/json' })
              res.end(JSON.stringify({ error: '代理错误', message: err.message }))
            }
          })
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('代理请求:', req.method, req.url)
            // 确保流式请求头正确传递
            if (req.headers['accept'] && req.headers['accept'].includes('text/event-stream')) {
              proxyReq.setHeader('Accept', 'text/event-stream')
            }
          })
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('代理响应:', proxyRes.statusCode, req.url)
            // 确保流式响应头正确传递
            if (proxyRes.headers['content-type'] && proxyRes.headers['content-type'].includes('text/event-stream')) {
              res.setHeader('Content-Type', 'text/event-stream')
              res.setHeader('Cache-Control', 'no-cache')
              res.setHeader('Connection', 'keep-alive')
            }
          })
        }
      },
      '/media': {
        target: 'http://127.0.0.1:8080',
        changeOrigin: true,
        secure: false
      }
    },
    hmr: {
      overlay: true
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  }
})