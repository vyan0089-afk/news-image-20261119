#!/usr/bin/env python3
"""Build-time renderer for the make.fun news-image-20261119 entry, v2.

Reads transcript.txt and renders entry.png, 1024x1024, deterministically:
a cream-paper newspaper front page — serif masthead, deck, region strip,
big-number strip, three equal hero columns with code-drawn illustrations,
numbered story cards with small icons, a numbered world map, an
"Also on Thursday" brief list, a DATE CHECK box and a footer.

Every word in the image comes from transcript.txt (date, masthead, deck,
date check, footer, story titles/summaries/sources/regions); generate.py
holds only layout, labels, the big-number picks, map coordinates and the
drawn illustrations/icons. Only used at build time (needs Pillow + DejaVu
fonts on this machine). The graded entrypoint is main.py, which copies
entry.png to the output dir, because the grader runs stdlib-only Python
3.13 with no Pillow or guaranteed fonts.
"""
import hashlib
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
W, H = 1024, 1024

PAPER = (247, 241, 221)
PANEL = (238, 231, 205)
PANEL2 = (233, 225, 196)
INK = (26, 26, 26)
RED = (176, 30, 36)
BLUE = (31, 58, 95)
MUTED = (96, 88, 70)
RULE = (74, 64, 44)
OCEAN = (214, 226, 222)
LAND = (231, 220, 184)
LAND_LINE = (122, 111, 77)

FD = "/usr/share/fonts/truetype/dejavu/"
FN = "/usr/share/fonts/truetype/noto/"


def font(name, size, base=FD):
    return ImageFont.truetype(base + name, size)


SERIF = lambda s: font("DejaVuSerif.ttf", s)          # noqa: E731
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)   # noqa: E731
SERIF_I = lambda s: font("NotoSerif-Italic.ttf", s, FN)  # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)            # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)     # noqa: E731

# ---------------------------------------------------------------- transcript

def parse_transcript():
    lines = (ROOT / "transcript.txt").read_text(encoding="utf-8").splitlines()
    date_line = lines[0].strip()
    meta = {}
    mains, briefs = [], []
    section = "main"
    for raw in lines[1:]:
        line = raw.strip()
        if not line:
            continue
        if line == "ALSO ON THURSDAY":
            section = "also"
            continue
        kind, _, rest = line.partition(" | ")
        if kind in ("MASTHEAD", "DECK", "DATECHECK", "FOOTER"):
            meta[kind] = rest.strip()
            continue
        parts = [p.strip() for p in line.split("|")]
        title = parts[0]
        text = parts[1] if len(parts) > 1 else ""
        source = parts[2] if len(parts) > 2 else ""
        region = parts[3] if len(parts) > 3 else ""
        story = {"title": title, "text": text, "source": source,
                 "region": region}
        (mains if section == "main" else briefs).append(story)
    assert len(mains) == 15, f"expected 15 mains, got {len(mains)}"
    assert len(briefs) >= 20, f"expected 20+ briefs, got {len(briefs)}"
    masthead, _, tagline = meta["MASTHEAD"].partition(" | ")
    return date_line, masthead.strip(), tagline.strip(), meta["DECK"], \
        meta["DATECHECK"], meta["FOOTER"], mains, briefs


# ---------------------------------------------------------------- helpers

