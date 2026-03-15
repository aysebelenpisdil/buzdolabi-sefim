import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
      server: {
        port: 3000,
        host: '127.0.0.1',
        strictPort: true,
        allowedHosts: true,
      },
      plugins: [react()],
      // test: {
      //   globals: true,
      //   environment: 'jsdom',
      //   setupFiles: ['./tests/setup.ts'],
      // },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
});
