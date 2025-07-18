import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/get-video-info': 'http://localhost:5000',
      '/video-info': 'http://localhost:5000',
      '/start-download': 'http://localhost:5000',
      '/progress': 'http://localhost:5000',
      '/stream-download': 'http://localhost:5000'
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
