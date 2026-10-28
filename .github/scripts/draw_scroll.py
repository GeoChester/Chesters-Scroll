"""Draws scroll.png from finders.json. Run by the GitHub workflow."""
import json
import os
import sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONTS = os.path.join(ROOT, ".fonts")
S = 2                     # drawn at double size so it stays sharp
W = 600 * S

NIGHT = (46, 36, 67)
LEDGER = (58, 46, 82)
LINE = (92, 75, 120)
INK = (239, 230, 214)
MUTED = (181, 168, 196)
PUMPKIN = (242, 131, 43)
GLOW = (255, 194, 92)


def font(names, size, weight=None):
    for n in names:
        p = n if os.path.isabs(n) else os.path.join(FONTS, n)
        if os.path.exists(p) and os.path.getsize(p) > 0:
            try:
                f = ImageFont.truetype(p, size)
            except OSError:
                continue
            if weight:
                try:
                    f.set_variation_by_axes([weight])
                except Exception:
                    pass
            return f
    return ImageFont.load_default(size)


FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FALLBACK_I = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
title_f = font(["PirataOne.ttf", FALLBACK], 54 * S)
sub_f = font(["PirataOne.ttf", FALLBACK], 30 * S)
ftf_f = font(["PirataOne.ttf", FALLBACK], 25 * S)
eyebrow_f = font(["CrimsonPro.ttf", FALLBACK], 14 * S, 600)
note_f = font(["CrimsonPro.ttf", FALLBACK], 17 * S)
name_f = font(["CrimsonPro.ttf", FALLBACK], 19 * S)
empty_f = font(["CrimsonPro-Italic.ttf", FALLBACK_I], 18 * S)
foot_f = font(["CrimsonPro-Italic.ttf", FALLBACK_I], 20 * S)


