#!/usr/bin/env python3
"""Draw THE DAILY WORLD front page for Wednesday 25 November 2026.

Renders entry.png (1024x1024, deterministic) from 18 web-verified headlines.
Run: python3 draw.py  -> writes entry.png next to this file.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")
W = H = 1024
MARGIN = 30

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",
    "/usr/share/fonts/truetype/liberation",
]


def font(name, size):
    for d in FONT_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    raise FileNotFoundError(f"font {name} not found in {FONT_DIRS}")


SERIF_B = "DejaVuSerif-Bold.ttf"
SANS_B = "DejaVuSans-Bold.ttf"
SANS = "DejaVuSans.ttf"
SANS_I = "LiberationSans-Italic.ttf"

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PAPER = (252, 252, 248)
RED = (139, 0, 0)
DARK = (40, 40, 40)
GREY = (110, 110, 110)
RULE = (180, 180, 180)

DATE_LINE = "WEDNESDAY, 25 NOVEMBER 2026"

# (kicker, headline) — all 18 web-verified for 25 Nov 2026.
LEAD = ("WORLD", "LEAKED DATA: NEARLY 500,000 RUSSIAN WAR DEAD")
LEAD_DECK = "Leaked Rosstat figures put confirmed deaths near half a million \u2014 BBC, 25 Nov 2026"

GRID = [
    ("WORLD", [
        "COP31 collapses in Antalya",
        "Zelenskiy confirms Gulf of Finland ship strike",
        "Ukraine sank Russian corvette off Benghazi",
        "Putin vows retaliation for refinery strikes",
        "Ukrainian drones hit Syzran, Samara refineries; one killed",
        "Trump awards Giuliani the Medal of Freedom",
        "Colombia rescues all hostages in Cartagena siege",
        "Bangladesh raises garment wage 36% after protests",
        "China investigates Shanghai party chief Chen Jining",
        "NATO space defence / Russian nuclear satellite",
    ]),
    ("MIDEAST", [
        "Houthis hit Riyadh's tallest tower, 11 wounded",
        "Houthis strike Saudi refinery, Riyadh financial district",
        "Israeli strike kills Hamas security chief Naim Abu Nahl",
        "Three tankers hit mines in Strait of Hormuz",
    ]),
    ("TECH", [
        "Huawei guilty of trade-secret theft, cleared of racketeering",
        "Shenzhou-24 launches with first Pakistani astronaut",
    ]),
    ("SPORT", [
        "Bellingham stunner, Real Madrid past PSV",
    ]),
]

# Columns: left = first 9 WORLD items; right = last WORLD item + the rest.
def grid_columns():
    left = [("header", "WORLD")] + [("item", h) for h in GRID[0][1][:9]]
    right = [("header", "WORLD"), ("item", GRID[0][1][9])]
    for name, items in GRID[1:]:
        right.append(("header", name))
        right += [("item", h) for h in items]
    return left, right

PHOTO_CAPTION = "A tanker burns in the Gulf after mine strikes \u2014 25 NOV 2026"
FOOTER = ("Every headline above was reported on Wednesday 25 November 2026. "
          "THE DAILY WORLD \u2014 one day's news, in one picture.")


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_halftone_tanker(box):
    """Draw a halftone-style tanker scene inside box (x0,y0,x1,y1)."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    scene = Image.new("L", (w, h), 235)
    sd = ImageDraw.Draw(scene)
    # Sky: pale gradient bands.
    for yy in range(0, int(h * 0.55)):
        v = 235 - int(35 * yy / max(1, int(h * 0.55)))
        sd.line([(0, yy), (w, yy)], fill=v)
    # Sun glare top-right.
    sd.ellipse([w - 150, 8, w - 70, 88], fill=250)
    # Sea: dark band.
    sd.rectangle([0, int(h * 0.55), w, h], fill=70)
    for yy in range(int(h * 0.55), h):
        v = 70 + int(25 * (yy - h * 0.55) / max(1, h * 0.45))
        sd.line([(0, yy), (w, yy)], fill=v)
    # Smoke plume rising from the tanker.
    rng = random.Random(42)
    cx = int(w * 0.62)
    for i in range(14):
        r = 12 + i * 4
        sx = cx + rng.randint(-18, 18) - i * 3
        sy = int(h * 0.52) - i * 9
        sd.ellipse([sx - r, sy - r, sx + r, sy + r], fill=150)
    # Tanker: hull + deck + funnel.
    hull_y = int(h * 0.62)
    sd.polygon([(int(w * 0.08), hull_y), (int(w * 0.92), hull_y),
                (int(w * 0.86), int(h * 0.82)), (int(w * 0.14), int(h * 0.82))],
               fill=25)
    sd.rectangle([int(w * 0.55), int(h * 0.44), int(w * 0.78), hull_y], fill=45)
    sd.rectangle([int(w * 0.60), int(h * 0.38), int(w * 0.70), int(h * 0.44)], fill=60)
    sd.rectangle([int(w * 0.20), int(h * 0.50), int(w * 0.30), hull_y], fill=45)
    # Flame licks on deck.
    for i, fx in enumerate([0.30, 0.36, 0.44, 0.50]):
        fx0 = int(w * fx)
        sd.polygon([(fx0 - 12, hull_y), (fx0, hull_y - 34 - (i % 2) * 10),
                    (fx0 + 12, hull_y)], fill=200)
    # Halftone: sample scene brightness, draw dots on white.
    panel = Image.new("RGB", (w, h), WHITE)
    pd = ImageDraw.Draw(panel)
    step = 7
    for yy in range(0, h, step):
        for xx in range(0, w, step):
            lum = scene.getpixel((min(xx, w - 1), min(yy, h - 1)))
            r = (1.0 - lum / 255.0) * 3.4
            if r > 0.4:
                pd.ellipse([xx - r, yy - r, xx + r, yy + r], fill=BLACK)
    # Frame the panel.
    pd.rectangle([0, 0, w - 1, h - 1], outline=BLACK, width=2)
    return panel


