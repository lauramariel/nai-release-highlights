import { defineConfig } from 'astro/config';

import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  output: "hybrid",

  build: {
    format: 'directory',
  },

  vite: {
    build: {
      rollupOptions: {
        external: ['/pagefind/pagefind-ui.js'],
      },
    },
  },

  adapter: cloudflare()
});