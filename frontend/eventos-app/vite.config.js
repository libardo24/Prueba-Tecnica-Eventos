import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import vuetify from 'vite-plugin-vuetify'; // Importa el plugin
import path from 'path';

export default defineConfig({
  plugins: [
    vue(),
    vuetify({ autoImport: true }), // Añade el plugin de Vuetify
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/tests/setup.js',
    css: true, // Habilita el soporte para CSS
    server: {
      deps: {
        inline: ['vuetify'], // Para Vuetify 3
      },
    },
    coverage: {
      provider: 'c8',
      all: true,
      include: ['src/**/*.{js,vue}'],
      exclude: ['**/node_modules/**', '**/tests/**'],
      reporter: ['text', 'json', 'html'],
    },
  },
});