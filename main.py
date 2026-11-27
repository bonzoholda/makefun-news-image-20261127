#!/usr/bin/env python3
"""Draw the front page of 27 November 2026 in one image.

Program: Python 3.13, standard library + Pillow only.
Writes a 1024x1024 PNG to /output/entry.png when /output exists
(the grader's target), otherwise to entry.png beside this file.
Fully deterministic: fixed colours, fixed geometry, no network,
no clocks, no randomness.
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (24, 24, 22)
RED = (178, 34, 28)
DARK = (32, 32, 34)
GREY = (96, 96, 92)
LIGHT_GREY = (210, 206, 196)
BLUE = (28, 68, 120)
GOLD = (196, 138, 30)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, max_w, fill=INK, leading=None):
    """Draw wrapped text; returns the y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_skyline(draw, box):
    """Drawn illustration for the lead story: a Gaza dusk skyline
    with smoke rising from damaged buildings. All shapes are fixed."""
    x0, y0, x1, y1 = box
    # Dusk sky: horizontal bands, deep amber at the horizon.
    bands = [
        ((58, 52, 74), 0.00),
        ((96, 62, 66), 0.28),
        ((168, 92, 58), 0.55),
        ((214, 138, 66), 0.78),
        ((232, 178, 96), 1.00),
    ]
    height = y1 - y0
    for i in range(height):
        t = i / max(1, height - 1)
        for j in range(len(bands) - 1):
            c0, t0 = bands[j]
            c1, t1 = bands[j + 1]
            if t0 <= t <= t1:
                f = (t - t0) / max(1e-6, t1 - t0)
                col = tuple(int(c0[k] + (c1[k] - c0[k]) * f) for k in range(3))
                break
        else:
            col = bands[-1][0]
        draw.line([(x0, y0 + i), (x1, y0 + i)], fill=col)
    # Low red sun.
    sun_cx, sun_cy, sun_r = x0 + 118, y0 + 128, 42
    draw.ellipse(
        [sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
        fill=(224, 84, 44),
    )
    # Distant skyline (dark, low).
    far = [(0, 210), (52, 210), (52, 168), (96, 168), (96, 200),
           (150, 200), (150, 150), (196, 150), (196, 210), (250, 210),
           (250, 176), (300, 176), (300, 210), (352, 210), (352, 158),
           (398, 158), (398, 210), (448, 210)]
    draw.polygon([(x0 + px, y0 + py) for px, py in far],
                 fill=(74, 58, 66))
    # Near skyline with two broken, smoking buildings.
    near = [(0, 300), (0, 218), (46, 218), (46, 196), (70, 196),
            (70, 232), (118, 232), (118, 176), (150, 176), (150, 150),
            (172, 150), (172, 210), (196, 210), (196, 246), (252, 246),
            (252, 190), (282, 190), (282, 224), (330, 224), (330, 172),
            (362, 172), (362, 246), (400, 246), (400, 206), (448, 206),
            (448, 300)]
    draw.polygon([(x0 + px, y0 + py) for px, py in near],
                 fill=(38, 32, 38))
    # Windows: small lit rectangles on the near buildings.
    for wx, wy in [(16, 232), (30, 232), (16, 252), (128, 192), (128, 212),
                   (262, 206), (340, 188), (340, 208), (410, 220),
                   (56, 210), (206, 258), (262, 226)]:
        draw.rectangle([x0 + wx, y0 + wy, x0 + wx + 7, y0 + wy + 9],
                       fill=(240, 196, 110))
    # Smoke columns rising from the two damaged buildings.
    for sx, sy, sr in [(163, 118, 26), (150, 82, 32), (138, 48, 38),
                       (347, 140, 22), (356, 106, 28), (366, 74, 33)]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr // 2,
                      x0 + sx + sr, y0 + sy + sr // 2],
                     fill=(120, 112, 108))
    for sx, sy, sr in [(158, 104, 14), (346, 122, 12)]:
        draw.ellipse([x0 + sx - sr, y0 + sy - sr // 2,
                      x0 + sx + sr, y0 + sy + sr // 2],
                     fill=(150, 142, 136))
    # Small flames at the base of the broken building.
    for fx in (150, 164, 178):
        draw.polygon([(x0 + fx, y0 + 246), (x0 + fx + 6, y0 + 224),
                      (x0 + fx + 12, y0 + 246)], fill=(232, 120, 40))
    # Ground line.
    draw.rectangle([x0, y1 - 6, x1, y1], fill=(30, 26, 30))


def draw_jet(draw, cx, cy, s, fill):
    """Simple fighter-jet silhouette, pointing up-right."""
    pts = [(cx - 26 * s, cy + 6 * s), (cx - 4 * s, cy - 2 * s),
           (cx + 22 * s, cy - 14 * s), (cx + 26 * s, cy - 12 * s),
           (cx + 8 * s, cy + 2 * s), (cx + 2 * s, cy + 10 * s),
           (cx - 6 * s, cy + 16 * s), (cx - 12 * s, cy + 8 * s),
           (cx - 20 * s, cy + 12 * s)]
    draw.polygon(pts, fill=fill)


def draw_no_entry(draw, cx, cy, r, fill):
    """Circle with a diagonal bar: a no-fly sign."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fill, width=6)
    draw.line([(cx - r + 6, cy + r - 6), (cx + r - 6, cy - r + 6)],
              fill=fill, width=6)


def draw_atom(draw, cx, cy, r, fill):
    """Atom: nucleus plus two elliptical orbits."""
    draw.ellipse([cx - r, cy - r // 3, cx + r, cy + r // 3],
                 outline=fill, width=4)
    draw.ellipse([cx - r // 3, cy - r, cx + r // 3, cy + r],
                 outline=fill, width=4)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=fill)


def draw_chart(draw, cx, cy, w, h, fill):
    """Rising bar chart with an arrow."""
    bars = [14, 22, 18, 30, 38]
    bw = w // len(bars)
    for i, bh in enumerate(bars):
        x = cx - w // 2 + i * bw + 2
        draw.rectangle([x, cy + h // 2 - bh, x + bw - 5, cy + h // 2],
                       fill=fill)
    draw.line([(cx - w // 2, cy - h // 2 + 6), (cx + w // 2, cy - h // 2 - 8)],
              fill=RED, width=5)
    draw.polygon([(cx + w // 2, cy - h // 2 - 8),
                  (cx + w // 2 - 12, cy - h // 2 - 8),
                  (cx + w // 2, cy - h // 2 + 4)], fill=RED)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---------- Masthead ----------
    d.rectangle([0, 0, W, 10], fill=INK)
    masthead = font(SERIF_B, 68)
    title = "THE WORLD TODAY"
    tw = d.textlength(title, font=masthead)
    d.text(((W - tw) / 2, 22), title, font=masthead, fill=INK)
    d.rectangle([28, 108, W - 28, 112], fill=INK)
    date_font = font(SANS_B, 30)
    date_line = "FRIDAY  27  NOVEMBER  2026"
    dw = d.textlength(date_line, font=date_font)
    d.text(((W - dw) / 2, 122), date_line, font=date_font, fill=RED)
    sub_font = font(SANS, 18)
    sub = "ONE DAY  \u00b7  ONE PAGE  \u00b7  THE WORLD'S NEWS"
    sw = d.textlength(sub, font=sub_font)
    d.text(((W - sw) / 2, 160), sub, font=sub_font, fill=GREY)
    d.rectangle([28, 190, W - 28, 194], fill=INK)

    # ---------- Lead story ----------
    lead_y0, lead_y1 = 208, 544
    d.rectangle([28, lead_y0, W - 28, lead_y1], outline=INK, width=3)
    d.rectangle([28, lead_y0, W - 28, lead_y0 + 4], fill=INK)
    ill_x0, ill_y0, ill_x1, ill_y1 = 34, 214, 482, 538
    draw_skyline(d, (ill_x0, ill_y0, ill_x1, ill_y1))
    cap_font = font(SANS, 15)
    d.text((ill_x0 + 8, ill_y1 - 24), "GAZA AT DUSK \u2014 DRAWN SCENE",
           font=cap_font, fill=(255, 255, 255))

    tx = 502
    kicker = font(SANS_B, 19)
    d.text((tx, 226), "MIDDLE EAST  \u2014  LEAD STORY",
           font=kicker, fill=RED)
    head = font(SERIF_B, 38)
    y = draw_text_block(d, tx, 254,
                        "Strikes kill 10 in Gaza\nas ceasefire frays",
                        head, 474, leading=44)
    body = font(SANS, 20)
    y = draw_text_block(
        d, tx, y + 10,
        "Israeli strikes and gunfire killed 10 Palestinians "
        "across Gaza, hospitals said, including a Hamas deputy "
        "minister and his wife in Deir al-Balah.",
        body, 474, leading=26)
    y = draw_text_block(
        d, tx, y + 8,
        "The year-old ceasefire has seen near-daily fire; "
        "the war's toll is above 74,700 dead.",
        body, 474, leading=26)

    # ---------- Secondary stories, 2 x 2 ----------
    cards = [
        ("UKRAINE", "Trump to Putin: \u201cpull back\u201d",
         "The US president urged Russia to end all military "
         "aggression in Europe. Zelensky warned a new mass "
         "Russian strike is being prepared.",
         "jet"),
        ("EUROPE", "Poland plans border no-fly zone",
         "Warsaw will seal airspace along its Ukraine border after "
         "Russian missiles and a drone crossed into Polish skies. "
         "NATO has not backed shooting them down.",
         "noentry"),
        ("ASIA", "Kim vows more nuclear weapons",
         "North Korea's leader toured uranium plants and ordered "
         "tactical nuclear arms deployed more widely, calling its "
         "nuclear status \u201cirreversible\u201d.",
         "atom"),
        ("ECONOMY", "Seoul raises rates to 3.25%",
         "South Korea's central bank lifted its key rate to a "
         "two-year high as a chip-export boom keeps growth hot "
         "and inflation above target.",
         "chart"),
    ]
    grid_y0 = 558
    card_w, card_h = 476, 158
    gap = 16
    for i, (tag, head_text, body_text, icon) in enumerate(cards):
        cx = 28 + (i % 2) * (card_w + gap)
        cy = grid_y0 + (i // 2) * (card_h + gap)
        d.rectangle([cx, cy, cx + card_w, cy + card_h],
                    outline=INK, width=2)
        d.rectangle([cx, cy, cx + card_w, cy + 30], fill=DARK)
        tag_f = font(SANS_B, 16)
        d.text((cx + 12, cy + 6), tag, font=tag_f, fill=(255, 255, 255))
        # Icon in the top-right of the dark strip.
        ix, iy = cx + card_w - 34, cy + 15
        if icon == "jet":
            draw_jet(d, ix, iy, 0.55, (240, 196, 110))
        elif icon == "noentry":
            draw_no_entry(d, ix, iy, 10, (240, 196, 110))
        elif icon == "atom":
            draw_atom(d, ix, iy, 11, (240, 196, 110))
        else:
            draw_chart(d, ix, iy + 6, 26, 12, (240, 196, 110))
        hf = font(SERIF_B, 24)
        y = draw_text_block(d, cx + 12, cy + 40, head_text, hf, 452,
                            leading=27)
        bf = font(SANS, 17)
        draw_text_block(d, cx + 12, y + 2, body_text, bf, 452, leading=21)

    # ---------- Also today strip ----------
    strip_y0 = 898
    d.rectangle([28, strip_y0, W - 28, strip_y0 + 46], fill=DARK)
    strip_f = font(SANS_B, 15)
    tick = ("ALSO TODAY \u2014 Black Friday opens at dawn \u00b7 "
            "Ebola in Congo tops 12,000 \u00b7 IAEA seeks a "
            "Zaporizhzhia ceasefire")
    tw2 = d.textlength(tick, font=strip_f)
    d.text(((W - tw2) / 2, strip_y0 + 12), tick, font=strip_f,
           fill=(255, 255, 255))

    # ---------- Footer ----------
    foot_f = font(SANS, 15)
    foot = ("Sources: Associated Press \u00b7 Reuters \u00b7 CNN \u00b7 Al Jazeera "
            "\u00b7 Kyiv Independent")
    fw = d.textlength(foot, font=foot_f)
    d.text(((W - fw) / 2, 958), foot, font=foot_f, fill=GREY)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        target = os.path.join(out_dir, "entry.png")
    elif os.path.isdir("/output"):
        target = "/output/entry.png"
    else:
        target = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "entry.png")
    os.makedirs(os.path.dirname(target) or ".", exist_ok=True)
    img.save(target, format="PNG", optimize=True)
    print("wrote", target, img.size)


if __name__ == "__main__":
    sys.exit(main())
