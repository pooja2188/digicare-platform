import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite'; // ✅ Load the v4 plugin configuration

// https://vitejs.dev
export default defineConfig({
  plugins: [
    react(),
    tailwindcss() // ✅ Run the design engine inside your React project
  ],
  server: {
    port: 5173
  }
});
