"""Draw the home-screen icon (a flag on a green, with a ball) and save the sizes the manifest needs.

Usage: python make_icons.py <output-dir>
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

S = 4            # supersample, then scale down for smooth edges
BASE = 512


def draw():
    im = Image.new("RGB", (BASE * S, BASE * S), "#2f6f3e")
    d = ImageDraw.Draw(im)
    sc = lambda *v: [x * S for x in v]
    d.ellipse(sc(92, 300, 420, 424), fill="#5fae6f")                 # the green
    d.ellipse(sc(238, 352, 282, 368), fill="#1d3d24")                # the cup
    d.rectangle(sc(254, 116, 264, 360), fill="#ffffff")              # flagstick
    d.polygon(sc(264, 120, 380, 168, 264, 216), fill="#e8402f")      # flag
    d.ellipse(sc(130, 336, 190, 396), fill="#ffffff")                # ball outline
    d.ellipse(sc(137, 343, 183, 389), fill="#ffd23f")                # ball
    return im


out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
big = draw()
for size in (512, 192, 180):
    big.resize((size, size), Image.LANCZOS).save(out / f"icon-{size}.png", optimize=True)
    print("wrote", out / f"icon-{size}.png")
