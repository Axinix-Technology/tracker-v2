import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc';
import tailwindcss from '@tailwindcss/vite';
import Pages from 'vite-plugin-pages';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    Pages(),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@api': path.resolve(__dirname, './src/api'),
      '@assets': path.resolve(__dirname, './src/assets'),
      '@components': path.resolve(__dirname, './src/components'),
      '@constants': path.resolve(__dirname, './src/constants'),
      '@context': path.resolve(__dirname, './src/context'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@layouts': path.resolve(__dirname, './src/layouts'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@platformAdmin': path.resolve(__dirname, './src/platformAdmin'),
      '@providers': path.resolve(__dirname, './src/providers'),
      '@services': path.resolve(__dirname, './src/services'),
      '@store': path.resolve(__dirname, './src/store'),
      '@styles': path.resolve(__dirname, './src/styles'),
      '@utilities': path.resolve(__dirname, './src/utilities'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@widgets': path.resolve(__dirname, './src/widgets'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/socket.io': {
        target: 'http://localhost:3000',
        ws: true,
        changeOrigin: true,
      }
    }
  },
  build: {
    sourcemap: false,
    chunkSizeWarningLimit: 600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            const normalized = id.replace(/\\/g, '/');
            if (normalized.includes('/react/') || normalized.includes('/react-dom/') || normalized.includes('/scheduler/')) {
              return 'vendor-react';
            }
            if (normalized.includes('/react-router/') || normalized.includes('/react-router-dom/')) {
              return 'vendor-router';
            }
            if (normalized.includes('/lucide-react/')) {
              return 'vendor-icons';
            }
            if (normalized.includes('/axios/') || normalized.includes('/js-cookie/') || normalized.includes('/jwt-decode/')) {
              return 'vendor-network';
            }
            if (normalized.includes('/country-state-city/')) {
              return 'vendor-geo';
            }
            if (normalized.includes('/xlsx/') || normalized.includes('/file-saver/')) {
              return 'vendor-excel';
            }
            if (normalized.includes('/react-quill-new/')) {
              return 'vendor-editor';
            }
            if (normalized.includes('/clsx/') || normalized.includes('/tailwind-merge/') || normalized.includes('/react-hot-toast/')) {
              return 'vendor-ui';
            }
          }
        },
      },
    },
  },
});
