"""Prepara las imagenes de la web a partir de las ilustraciones entregadas por el usuario (carpeta de origen indicada por --src). Uso: python tools/prep_images.py --src <carpeta con 2.webp 4.webp 6.webp 7.webp 8.webp>"""
import argparse, os
from PIL import Image

ap = argparse.ArgumentParser(); ap.add_argument('--src', required=True); a = ap.parse_args()
out = os.path.join(os.path.dirname(__file__), '..', 'assets', 'img'); os.makedirs(out, exist_ok=True)
def opn(n): return Image.open(os.path.join(a.src, n)).convert('RGBA')
def save(im, name, **kw):
    p = os.path.join(out, name); im.save(p, **kw); print(name, im.size, os.path.getsize(p) // 1024, 'KB')

# logotipo (con transparencia)
logo = opn('4.webp'); logo.thumbnail((1200, 600), Image.LANCZOS); save(logo, 'logo.webp', quality=90, method=6)
# escena de los dos espejos: solo la franja de los portales (y 10 %..62 % de la ilustracion)
bg = opn('6.webp'); w, h = bg.size; crop = bg.crop((0, int(h * 0.10), w, int(h * 0.62))).convert('RGB'); save(crop, 'portals.webp', quality=86, method=6)
# cubo y anillo
save(opn('7.webp'), 'cube.webp', quality=90, method=6)
ring = opn('8.webp'); ring.thumbnail((1200, 600), Image.LANCZOS); save(ring, 'ring.webp', quality=90, method=6)
# iconos de la app / favicon
ic = opn('2.webp').convert('RGB')
for s in (32, 180, 192, 512): save(ic.resize((s, s), Image.LANCZOS), f'icon-{s}.png')
# imagen para compartir en redes (1200x630)
og = Image.new('RGB', (1200, 630), (8, 8, 10))
for y in range(630):
    for x in range(0, 1200, 4):
        t = max(0.0, 1 - (((x - 600) ** 2 + (y - 300) ** 2) ** 0.5) / 700)
        og.paste((int(8 + 70 * t), int(8 + 6 * t), int(10 + 8 * t)), (x, y, x + 4, y + 1))
lg = opn('4.webp'); lg.thumbnail((980, 520), Image.LANCZOS)
og.paste(lg, ((1200 - lg.width) // 2, (630 - lg.height) // 2), lg)
save(og, 'og-image.png')
