import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import viteRawPlugin from "./vite/vite-raw-plugin.js";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    svelte({
      emitCss: false,
    }),
    viteRawPlugin({
      fileRegex: /\.navy$/,
    })
  ]
})