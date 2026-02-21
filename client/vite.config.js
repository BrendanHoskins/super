import { defineConfig, transformWithEsbuild } from 'vite';
import react from '@vitejs/plugin-react';

// Import-analysis parses source before any transform runs. So we pre-transform
// .js files that contain JSX into plain JS so parsing succeeds. No .js → .jsx renames needed.
function jsAsJsx() {
  return {
    name: 'js-as-jsx',
    enforce: 'pre',
    async transform(code, id) {
      if (!/\.js$/.test(id) || id.includes('node_modules')) return null;
      const result = await transformWithEsbuild(code, id, {
        loader: 'jsx',
        jsx: 'automatic',
      });
      return { code: result.code, map: result.map };
    },
  };
}

export default defineConfig({
  plugins: [
    jsAsJsx(),
    react({ include: /\.(jsx|js|tsx|ts)$/ }),
  ],
  optimizeDeps: {
    esbuildOptions: {
      loader: { '.js': 'jsx' },
    },
  },
  server: {
    port: parseInt(process.env.PORT || '3000', 10),
    host: true,
  },
});
