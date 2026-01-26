import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import {visualizer} from 'rollup-plugin-visualizer'
import compression from 'vite-plugin-compression';

// https://vite.dev/config/
export default defineConfig({
  optimizeDeps: {
    exclude: ["rrweb"],
  },
  plugins: [
    vue(),
    compression(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  manualChunks: {}
})
