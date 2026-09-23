"""Automated browser checks. Usage: python3 tools/playtest.py <scenario>"""
import asyncio, sys, os, json, subprocess, time
from playwright.async_api import async_playwright
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = '/tmp/pt'
os.makedirs(OUT, exist_ok=True)
PORT = 4180

def serve():
    return subprocess.Popen([sys.executable, '-m', 'http.server', str(PORT)], cwd=os.path.join(ROOT, 'dist'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

class T:
    def __init__(self, page): self.p = page; self.n = 0
    async def shot(self, name):
        self.n += 1
        await self.p.locator('canvas').screenshot(path=f'{OUT}/{self.n:02d}_{name}.png')
    async def key(self, k, hold=90, after=120):
        await self.p.keyboard.down(k); await self.p.wait_for_timeout(hold); await self.p.keyboard.up(k); await self.p.wait_for_timeout(after)
    async def keys(self, seq, hold=90, after=120):
        for k in seq: await self.key(k, hold, after)
    async def js(self, code): return await self.p.evaluate(code)
    async def wait(self, ms): await self.p.wait_for_timeout(ms)
    async def mash(self, n=10, k='z', gap=250):
        for _ in range(n): await self.key(k, 60, gap)
    async def top(self): return await self.js('window.__tiamat.input.top()')

async def run(scenario):
    subprocess.run(['npx', 'vite', 'build', '--logLevel', 'error'], cwd=ROOT, check=True)
    for f in os.listdir(OUT): os.remove(os.path.join(OUT, f))
    srv = serve(); time.sleep(0.6)
    logs = []
    try:
        async with async_playwright() as pw:
            b = await pw.chromium.launch(args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
            page = await b.new_page(viewport={'width': 960, 'height': 540})
            page.on('console', lambda m: logs.append(f'{m.type}: {m.text}') if m.type in ('error', 'warning') else None)
            page.on('pageerror', lambda e: logs.append(f'PAGEERROR: {e}'))
            t = T(page)
            mod = __import__('scenarios', fromlist=[scenario])
            await getattr(mod, scenario)(t, PORT)
            await b.close()
    finally:
        srv.terminate()
    print('\n'.join(logs[:60]) or 'no errors')

if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(__file__))
    asyncio.run(run(sys.argv[1]))