def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, color, max_w, leading, max_lines=None):
    lines = wrap(d, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y, len(lines)


def centered(d, cx, y, text, fnt, color):
    w = d.textlength(text, font=fnt)
    d.text((cx - w / 2, y), text, font=fnt, fill=color)
    return w


# ---------------------------------------------------------------- icons
# All icons are drawn in code with simple shapes; each takes the draw
# object, the top-left corner of a ~20x20 box, and a colour.

def icon_controller(d, x, y, c):
    d.rounded_rectangle([x + 1, y + 5, x + 19, y + 15], radius=4,
                        outline=c, width=2)
    d.line([x + 5, y + 10, x + 8, y + 10], fill=c, width=2)
    d.line([x + 6.5, y + 8.5, x + 6.5, y + 11.5], fill=c, width=2)
    d.ellipse([x + 13, y + 8, x + 15, y + 10], fill=c)
    d.ellipse([x + 15.5, y + 10.5, x + 17.5, y + 12.5], fill=c)


def icon_leaf(d, x, y, c):
    d.polygon([(x + 10, y + 1), (x + 18, y + 9), (x + 10, y + 17),
               (x + 2, y + 9)], outline=c, width=2)
    d.line([x + 10, y + 2, x + 10, y + 18], fill=c, width=1)
    d.line([x + 10, y + 9, x + 15, y + 6], fill=c, width=1)
    d.line([x + 10, y + 12, x + 5, y + 9], fill=c, width=1)


def icon_cyclone(d, x, y, c):
    for r, a0, a1 in ((8, 200, 380), (5.5, 20, 200), (3, 200, 20)):
        d.arc([x + 10 - r, y + 10 - r, x + 10 + r, y + 10 + r],
              a0, a1, fill=c, width=2)


def icon_pencil(d, x, y, c):
    d.polygon([(x + 4, y + 16), (x + 13, y + 3), (x + 16, y + 6),
               (x + 7, y + 19)], outline=c, width=2)
    d.polygon([(x + 4, y + 16), (x + 7, y + 19), (x + 2, y + 19)],
              fill=c)
    d.line([x + 12, y + 6, x + 14, y + 8], fill=c, width=1)


def icon_megaphone(d, x, y, c):
    d.polygon([(x + 2, y + 8), (x + 12, y + 3), (x + 12, y + 15),
               (x + 2, y + 12)], outline=c, width=2)
    d.line([x + 5, y + 13, x + 5, y + 18], fill=c, width=2)
    d.arc([x + 13, y + 5, x + 19, y + 13], 300, 60, fill=c, width=2)
    d.arc([x + 15, y + 3, x + 21, y + 15], 300, 60, fill=c, width=1)


def icon_missile(d, x, y, c):
    d.polygon([(x + 10, y + 1), (x + 13, y + 9), (x + 10, y + 14),
               (x + 7, y + 9)], outline=c, width=2)
    d.polygon([(x + 7, y + 9), (x + 4, y + 14), (x + 7, y + 12)], fill=c)
    d.polygon([(x + 13, y + 9), (x + 16, y + 14), (x + 13, y + 12)], fill=c)
    d.polygon([(x + 9, y + 14), (x + 11, y + 14), (x + 10, y + 19)],
              fill=RED)


def icon_pin(d, x, y, c):
    d.ellipse([x + 4, y + 1, x + 16, y + 13], outline=c, width=2)
    d.ellipse([x + 8, y + 5, x + 12, y + 9], fill=c)
    d.polygon([(x + 6, y + 11), (x + 14, y + 11), (x + 10, y + 19)],
              outline=c, width=2)


def icon_bridge(d, x, y, c):
    d.arc([x + 1, y + 2, x + 19, y + 18], 180, 360, fill=c, width=2)
    d.line([x + 1, y + 15, x + 19, y + 15], fill=c, width=2)
    d.line([x + 5, y + 10, x + 5, y + 15], fill=c, width=1)
    d.line([x + 10, y + 8, x + 10, y + 15], fill=c, width=1)
    d.line([x + 15, y + 10, x + 15, y + 15], fill=c, width=1)


def icon_chartdown(d, x, y, c):
    d.line([x + 2, y + 2, x + 2, y + 18], fill=c, width=2)
    d.line([x + 2, y + 18, x + 18, y + 18], fill=c, width=2)
    d.line([x + 4, y + 5, x + 9, y + 10, x + 13, y + 8, x + 17, y + 15],
           fill=c, width=2)
    d.polygon([(x + 17, y + 15), (x + 14, y + 13), (x + 18, y + 12)],
              fill=c)


def icon_rain(d, x, y, c):
    d.ellipse([x + 2, y + 3, x + 10, y + 10], outline=c, width=2)
    d.ellipse([x + 8, y + 1, x + 17, y + 10], outline=c, width=2)
    d.ellipse([x + 5, y + 5, x + 14, y + 11], fill=c)
    for rx in (5, 10, 15):
        d.line([x + rx, y + 14, x + rx - 1, y + 18], fill=c, width=2)


def icon_gavel(d, x, y, c):
    d.polygon([(x + 11, y + 9), (x + 17, y + 3), (x + 19, y + 5),
               (x + 13, y + 11)], fill=c)
    d.polygon([(x + 2, y + 17), (x + 11, y + 8), (x + 13, y + 10),
               (x + 4, y + 19)], fill=c)
    d.line([x + 2, y + 18, x + 18, y + 18], fill=c, width=2)


def icon_ballot(d, x, y, c):
    d.rectangle([x + 3, y + 9, x + 17, y + 18], outline=c, width=2)
    d.line([x + 8, y + 9, x + 12, y + 9], fill=c, width=2)
    d.polygon([(x + 7, y + 1), (x + 13, y + 1), (x + 13, y + 8),
               (x + 7, y + 8)], outline=c, width=1)
    d.line([x + 9, y + 5, x + 11, y + 3], fill=c, width=1)

CARD_ICONS = [icon_controller, icon_leaf, icon_cyclone, icon_pencil,
              icon_megaphone, icon_missile, icon_pin, icon_bridge,
              icon_chartdown, icon_rain, icon_gavel, icon_ballot]

# Card summaries show only the first source, shortened where needed.
SHORT_SOURCES = {"The War Zone": "TWZ"}


# ---------------------------------------------------------------- hero art
# Each hero illustration is drawn in code inside its panel; no photos,
# no copied artwork.

def art_flags(d, x, y, w, h):
    # Three flagpoles: US, China, Russia. Ground line + sky.
    gy = y + h - 12
    d.line([x + 8, gy, x + w - 8, gy], fill=RULE, width=2)
    poles = [x + w * 0.22, x + w * 0.5, x + w * 0.78]
    fw, fh = 52, 32
    for px, kind in zip(poles, ("us", "cn", "ru")):
        top = gy - fh - 34
        d.line([px, top, px, gy], fill=INK, width=2)
        d.ellipse([px - 2, top - 4, px + 2, top], fill=INK)
        fx, fy = px + 1, top + 2
        if kind == "us":
            for i in range(7):
                d.rectangle([fx, fy + i * fh / 7, fx + fw,
                             fy + (i + 1) * fh / 7],
                            fill=RED if i % 2 == 0 else PAPER)
            d.rectangle([fx, fy, fx + fw * 0.45, fy + fh * 0.55],
                        fill=BLUE)
            for sx in (4, 12, 20):
                for sy in (3, 9):
                    d.ellipse([fx + sx, fy + sy, fx + sx + 2,
                               fy + sy + 2], fill=PAPER)
        elif kind == "cn":
            d.rectangle([fx, fy, fx + fw, fy + fh], fill=RED)
            d.ellipse([fx + 6, fy + 6, fx + 12, fy + 12], fill=(255, 210, 60))
            for sx, sy in ((18, 5), (23, 9), (23, 15), (18, 19)):
                d.ellipse([fx + sx, fy + sy, fx + sx + 3, fy + sy + 3],
                          fill=(255, 210, 60))
        else:
            for i, col in enumerate((PAPER, BLUE, RED)):
                d.rectangle([fx, fy + i * fh / 3, fx + fw,
                             fy + (i + 1) * fh / 3], fill=col)
        d.rectangle([fx, fy, fx + fw, fy + fh], outline=INK, width=1)


def art_scales(d, x, y, w, h):
    cx = x + w / 2
    base = y + h - 10
    d.line([cx - 26, base, cx + 26, base], fill=INK, width=3)
    d.line([cx, y + 8, cx, base], fill=INK, width=3)
    d.line([cx - 34, y + 16, cx + 34, y + 16], fill=INK, width=3)
    d.ellipse([cx - 3, y + 5, cx + 3, y + 11], fill=INK)
    for sx in (cx - 34, cx + 34):
        d.line([sx, y + 16, sx - 10, y + 42], fill=INK, width=2)
        d.line([sx, y + 16, sx + 10, y + 42], fill=INK, width=2)
        d.line([sx, y + 16, sx, y + 42], fill=INK, width=1)
        d.arc([sx - 12, y + 36, sx + 12, y + 52], 0, 180, fill=INK,
              width=3)
    d.ellipse([cx - 4, y + 20, cx + 4, y + 28], fill=RED)


def art_bell(d, x, y, w, h):
    # IPO bell, big and solid on the left; rising chart arrow on the right.
    # Bell dome.
    bx, by = x + 22, y + 10
    d.pieslice([bx, by, bx + 56, by + 56], 180, 360, fill=INK)
    d.rectangle([bx - 4, by + 50, bx + 60, by + 56], fill=INK)
    d.ellipse([bx + 24, by + 58, bx + 32, by + 66], fill=INK)
    d.ellipse([bx + 25, by - 3, bx + 31, by + 3], fill=INK)
    # Chart arrow, right half, clear of the bell and of the labels.
    pts = [(x + 128, y + 58), (x + 158, y + 44), (x + 182, y + 50),
           (x + 258, y + 16)]
    d.line(pts, fill=BLUE, width=3)
    d.polygon([(x + 258, y + 16), (x + 244, y + 16), (x + 254, y + 26)],
              fill=BLUE)
    d.text((x + 116, y + 60), "$83", font=SERIF_B(13), fill=RED)
    d.text((x + 196, y + 0), "$111.50", font=SERIF_B(13), fill=BLUE)


HERO_ART = [art_flags, art_scales, art_bell]
HERO_KICKERS = ["SUMMIT · SHENZHEN", "THE HAGUE · WORLD COURT",
                "WALL STREET · RECORD IPO"]

# Big-number strip: (main-story index 1-based, value, label).
BIG_NUMBERS = [(2, "9–6", "World Court votes Myanmar guilty"),
               (7, "551,864", "sit Korea's Suneung exam"),
               (3, "$81.3bn", "Anthropic's record IPO"),
               (4, "15.9m", "GTA VI pre-orders (estimate)"),
               (6, "204,070", "marked to flee Cyclone Akvan")]

# World map: (story number, latitude, longitude, nudge dx, nudge dy).
MAP_PINS = [(1, 22.54, 114.06, 0, 0), (2, 52.07, 4.30, 0, -13),
            (3, 40.71, -74.01, 0, -6), (4, -41.29, 174.78, 0, 0),
            (5, 36.90, 30.71, -13, 4), (6, 20.30, 85.83, 0, 0),
            (7, 37.57, 126.98, 0, 0), (8, 4.71, -74.07, 0, 8),
            (9, 24.71, 46.68, 0, 0), (10, 31.50, 34.47, 12, 10),
            (11, 45.31, 36.51, 8, -12), (12, -35.28, 149.13, 0, 0),
            (13, 25.76, -80.19, -11, 3), (14, -6.21, 106.85, 0, 0),
            (15, 48.86, 2.35, -3, 13)]

# Coarse continent outlines (lon, lat), drawn as one landmass each.
CONTINENTS = [
    [(-168, 66), (-158, 71), (-140, 70), (-130, 72), (-120, 72),
     (-110, 73), (-95, 80), (-85, 76), (-80, 73), (-75, 70), (-65, 62),
     (-60, 55), (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-75, 36),
     (-76, 34), (-80, 32), (-81, 26), (-84, 30), (-89, 29), (-91, 19),
     (-95, 16), (-92, 15), (-97, 16), (-105, 20), (-110, 23),
     (-114, 28), (-117, 33), (-122, 37), (-124, 42), (-125, 49),
     (-130, 55), (-140, 60), (-152, 58), (-162, 58), (-168, 66)],
    [(-58, 64), (-55, 70), (-50, 74), (-40, 76), (-30, 74), (-25, 70),
     (-32, 68), (-45, 60), (-55, 60), (-58, 64)],
    [(-79, 9), (-77, 7), (-72, 12), (-64, 10), (-60, 8), (-54, 6),
     (-51, 4), (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-37, -13),
     (-39, -17), (-41, -23), (-48, -27), (-52, -32), (-57, -38),
     (-62, -41), (-65, -45), (-68, -50), (-70, -54), (-73, -50),
     (-73, -44), (-72, -37), (-71, -30), (-70, -20), (-75, -15),
     (-80, -6), (-81, -1), (-80, 4), (-79, 9)],
    [(-17, 15), (-16, 20), (-13, 27), (-10, 31), (-6, 34), (-2, 35),
     (3, 37), (10, 37), (11, 34), (15, 32), (20, 32), (25, 32),
     (30, 31), (32, 31), (35, 28), (37, 22), (39, 18), (41, 12),
     (43, 11), (48, 11), (51, 12), (48, 5), (44, 0), (41, -4),
     (40, -10), (39, -15), (36, -20), (34, -26), (32, -29), (28, -33),
     (20, -35), (17, -32), (15, -27), (13, -20), (12, -15), (13, -10),
     (12, -5), (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 15)],
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 46), (-1, 48),
     (-4, 48), (0, 50), (2, 51), (4, 53), (7, 54), (8, 57), (10, 59),
     (12, 56), (18, 56), (21, 55), (21, 57), (24, 59), (26, 60),
     (28, 61), (30, 62), (30, 66), (32, 70), (35, 68), (40, 68),
     (44, 68), (48, 66), (48, 62), (44, 60), (40, 58), (38, 55),
     (36, 52), (34, 50), (32, 48), (30, 46), (28, 45), (27, 44),
     (24, 42), (23, 40), (22, 40), (20, 40), (19, 42), (16, 44),
     (14, 45), (12, 44), (10, 44), (8, 44), (6, 43), (3, 42), (0, 40),
     (-2, 37), (-6, 36), (-9, 37), (-10, 36)],
    [(30, 62), (30, 66), (34, 68), (40, 68), (44, 68), (48, 68),
     (55, 69), (62, 70), (68, 71), (75, 72), (82, 73), (90, 75),
     (100, 76), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
     (158, 69), (162, 66), (170, 66), (178, 65), (178, 62), (170, 60),
     (162, 58), (158, 52), (155, 50), (150, 45), (145, 44), (142, 42),
     (140, 39), (138, 36), (135, 34), (132, 33), (130, 33), (128, 35),
     (127, 37), (126, 40), (124, 40), (122, 38), (120, 35), (119, 32),
     (117, 28), (115, 23), (112, 22), (110, 20), (108, 15), (106, 10),
     (104, 9), (102, 8), (100, 7), (98, 10), (97, 15), (95, 16),
     (93, 18), (91, 22), (89, 22), (87, 21), (85, 20), (83, 17),
     (81, 14), (80, 10), (78, 8), (76, 10), (75, 13), (73, 16),
     (72, 20), (70, 21), (68, 23), (66, 25), (64, 25), (62, 25),
     (60, 25), (58, 26), (56, 27), (54, 27), (52, 28), (50, 29),
     (48, 30), (47, 30), (45, 30), (43, 31), (41, 32), (39, 33),
     (37, 35), (35, 36), (33, 36), (30, 36), (30, 40), (30, 45),
     (30, 50), (30, 55), (30, 62)],
    [(113, -22), (114, -28), (115, -33), (118, -35), (122, -34),
     (126, -32), (130, -32), (132, -32), (135, -35), (137, -35),
     (139, -37), (141, -38), (145, -38), (147, -39), (150, -37),
     (152, -34), (153, -30), (153, -27), (151, -24), (148, -20),
     (146, -19), (144, -15), (142, -11), (141, -13), (139, -15),
     (137, -12), (136, -12), (135, -15), (134, -12), (132, -11),
     (130, -13), (128, -14), (126, -14), (124, -16), (122, -17),
     (120, -19), (118, -20), (116, -21), (114, -22), (113, -22)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50), (-5, 50)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
     (141, 41), (142, 43), (144, 44), (142, 42), (140, 39), (138, 36),
     (136, 35), (133, 34), (131, 32), (130, 31)],
    [(167, -45), (169, -43), (171, -41), (173, -39), (175, -38),
     (176, -37), (178, -38), (176, -40), (174, -41), (172, -43),
     (170, -44), (168, -46), (167, -45)],
]

