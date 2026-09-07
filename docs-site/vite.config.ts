import { defineConfig } from 'vite'
import { dockit } from '@dreamlake/dockit/vite'
import { readFileSync } from 'node:fs'
const version = JSON.parse(readFileSync(new URL('./version.json', import.meta.url), 'utf8'))
export default defineConfig({plugins: [...dockit()], define: {
  __DOCS_VERSION__: JSON.stringify(version.version),
  __DOCS_BRANCH__: JSON.stringify(version.branch),
}, server: {host: '127.0.0.1', port: 3021}})
