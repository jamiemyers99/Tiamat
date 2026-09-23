import { defineConfig } from 'vite';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

// After each production build, write dist/sw.js: a service worker that caches every file of the
// game so the installed phone app works offline. Its version changes whenever any file changes.
function offlineCache() {
  return {
    name: 'tiamat-offline-cache',
    apply: 'build',
    closeBundle() {
      const dist = path.resolve('dist');
      const files = [];
      const walk = (dir) => {
        for (const f of fs.readdirSync(dir)) {
          const p = path.join(dir, f);
          if (fs.statSync(p).isDirectory()) { walk(p); } else { files.push(path.relative(dist, p).split(path.sep).join('/')); }
        }
      };
      walk(dist);
      const list = files.filter((f) => f !== 'sw.js' && f !== '.nojekyll').sort();
      const hash = crypto.createHash('sha1');
      for (const f of list) { hash.update(f); hash.update(fs.readFileSync(path.join(dist, f))); }
      const tpl = fs.readFileSync(path.resolve('tools/pwa/sw-template.js'), 'utf8');
      const sw = tpl.replace('__VERSION__', hash.digest('hex').slice(0, 12))
        .replace('__FILES__', JSON.stringify(['./', ...list.map((f) => `./${f}`)]));
      fs.writeFileSync(path.join(dist, 'sw.js'), sw);
    },
  };
}

export default defineConfig({
  base: './',
  plugins: [offlineCache()],
  build: {
    outDir: 'dist',
    assetsInlineLimit: 0,
    chunkSizeWarningLimit: 2000,
  },
  server: { port: 5173, open: false },
});
