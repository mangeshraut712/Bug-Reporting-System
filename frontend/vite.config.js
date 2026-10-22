import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';

// PUBLIC_URL keeps the same meaning it had under Create React App
// (e.g. "/Bug-Reporting-System/" for GitHub Pages, "/" for Netlify).
export default defineConfig({
  base: process.env.PUBLIC_URL || '/',
  plugins: [react(), tailwindcss()],
  envPrefix: ['VITE_', 'REACT_APP_'],
  server: { port: 3000 },
  preview: { port: 3000 },
  build: { outDir: 'build' },
  test: {
    environment: 'jsdom',
    setupFiles: './src/setupTests.js',
    css: true,
    restoreMocks: true,
    testTimeout: 20000,
  },
});