def measure_grid(draw, head_size, col_w):
    """Return total grid height for a headline font size."""
    hf = font(SANS_B, head_size)
    lh = head_size + 4
    heights = []
    for col in grid_columns():
        y = 0
        for kind, text in col:
            if kind == "header":
                y += 22
            else:
                y += len(wrap(draw, text, hf, col_w)) * lh + 6
        heights.append(y)
    return max(heights)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # Outer border.
    d.rectangle([10, 10, W - 11, H - 11], outline=BLACK, width=3)
    d.rectangle([16, 16, W - 17, H - 17], outline=RULE, width=1)

    y = 26
    # Masthead.
    mf = font(SERIF_B, 62)
    d.text((W // 2, y), "THE DAILY WORLD", font=mf, fill=BLACK, anchor="ma")
    y += 78
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=BLACK, width=3)
    y += 10
    # Date banner: black full-width band, white 40pt text.
    d.rectangle([MARGIN, y, W - MARGIN, y + 56], fill=BLACK)
    bf = font(SANS_B, 38)
    d.text((W // 2, y + 28), DATE_LINE, font=bf, fill=WHITE, anchor="mm")
    y += 56 + 12

    # Lead story.
    kf = font(SANS_B, 18)
    d.text((W // 2, y), LEAD[0], font=kf, fill=RED, anchor="ma")
    y += 24
    lf = font(SANS_B, 40)
    lead_lines = wrap(d, LEAD[1], lf, W - 2 * MARGIN - 20)
    assert len(lead_lines) <= 2, f"lead wraps to {len(lead_lines)} lines"
    for line in lead_lines:
        d.text((W // 2, y), line, font=lf, fill=BLACK, anchor="ma")
        y += 46
    df = font(SANS_I, 17)
    d.text((W // 2, y), LEAD_DECK, font=df, fill=DARK, anchor="ma")
    y += 26

    # Photo panel (height auto-fit with the grid below).
    head_size = 21
    photo_h = 170
    while True:
        grid_h = measure_grid(d, head_size, (W - 2 * MARGIN - 20) // 2)
        total = y + photo_h + 26 + grid_h + 12 + 40 + 24
        if total <= H or (head_size <= 18 and photo_h <= 120):
            break
        if head_size > 18:
            head_size -= 1
        else:
            photo_h -= 10
    panel = draw_halftone_tanker((0, 0, W - 2 * MARGIN, photo_h))
    img.paste(panel, (MARGIN, y))
    y += photo_h + 6
    cf = font(SANS_I, 16)
    d.text((W // 2, y), PHOTO_CAPTION, font=cf, fill=DARK, anchor="ma")
    y += 26

    # Headlines grid, two columns with section headers.
    hf = font(SANS_B, head_size)
    sf = font(SANS_B, 15)
    lh = head_size + 4
    col_w = (W - 2 * MARGIN - 20) // 2
    for ci, col in enumerate(grid_columns()):
        x = MARGIN + ci * (col_w + 20)
        cy = y
        for kind, text in col:
            if kind == "header":
                d.text((x, cy), text, font=sf, fill=RED, anchor="la")
                d.line([(x, cy + 18), (x + col_w, cy + 18)], fill=RED, width=2)
                cy += 22
            else:
                for line in wrap(d, text, hf, col_w):
                    d.text((x, cy), line, font=hf, fill=BLACK, anchor="la")
                    cy += lh
                cy += 6
                d.line([(x, cy - 3), (x + col_w, cy - 3)], fill=RULE, width=1)
    y += grid_h

    # Footer.
    y += 12
    d.line([(MARGIN, y), (W - MARGIN, y)], fill=BLACK, width=2)
    y += 8
    ff = font(SANS, 15)
    foot_lines = wrap(d, FOOTER, ff, W - 2 * MARGIN - 20)
    for line in foot_lines:
        d.text((W // 2, y), line, font=ff, fill=DARK, anchor="ma")
        y += 19
    assert y <= H - 18, f"layout overflow: y={y}"

    img.save(OUT, "PNG", optimize=True)
    size = os.path.getsize(OUT)
    assert img.size == (1024, 1024), img.size
    assert size <= 1048576, f"entry.png {size} bytes > 1 MiB"
    print(f"wrote {OUT} {size} bytes headline_font={head_size} photo_h={photo_h} bottom_y={y}")


if __name__ == "__main__":
    build()