def tw(d, text, f):
    b = d.textbbox((0, 0), text, font=f)
    return b[2] - b[0]


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if tw(d, t, f) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def main():
    try:
        with open(os.path.join(ROOT, "finders.json"), encoding="utf-8") as fh:
            data = json.load(fh)
        names = [str(n).strip() for n in data if str(n).strip()]
    except Exception as e:
        print("Could not read finders.json:", e)
        sys.exit(1)

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    pad, card_pad = 28 * S, 22 * S
    inner = W - 2 * pad - 2 * card_pad

    # lay out the name tags in rows
    chip_h, chip_px, gap = 38 * S, 16 * S, 9 * S
    chips = []
    for n in names[1:]:
        f = name_f
        while tw(probe, n, f) + 2 * chip_px > inner and f.size > 11 * S:
            f = f.font_variant(size=f.size - S)
        chips.append((n, f, min(inner, tw(probe, n, f) + 2 * chip_px)))
    rows, row, roww = [], [], 0
    for c in chips:
        need = c[2] + (gap if row else 0)
        if row and roww + need > inner:
            rows.append((row, roww))
            row, roww = [], 0
            need = c[2]
        row.append(c)
        roww += need
    if row:
        rows.append((row, roww))

    title_lines = wrap(probe, "Chester's Scroll of Honour", title_f, W - 2 * pad)
    sub_lines = wrap(probe, "They braved every trick and claimed every treat!", sub_f, inner)
    ftf_text = ("First to Find: ", names[0]) if names else None

    # heights
    y = 26 * S
    top_eyebrow = y
    y += 26 * S
    title_y = y
    y += len(title_lines) * 58 * S + 14 * S
    card_top = y
    cy = card_top + card_pad
    sub_y = cy
    cy += len(sub_lines) * 34 * S + 6 * S
    note_y = cy
    cy += 28 * S
    ftf_y = cy
    if ftf_text:
        cy += 62 * S
    rows_y = cy
    if rows:
        cy += len(rows) * chip_h + (len(rows) - 1) * gap + 4 * S
    elif not names:
        cy += 30 * S
    card_bottom = cy + card_pad - 6 * S
    foot_y = card_bottom + 20 * S
    H = foot_y + 46 * S

    img = Image.new("RGB", (W, H), NIGHT)
    # soft moon glow top right, ember glow at the bottom
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((W - 190 * S, -60 * S, W - 30 * S, 100 * S), fill=(120, 90, 40))
    g.ellipse((W * 0.15, H - 60 * S, W * 0.85, H + 160 * S), fill=(80, 40, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(60 * S))
    img = ImageChops.add(img, Image.eval(glow, lambda v: v // 2))
    d = ImageDraw.Draw(img)

    def center(text, f, yy, fill):
        d.text(((W - tw(d, text, f)) / 2, yy), text, font=f, fill=fill)

    # eyebrow
    eb = "CHESTER'S TRICKS AND TREATS"
    spaced = " ".join(eb)
    center(spaced, eyebrow_f, top_eyebrow, MUTED)
    # title with a warm glow behind it
    tl = Image.new("L", (W, H), 0)
    tdraw = ImageDraw.Draw(tl)
    for i, line in enumerate(title_lines):
        tdraw.text(((W - tw(d, line, title_f)) / 2, title_y + i * 58 * S), line, font=title_f, fill=255)
    halo = tl.filter(ImageFilter.GaussianBlur(10 * S))
    img.paste(Image.new("RGB", (W, H), PUMPKIN), (0, 0), Image.eval(halo, lambda v: int(v * 0.35)))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(title_lines):
        center(line, title_f, title_y + i * 58 * S, PUMPKIN)

    # card
    d.rounded_rectangle((pad, card_top, W - pad, card_bottom), radius=14 * S, fill=LEDGER, outline=LINE, width=S)
    for i, line in enumerate(sub_lines):
        center(line, sub_f, sub_y + i * 34 * S, GLOW)
    center("The scroll updates once a day.", note_f, note_y, MUTED)
    if ftf_text:
        a, b = ftf_text
        f = ftf_f
        while tw(d, a + b, f) > inner and f.size > 14 * S:
            f = f.font_variant(size=f.size - S)
        while tw(d, a + b, f) + 44 * S > inner and f.size > 14 * S:
            f = f.font_variant(size=f.size - S)
        tw_all = tw(d, a + b, f)
        bx0, bx1 = (W - tw_all) / 2 - 22 * S, (W + tw_all) / 2 + 22 * S
        by0, by1 = ftf_y, ftf_y + 50 * S
        # soft gold glow, then the framed box
        gl = Image.new("L", (W, H), 0)
        ImageDraw.Draw(gl).rounded_rectangle((bx0, by0, bx1, by1), radius=14 * S, outline=255, width=4 * S)
        gl = gl.filter(ImageFilter.GaussianBlur(9 * S))
        img.paste(Image.new("RGB", (W, H), GLOW), (0, 0), Image.eval(gl, lambda v: int(v * 0.3)))
        d = ImageDraw.Draw(img)
        d.rounded_rectangle((bx0, by0, bx1, by1), radius=14 * S, fill=(76, 62, 82), outline=GLOW, width=2 * S)
        tb = d.textbbox((0, 0), a + b, font=f)
        ty = by0 + (by1 - by0 - (tb[3] - tb[1])) / 2 - tb[1]
        x = (W - tw_all) / 2
        d.text((x, ty), a, font=f, fill=PUMPKIN)
        d.text((x + tw(d, a, f), ty), b, font=f, fill=GLOW)
    if rows:
        yy = rows_y
        for row, roww in rows:
            x = (W - roww) / 2
            for n, f, cw in row:
                d.rounded_rectangle((x, yy, x + cw, yy + chip_h), radius=chip_h // 2, fill=NIGHT, outline=LINE, width=S)
                b = d.textbbox((0, 0), n, font=f)
                d.text((x + (cw - (b[2] - b[0])) / 2 - b[0], yy + (chip_h - (b[3] - b[1])) / 2 - b[1]), n, font=f, fill=INK)
                x += cw + gap
            yy += chip_h + gap
    elif not names:
        center("No names on the scroll yet.", empty_f, rows_y, MUTED)

    # footer with a small pumpkin
    ft = "Happy haunting from Chester."
    fw = tw(d, ft, foot_f)
    pw = 30 * S
    fx = (W - fw - pw - 10 * S) / 2
    d.text((fx, foot_y), ft, font=foot_f, fill=MUTED)
    px, py = fx + fw + 10 * S, foot_y + 2 * S
    d.ellipse((px, py + 6 * S, px + 16 * S, py + 26 * S), fill=(232, 116, 31))
    d.ellipse((px + 14 * S, py + 6 * S, px + 30 * S, py + 26 * S), fill=(232, 116, 31))
    d.ellipse((px + 7 * S, py + 4 * S, px + 23 * S, py + 27 * S), fill=PUMPKIN)
    d.line((px + 15 * S, py + 5 * S, px + 18 * S, py), fill=(90, 138, 58), width=2 * S)

    img.save(os.path.join(ROOT, "scroll.png"), optimize=True)
    print("Drew scroll.png with", len(names), "name(s)")


if __name__ == "__main__":
    main()
