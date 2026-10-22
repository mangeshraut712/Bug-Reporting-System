import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// PUBLIC_URL keeps the same meaning it had under Create React App
// (e.g. "/Bug-Reporting-System/" for GitHub Pages, "/" for Netlify).
export default defineConfig({
  base: process.env.PUBLIC_URL || '/',
  plugins: [react()],
  envPrefix: ['VITE_', 'REACT_APP_'],
  server: { port: 3000 },
  preview: { port: 3000 },
  build: { outDir: 'build' },
});