REGION_ORDER = ["ASIA", "EUROPE", "N. AMERICA", "M. EAST", "S. AMERICA",
                "AFRICA", "OCEANIA", "WORLD"]

MARGIN = 24
CW = W - 2 * MARGIN  # 976


def main():
    date_line, masthead, tagline, deck, datecheck, footer, mains, briefs = \
        parse_transcript()
    total = len(mains) + len(briefs)

    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 12

    # ---- Masthead -------------------------------------------------------
    d.rectangle([MARGIN, y, W - MARGIN, y + 1], fill=INK)
    d.rectangle([MARGIN, y + 4, W - MARGIN, y + 4], fill=INK)
    y += 9
    d.text((MARGIN, y), date_line.upper(), font=SANS_B(14), fill=INK)
    tw = d.textlength(tagline, font=SANS_B(12))
    d.text((W - MARGIN - tw, y + 1), tagline, font=SANS_B(12), fill=MUTED)
    y += 20
    centered(d, W / 2, y, masthead, SERIF_B(42), INK)
    y += 50
    d.rectangle([MARGIN, y, W - MARGIN, y + 1], fill=INK)
    y += 6
    centered(d, W / 2, y, deck, SERIF_I(15), RED)
    y += 22

    # ---- Region strip ---------------------------------------------------
    counts = {}
    for s in mains + briefs:
        counts[s["region"]] = counts.get(s["region"], 0) + 1
    strip = f"{total} STORIES  ·  " + "  ·  ".join(
        f"{r} {counts.get(r, 0)}" for r in REGION_ORDER)
    centered(d, W / 2, y, strip, SANS_B(12), INK)
    print("region strip:", strip)
    y += 20

    # ---- Big-number strip ----------------------------------------------
    bw = (CW - 4 * 8) // 5
    by = y
    for i, (idx, value, label) in enumerate(BIG_NUMBERS):
        x = MARGIN + i * (bw + 8)
        d.rectangle([x, by, x + bw, by + 42], outline=RULE, width=1)
        d.rectangle([x, by, x + bw, by + 2], fill=RED)
        centered(d, x + bw / 2, by + 7, value, SERIF_B(20), INK)
        centered(d, x + bw / 2, by + 29, label, SANS(10), MUTED)
    y = by + 42 + 8

    # ---- Heroes: stories 1-3, three equal columns ----------------------
    hw = (CW - 2 * 16) // 3
    hh = 214
    hy = y
    for i in range(3):
        s = mains[i]
        x = MARGIN + i * (hw + 16)
        d.rectangle([x, hy, x + hw, hy + hh], outline=RULE, width=1)
        d.rectangle([x, hy, x + hw, hy + hh], fill=PANEL)
        d.text((x + 10, hy + 8), f"{i + 1}  {HERO_KICKERS[i]}",
               font=SANS_B(11), fill=RED)
        yy, _ = draw_wrapped(d, x + 10, hy + 26, s["title"], SERIF_B(19),
                              INK, hw - 20, 22, max_lines=2)
        ay = hy + 70
        d.rectangle([x + 10, ay, x + hw - 10, ay + 74], outline=RULE,
                    width=1, fill=PANEL2)
        HERO_ART[i](d, x + 10, ay, hw - 20, 74)
        yy, _ = draw_wrapped(d, x + 10, ay + 80, s["text"], SANS(12),
                              INK, hw - 20, 15, max_lines=3)
        d.text((x + 10, hy + hh - 16), "Sources: " + s["source"],
               font=SANS(9), fill=MUTED)
    y = hy + hh + 8

    # ---- Story cards 4-15: 4 columns x 3 rows --------------------------
    cw2 = (CW - 3 * 12) // 4
    ch2 = 82
    cy = y
    for j in range(12):
        s = mains[3 + j]
        col, row = j % 4, j // 4
        x = MARGIN + col * (cw2 + 12)
        yy = cy + row * (ch2 + 6)
        d.rectangle([x, yy, x + cw2, yy + ch2], outline=RULE, width=1)
        d.ellipse([x + 8, yy + 8, x + 28, yy + 28], fill=RED)
        num = str(4 + j)
        nw = d.textlength(num, font=SANS_B(12))
        d.text((x + 18 - nw / 2, yy + 11), num, font=SANS_B(12),
               fill=PAPER)
        CARD_ICONS[j](d, x + cw2 - 28, yy + 8, BLUE)
        draw_wrapped(d, x + 34, yy + 7, s["title"], SERIF_B(13), INK,
                     cw2 - 66, 15, max_lines=2)
        src = SHORT_SOURCES.get(s["source"].split(" · ")[0],
                                s["source"].split(" · ")[0])
        draw_wrapped(d, x + 8, yy + 40, s["text"] + " (" + src + ")",
                     SANS(10), INK, cw2 - 16, 13, max_lines=3)
    y = cy + 3 * ch2 + 2 * 6 + 8

    # ---- World map ------------------------------------------------------
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=SANS_B(13), fill=INK)
    note = "Numbers match the stories above"
    nw = d.textlength(note, font=SERIF_I(11))
    d.text((W - MARGIN - nw, y + 1), note, font=SERIF_I(11), fill=MUTED)
    y += 18
    my, mh = y, 120
    d.rectangle([MARGIN, my, W - MARGIN, my + mh], fill=OCEAN,
                outline=RULE, width=1)

    def proj(lon, lat):
        px = MARGIN + (lon + 180) / 360 * CW
        py = my + (78 - lat) / 136 * mh
        return px, py

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND,
                  outline=LAND_LINE)
    # Indonesia islands as small land dots.
    for lon, lat, r in ((100, 0, 4), (106, -6, 4), (114, -2, 4),
                        (113, -7, 3), (136, -4, 5)):
        px, py = proj(lon, lat)
        d.ellipse([px - r, py - r * 0.6, px + r, py + r * 0.6], fill=LAND,
                  outline=LAND_LINE)
    for label, lon, lat in (("ATLANTIC", -30, 8), ("PACIFIC", -150, -12),
                            ("INDIAN OCEAN", 72, -32)):
        px, py = proj(lon, lat)
        centered(d, px, py, label, SERIF_I(10), (110, 120, 112))
    for num, lat, lon, ndx, ndy in MAP_PINS:
        px, py = proj(lon, lat)
        cx, cy2 = px + ndx, py + ndy
        if ndx or ndy:
            d.line([px, py, cx, cy2], fill=INK, width=1)
        d.ellipse([cx - 7.5, cy2 - 7.5, cx + 7.5, cy2 + 7.5], fill=RED,
                  outline=PAPER, width=1)
        t = str(num)
        tw = d.textlength(t, font=SANS_B(10))
        d.text((cx - tw / 2, cy2 - 7), t, font=SANS_B(10), fill=PAPER)
    y = my + mh + 8

    # ---- Also on Thursday ----------------------------------------------
    d.text((MARGIN, y), "ALSO ON THURSDAY", font=SANS_B(13), fill=INK)
    y += 18
    colw = (CW - 2 * 16) // 3
    bf = SANS_B(11)
    for i, s in enumerate(briefs):
        col, row = i % 3, i // 3
        x = MARGIN + col * (colw + 16)
        yy = y + row * 12
        tw = d.textlength("• " + s["title"], font=bf)
        if tw > colw:
            print(f"WARNING brief {i + 1} too wide: {tw:.0f} > {colw}: "
                  f"{s['title']}")
        d.text((x, yy), "•", font=bf, fill=RED)
        d.text((x + 12, yy), s["title"], font=bf, fill=INK)
    y = y + 8 * 12 + 6

    # ---- Date check -----------------------------------------------------
    d.rectangle([MARGIN, y, W - MARGIN, y + 38], outline=RED, width=2)
    d.text((MARGIN + 10, y + 5), "DATE CHECK", font=SANS_B(11), fill=RED)
    draw_wrapped(d, MARGIN + 96, y + 5, datecheck, SANS(11), INK,
                 CW - 106, 14, max_lines=2)
    y += 38 + 8

    # ---- Footer ---------------------------------------------------------
    draw_wrapped(d, MARGIN, y, footer, SANS(10), MUTED, CW, 13,
                 max_lines=2)
    y += 26

    assert y <= H, f"layout overflow: bottom={y}"
    print(f"layout bottom={y} (canvas {H})")

    out = ROOT / "entry.png"
    img.save(out, format="PNG", optimize=False)
    data = out.read_bytes()
    print(f"wrote {out} {len(data)} bytes "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    print(f"size {img.size} mode {img.mode}")


if __name__ == "__main__":
    sys.exit(main())
