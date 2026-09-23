"""Rebuild every generated asset: characters, UI, Morphs, battle backgrounds, maps and the Reach Map.

    python tools/art/build_all.py
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
STEPS = [
    ['tools/art/build_chars.py'],
    ['tools/art/font.py'],
    ['tools/art/build_ui.py'],
    ['tools/art/build_mons.py'],
    ['tools/art/build_battlebg.py'],
    ['tools/worldgen.py'],
    ['tools/art/build_maps.py'],
    ['tools/art/build_regionmap.py'],
]

for step in STEPS:
    print('»', ' '.join(step))
    subprocess.run([sys.executable, *step], cwd=ROOT, check=True)
print('all assets rebuilt')
