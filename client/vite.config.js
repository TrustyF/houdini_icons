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
    visualizer({
      filename: `dist_stats/stats_${Date.now()}.html`,
      open: false,
      template: 'flamegraph',
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  manualChunks: {}
})
