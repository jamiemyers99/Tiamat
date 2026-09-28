// Tiamat rescue script. Older versions of the game named their code "index-<hash>.js"; a phone or browser whose
// offline copy still holds one of those old pages asks for this file. Instead of the old game it clears the
// offline copy and reloads, so the current version loads. (See tools/pwa/sw-template.js.)
(async () => {
  try { const regs = await navigator.serviceWorker.getRegistrations(); await Promise.all(regs.map((r) => r.unregister())); } catch (e) { /* none */ }
  try { const keys = await caches.keys(); await Promise.all(keys.map((k) => caches.delete(k))); } catch (e) { /* none */ }
  location.replace(location.pathname + '?fresh=' + Date.now());
})();
