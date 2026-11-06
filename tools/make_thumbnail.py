#!/usr/bin/env python3
"""Draws mod/thumbnail.png (512x512): dark backdrop, crimson medallion with a gold
ring and hourglass, EB Garamond title. Uses EB Garamond (OFL) from a Paradox game install
(CK3 doesn't ship it, so it's taken from Victoria 3)."""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

GAME = os.path.expanduser(
    os.environ.get("VIC3_DIR", "~/.local/share/Steam/steamapps/common/Victoria 3"))
FONTS = os.path.join(GAME, "game/fonts/EBGaramond")
OUT = os.path.join(os.path.dirname(__file__), "..", "mod", "thumbnail.png")

S = 4  # supersampling factor
W = 512 * S
GOLD = (214, 178, 112)
GOLD_LIGHT = (240, 214, 160)


def backdrop():
    img = Image.new("RGB", (W, W))
    d = ImageDraw.Draw(img)
    # Radial-ish vignette: lighter in the middle
    for r in range(W, 0, -8 * S):
        t = r / W
        c = int(14 + 26 * (1 - t))
        d.ellipse([W / 2 - r, W * 0.42 - r, W / 2 + r, W * 0.42 + r], fill=(c, c + 1, c + 2))
    return img.filter(ImageFilter.GaussianBlur(20 * S))


def medallion(img):
    cx, cy, r = W / 2, 206 * S, 128 * S
    # Shadow
    shadow = Image.new("L", (W, W), 0)
    ImageDraw.Draw(shadow).ellipse([cx - r, cy - r + 8 * S, cx + r, cy + r + 8 * S], fill=170)
    shadow = shadow.filter(ImageFilter.GaussianBlur(14 * S))
    img.paste((0, 0, 0), mask=shadow)

    # Green face with horizontal brushed streaks
    face = Image.new("RGB", (W, W), (96, 26, 30))
    fd = ImageDraw.Draw(face)
    rng = random.Random(7)
    for _ in range(900):
        y = rng.uniform(cy - r, cy + r)
        x = rng.uniform(cx - r, cx + r)
        length = rng.uniform(20, 120) * S
        shade = rng.randint(-14, 14)
        fd.line([x, y, x + length, y + rng.uniform(-2, 2) * S],
                fill=(96 + shade, 26 + shade, 30 + shade), width=rng.randint(1, 3) * S)
    face = face.filter(ImageFilter.GaussianBlur(1.5 * S))
    mask = Image.new("L", (W, W), 0)
    ImageDraw.Draw(mask).ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    img.paste(face, mask=mask)

    d = ImageDraw.Draw(img)
    # Inner shading ring and gold rim
    d.ellipse([cx - r + 8 * S, cy - r + 8 * S, cx + r - 8 * S, cy + r - 8 * S],
              outline=(60, 14, 18), width=6 * S)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=7 * S)
    d.ellipse([cx - r - 3 * S, cy - r - 3 * S, cx + r + 3 * S, cy + r + 3 * S],
              outline=(120, 92, 48), width=2 * S)
    return cx, cy


def hourglass(img, cx, cy):
    d = ImageDraw.Draw(img)
    lw = 8 * S
    w, h = 54 * S, 70 * S  # half width, half height
    top, bot = cy - h, cy + h
    # Plates
    for y in (top, bot):
        d.rounded_rectangle([cx - w - 8 * S, y - 7 * S, cx + w + 8 * S, y + 7 * S], radius=4 * S, fill=GOLD)
    # Glass: two triangles meeting at the neck
    for sx in (-1, 1):
        d.line([cx + sx * w, top, cx + sx * 6 * S, cy], fill=GOLD, width=lw)
        d.line([cx + sx * 6 * S, cy, cx + sx * w, bot], fill=GOLD, width=lw)
    # Sand: the same shape in both bulbs, mirrored about the neck, nearly filling each
    inset = lw / 2 + 5 * S
    def edge(y):  # glass half-width at y, minus the inset
        return 6 * S + (w - 6 * S) * abs(y - cy) / h - inset
    y_far, y_near = 16 * S, 11 * S  # distance from the plates / the neck, as offsets from cy
    for sign in (-1, 1):
        ya = cy + sign * (h - y_far)   # far edge of the sand (flat)
        yb = cy + sign * y_near        # near edge, at the neck
        d.polygon([cx - edge(ya), ya, cx + edge(ya), ya, cx + edge(yb), yb, cx - edge(yb), yb], fill=GOLD_LIGHT)


def text(img):
    d = ImageDraw.Draw(img)
    title = ImageFont.truetype(os.path.join(FONTS, "EBGaramond-Medium.ttf"), 84 * S)
    tag = ImageFont.truetype(os.path.join(FONTS, "EBGaramond-Italic.ttf"), 27 * S)
    d.text((W / 2, 410 * S), "Date Stop", font=title, fill=(232, 210, 160), anchor="ms")
    d.text((W / 2, 470 * S), "Pause when your chosen date arrives", font=tag,
           fill=(222, 200, 152), anchor="ms")


def main():
    if not os.path.isdir(FONTS):
        sys.exit(f"EB Garamond not found in {FONTS}; set VIC3_DIR to the game install")
    img = backdrop()
    cx, cy = medallion(img)
    hourglass(img, cx, cy)
    text(img)
    img.resize((512, 512), Image.LANCZOS).save(OUT)
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
