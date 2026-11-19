#!/usr/bin/env python3
"""Build-time renderer for the make.fun news-image-20261119 entry.

Reads transcript.txt (first line = date, then one story per line as
"TITLE | one-line summary", in importance order) and renders entry.png,
1024x1024, deterministically. Every word in the image comes from the
transcript; no other text, no logos, no network, no external assets.
Only used at build time (needs Pillow + DejaVu fonts on this machine).
The graded entrypoint is main.py, which copies entry.png to the output
dir, because the grader runs stdlib-only Python 3.13 with no Pillow or
guaranteed fonts.
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1024, 1024

NAVY = (10, 17, 32)
NAVY2 = (16, 28, 52)
CARD = (22, 38, 68)
GOLD = (255, 190, 60)
CYAN = (96, 205, 255)
WHITE = (255, 255, 255)
MUTED = (203, 213, 230)
LINE = (56, 82, 128)

FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, color, max_w, leading):
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def main():
    transcript = (ROOT / "transcript.txt").read_text(encoding="utf-8").splitlines()
    date_line = transcript[0].strip()
    stories = []
    for line in transcript[1:]:
        line = line.strip()
        if not line:
            continue
        title, _, summary = line.partition(" | ")
        stories.append((title.strip(), summary.strip()))
    assert stories, "no stories in transcript"

    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # Deterministic background: subtle vertical bands, no randomness.
    for i in range(0, W, 64):
        shade = 10 + (i // 64) % 2
        d.rectangle([i, 0, i + 31, H], fill=(shade, 17 + (i // 64) % 2, 32))
    # Header band
    d.rectangle([0, 0, W, 92], fill=NAVY2)
    d.rectangle([0, 92, W, 96], fill=GOLD)
    f_date = font(FONT_BOLD, 34)
    d.text((40, 28), date_line, font=f_date, fill=GOLD)

    # Hero story (stories[0])
    hero_title, hero_sum = stories[0]
    y = 118
    d.rectangle([40, y, 52, y + 140], fill=GOLD)
    y = draw_wrapped(d, 72, y, hero_title, font(FONT_BOLD, 52),
                     WHITE, W - 112, 60)
    y += 4
    y = draw_wrapped(d, 72, y + 4, hero_sum, font(FONT_REG, 24),
                     MUTED, W - 112, 31)
    hero_bottom = y + 14
    d.line([40, hero_bottom, W - 40, hero_bottom], fill=LINE, width=2)

    # Grid: stories 1..6 (2 columns x 3 rows). Summaries are clipped to
    # fit inside their card so nothing can overflow.
    grid = stories[1:7]
    gx0, gy0 = 40, hero_bottom + 18
    cw, ch = 462, 152
    gapx, gapy = 20, 14
    for i, (title, summary) in enumerate(grid):
        col, row = i % 2, i // 2
        x = gx0 + col * (cw + gapx)
        yy = gy0 + row * (ch + gapy)
        d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=10, fill=CARD)
        d.rectangle([x, yy, x + 6, yy + ch], fill=CYAN if col == 0 else GOLD)
        tf = font(FONT_BOLD, 24)
        sf = font(FONT_REG, 18)
        tlines = wrap(d, title, tf, cw - 36)[:2]
        ty = yy + 12
        for ln in tlines:
            d.text((x + 22, ty), ln, font=tf, fill=WHITE)
            ty += 29
        slines = wrap(d, summary, sf, cw - 36)
        max_s = max(1, (yy + ch - 10 - (ty + 4)) // 22)
        for ln in slines[:max_s]:
            d.text((x + 22, ty + 4), ln, font=sf, fill=MUTED)
            ty += 22
    grid_bottom = gy0 + 3 * ch + 2 * gapy

    # Bottom strip: remaining stories in a 2x2 compact grid.
    y = grid_bottom + 12
    d.line([40, y, W - 40, y], fill=LINE, width=2)
    y += 12
    rest = stories[7:]
    bcw, bch = 462, 88
    for i, (title, summary) in enumerate(rest):
        col, row = i % 2, i // 2
        x = gx0 + col * (bcw + gapx)
        yy = y + row * (bch + 10)
        d.ellipse([x + 4, yy + 6, x + 16, yy + 18], fill=GOLD)
        tf = font(FONT_BOLD, 20)
        sf = font(FONT_REG, 17)
        ty = yy
        for ln in wrap(d, title, tf, bcw - 36)[:1]:
            d.text((x + 28, ty), ln, font=tf, fill=WHITE)
            ty += 25
        for ln in wrap(d, summary, sf, bcw - 36)[:2]:
            d.text((x + 28, ty), ln, font=sf, fill=MUTED)
            ty += 21
    bottom = y + 2 * bch + 10
    assert bottom <= H - 10, f"layout overflow: bottom={bottom}"
    # Footer rule only (no extra text: all words are from the transcript)
    d.rectangle([0, H - 8, W, H], fill=GOLD)

    out = ROOT / "entry.png"
    img.save(out, format="PNG", optimize=False)
    data = out.read_bytes()
    print(f"wrote {out} {len(data)} bytes sha256={hashlib.sha256(data).hexdigest()}")
    print(f"size {img.size} mode {img.mode}")


if __name__ == "__main__":
    sys.exit(main())
