"""Genera assets/img/og-image.png (1200x630): logo de MultiSpace sobre degradado negro-granate."""
from PIL import Image
import pathlib
root = pathlib.Path(__file__).resolve().parent.parent
W, H = 1200, 630
bg = Image.new("RGB", (W, H), (8, 8, 10))
px = bg.load()
for y in range(H):
    for x in range(W):
        t = max(0.0, min(1.0, (x / W * 0.7 + y / H * 0.3 - 0.35) / 0.8))
        px[x, y] = (int(8 + t * 120), int(8 + t * 4), int(10 + t * 12))
logo = Image.open(root / "assets/img/logo.webp").convert("RGBA")
lw = 900
lh = int(logo.height * lw / logo.width)
logo = logo.resize((lw, lh), Image.LANCZOS)
bg = bg.convert("RGBA")
bg.alpha_composite(logo, ((W - lw) // 2, (H - lh) // 2))
bg.convert("RGB").save(root / "assets/img/og-image.png", optimize=True)
print("og ok")
