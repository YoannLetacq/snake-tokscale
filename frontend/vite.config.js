import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import { parse } from 'smol-toml'

const __dirname = dirname(fileURLToPath(import.meta.url))
const configPath = resolve(__dirname, '..', 'config.toml')
const rootConfig = parse(readFileSync(configPath, 'utf8'))

export default defineConfig({
  base: './',
  plugins: [react(), tailwindcss()],
  define: {
    __GAME_CONFIG__: JSON.stringify(rootConfig.game ?? {}),
    __GRID_CONFIG__: JSON.stringify(rootConfig.grid ?? {}),
    __TOKSCALE_USERNAME__: JSON.stringify(rootConfig.tokscale?.username ?? ''),
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.js'],
  },
})
