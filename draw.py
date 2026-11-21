#!/usr/bin/env python3
"""Render the passport spread for the invented Republic of Velmora.

Draws a 1024x1024 open-passport spread with PIL only: a data page with a
stylised drawn portrait and a real-format MRZ (check digits computed with
the standard 7-3-1 weighting), and a visa page with six consistent stamps
(all dated after the passport's issue date) plus one telling paperwork
detail: the folk-song visa condition.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"

def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)

F_BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)
F_REG = lambda s: font("DejaVuSans.ttf", s)
F_MONO = lambda s: font("DejaVuSansMono.ttf", s)
F_SERIF_IT = lambda s: font("DejaVuSerif.ttf", s)
F_SERIF = lambda s: font("DejaVuSerif.ttf", s)

# ---------------------------------------------------------------- MRZ
MRZ_WEIGHTS = (7, 3, 1)

def mrz_value(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10 ... Z=35

def mrz_check(text):
    total = 0
    for i, ch in enumerate(text):
        total += mrz_value(ch) * MRZ_WEIGHTS[i % 3]
    return str(total % 10)

def build_mrz():
    line1 = "P<VELILSEN<<MARA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "VM482916<"
    doc_c = mrz_check(doc)
    dob = "960608"
    dob_c = mrz_check(dob)
    exp = "340312"
    exp_c = mrz_check(exp)
    pers = "<" * 14
    pers_c = mrz_check(pers)
    composite_src = doc + doc_c + dob + dob_c + exp + exp_c + pers + pers_c
    comp_c = mrz_check(composite_src)
    line2 = doc + doc_c + "VEL" + dob + dob_c + "F" + exp + exp_c + pers + pers_c + comp_c
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2

# ---------------------------------------------------------------- portrait
def draw_portrait(img, x, y, w, h):
    """Stylised flat portrait of the holder: dark-haired woman, three-quarter
    view, drawn from simple shapes on its own layer so nothing spills past
    the portrait box. No photo, no copied face."""
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    bg = (176, 196, 205)
    draw.rectangle([0, 0, w, h], fill=bg, outline=(90, 110, 120), width=2)
    # faint guilloche arcs behind the head, clipped to the box
    cx, cy = w // 2, h // 2 - 10
    for r in range(30, 120, 14):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=(150, 172, 182))
    skin = (232, 184, 138)
    skin_shadow = (214, 164, 118)
    hair = (58, 38, 28)
    jacket = (38, 74, 84)
    # shoulders / jacket
    draw.pieslice([8, h - 78, w - 8, h + 40], 180, 360, fill=jacket)
    draw.rectangle([cx - 16, h - 52, cx + 16, h], fill=(240, 238, 228))
    # neck
    draw.rectangle([cx - 13, cy + 42, cx + 13, cy + 72], fill=skin_shadow)
    # head
    draw.ellipse([cx - 34, cy - 46, cx + 34, cy + 48], fill=skin)
    # hair: cap + side locks
    draw.pieslice([cx - 38, cy - 52, cx + 38, cy + 6], 180, 360, fill=hair)
    draw.rectangle([cx - 38, cy - 14, cx - 26, cy + 34], fill=hair)
    draw.rectangle([cx + 26, cy - 14, cx + 38, cy + 34], fill=hair)
    draw.ellipse([cx - 38, cy - 52, cx + 38, cy - 6], fill=hair)
    # face: brow, eyes, nose, mouth
    draw.line([cx - 22, cy - 8, cx - 8, cy - 10], fill=(70, 45, 30), width=2)
    draw.line([cx + 8, cy - 10, cx + 22, cy - 8], fill=(70, 45, 30), width=2)
    draw.ellipse([cx - 20, cy - 4, cx - 12, cy + 2], fill=(40, 26, 18))
    draw.ellipse([cx + 12, cy - 4, cx + 20, cy + 2], fill=(40, 26, 18))
    draw.line([cx + 1, cy + 4, cx - 2, cy + 20], fill=skin_shadow, width=2)
    draw.line([cx - 2, cy + 20, cx + 6, cy + 22], fill=skin_shadow, width=2)
    draw.arc([cx - 9, cy + 28, cx + 9, cy + 38], 0, 180, fill=(150, 70, 60), width=2)
    # jacket lapels
    draw.polygon([(cx - 16, h - 52), (cx, h - 18), (cx - 30, h - 6)], fill=(28, 58, 66))
    draw.polygon([(cx + 16, h - 52), (cx, h - 18), (cx + 30, h - 6)], fill=(28, 58, 66))
    img.paste(layer, (x, y), layer)

# ---------------------------------------------------------------- stamps
def make_stamp(lines, ink, angle, box_w=250, box_h=92):
    """A rotated rectangular border-control stamp on its own RGBA layer."""
    layer = Image.new("RGBA", (box_w + 60, box_h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = 30, 30
    d.rounded_rectangle([ox, oy, ox + box_w, oy + box_h], radius=10,
                        outline=ink + (230,), width=3)
    d.rounded_rectangle([ox + 6, oy + 6, ox + box_w - 6, oy + box_h - 6], radius=7,
                        outline=ink + (200,), width=1)
    y = oy + 10
    for i, (text, f) in enumerate(lines):
        tw = d.textlength(text, font=f)
        d.text((ox + (box_w - tw) / 2, y), text, font=f, fill=ink + (235,))
        y += f.size + 2
    return layer.rotate(angle, expand=True, resample=Image.BICUBIC)

def make_oval_stamp(lines, ink, angle, w=240, h=110):
    layer = Image.new("RGBA", (w + 60, h + 60), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ox, oy = 30, 30
    d.ellipse([ox, oy, ox + w, oy + h], outline=ink + (230,), width=3)
    d.ellipse([ox + 6, oy + 6, ox + w - 6, oy + h - 6], outline=ink + (200,), width=1)
    y = oy + 16
    for text, f in lines:
        tw = d.textlength(text, font=f)
        d.text((ox + (w - tw) / 2, y), text, font=f, fill=ink + (235,))
        y += f.size + 2
    return layer.rotate(angle, expand=True, resample=Image.BICUBIC)

# ---------------------------------------------------------------- pages
def draw_data_page(img, px, py, pw, ph):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([px, py, px + pw, py + ph], fill=(245, 241, 230, 255),
                outline=(120, 110, 90, 255), width=2)
    d.rectangle([px + 8, py + 8, px + pw - 8, py + ph - 8],
                outline=(150, 140, 115, 255), width=1)
    cx = px + pw // 2
    # emblem: mountain + star
    ex, ey = cx - 14, py + 18
    d.polygon([(ex, ey + 26), (ex + 14, ey), (ex + 28, ey + 26)], outline=(90, 60, 30), width=2)
    d.polygon([(ex + 14, ey + 26), (ex + 22, ey + 12), (ex + 30, ey + 26)], fill=(90, 60, 30))
    d.text((cx + 26, py + 22), "*", font=F_BOLD(22), fill=(90, 60, 30))
    d.text((cx - 108, py + 52), "REPUBLIC OF VELMORA", font=F_BOLD(19), fill=(30, 30, 30))
    d.text((cx - 52, py + 76), "PASSPORT", font=F_BOLD(15), fill=(60, 60, 60))
    d.text((cx - 56, py + 94), "PASSEPORT", font=F_REG(11), fill=(100, 100, 100))
    d.line([px + 24, py + 118, px + pw - 24, py + 118], fill=(120, 110, 90), width=1)
    # portrait
    draw_portrait(img, px + 24, py + 136, 150, 196)
    d.text((px + 24, py + 338), "PHOTOGRAPH", font=F_REG(9), fill=(110, 110, 110))
    # data fields, right of portrait
    fx = px + 196
    fields = [
        ("Type", "P", "Code", "VEL", None, None),
        ("Passport No.", "VM 482 916", None, None, None, None),
        ("Surname", "ILSEN", None, None, None, None),
        ("Given names", "MARA", None, None, None, None),
        ("Nationality", "VELMORAN", "Sex", "F", None, None),
        ("Date of birth", "08 JUN 1996", None, None, None, None),
        ("Place of birth", "DRENVAR", None, None, None, None),
        ("Date of issue", "12 MAR 2024", None, None, None, None),
        ("Date of expiry", "12 MAR 2034", None, None, None, None),
        ("Authority", "MINISTRY OF PASSPORTS", None, None, None, None),
        ("", "DRENVAR", None, None, None, None),
    ]
    y = py + 136
    for label, value, l2, v2, l3, v3 in fields:
        d.text((fx, y), label.upper(), font=F_REG(10), fill=(110, 100, 80))
        d.text((fx, y + 13), value, font=F_BOLD(15), fill=(20, 20, 20))
        if l2:
            d.text((fx + 150, y), l2.upper(), font=F_REG(10), fill=(110, 100, 80))
            d.text((fx + 150, y + 13), v2, font=F_BOLD(15), fill=(20, 20, 20))
        if l3:
            d.text((fx + 218, y), l3.upper(), font=F_REG(10), fill=(110, 100, 80))
            d.text((fx + 218, y + 13), v3, font=F_BOLD(15), fill=(20, 20, 20))
        y += 34 if label else 30
    # signature
    d.text((px + 24, py + 560), "Mara Ilsen", font=F_SERIF_IT(24), fill=(30, 40, 90))
    d.line([px + 24, py + 592, px + 200, py + 592], fill=(120, 110, 90), width=1)
    d.text((px + 24, py + 598), "Signature of holder", font=F_REG(10), fill=(110, 100, 80))
    # holder's mark: fingerprint-ish whorl
    for r in range(4, 26, 6):
        d.arc([px + 330, py + 556, px + 330 + 2 * r, py + 556 + 2 * r], 0, 300,
              fill=(90, 90, 110), width=1)
    d.text((px + 330, py + 598), "Right thumb", font=F_REG(10), fill=(110, 100, 80))
    # MRZ
    line1, line2 = build_mrz()
    d.rectangle([px + 16, py + 640, px + pw - 16, py + 700], fill=(232, 228, 216))
    d.text((px + 24, py + 648), line1, font=F_MONO(15), fill=(20, 20, 20))
    d.text((px + 24, py + 670), line2, font=F_MONO(15), fill=(20, 20, 20))
    d.text((px + pw - 44, py + 716), "8", font=F_REG(11), fill=(110, 100, 80))

def draw_visa_page(img, px, py, pw, ph):
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([px, py, px + pw, py + ph], fill=(245, 241, 230, 255),
                outline=(120, 110, 90, 255), width=2)
    d.rectangle([px + 8, py + 8, px + pw - 8, py + ph - 8],
                outline=(150, 140, 115, 255), width=1)
    cx = px + pw // 2
    d.text((cx - 28, py + 20), "VISAS", font=F_BOLD(17), fill=(40, 40, 40))
    d.text((px + pw - 40, py + 20), "9", font=F_REG(11), fill=(110, 100, 80))
    d.line([px + 24, py + 48, px + pw - 24, py + 48], fill=(120, 110, 90), width=1)
    blue = (28, 72, 150)
    purple = (128, 32, 96)
    green = (24, 110, 70)
    red = (178, 34, 34)
    stamps = [
        (make_oval_stamp([("KESTRIA", F_BOLD(15)), ("ARRIVAL", F_BOLD(11)),
                          ("04 MAY 2024", F_REG(11)), ("TARN CROSSING", F_REG(9))],
                         blue, -6, 200, 80), px + 30, py + 60),
        (make_oval_stamp([("KESTRIA", F_BOLD(15)), ("DEPARTURE", F_BOLD(11)),
                          ("19 MAY 2024", F_REG(11)), ("TARN CROSSING", F_REG(9))],
                         blue, 4, 200, 80), px + 230, py + 122),
        (make_oval_stamp([("ONDAL REPUBLIC", F_BOLD(13)), ("ARRIVAL", F_BOLD(11)),
                          ("02 SEP 2025", F_REG(11)), ("PORT LIR", F_REG(9))],
                         purple, 5, 200, 80), px + 30, py + 184),
        (make_oval_stamp([("ONDAL REPUBLIC", F_BOLD(13)), ("DEPARTURE", F_BOLD(11)),
                          ("21 SEP 2025", F_REG(11)), ("PORT LIR", F_REG(9))],
                         purple, -4, 200, 80), px + 230, py + 246),
        (make_oval_stamp([("KESTRIA", F_BOLD(15)), ("ARRIVAL", F_BOLD(11)),
                          ("14 JAN 2026", F_REG(11)), ("TARN CROSSING", F_REG(9))],
                         green, -7, 200, 80), px + 30, py + 308),
        (make_oval_stamp([("KESTRIA", F_BOLD(15)), ("DEPARTURE", F_BOLD(11)),
                          ("28 JAN 2026", F_REG(11)), ("TARN CROSSING", F_REG(9))],
                         green, 3, 200, 80), px + 230, py + 370),
    ]
    for layer, sx, sy in stamps:
        img.paste(layer, (sx, sy), layer)
    # telling detail: the folk-song visa condition, boxed in red
    cond = make_stamp([("VISA CONDITION", F_BOLD(14)),
                       ("HOLDER MUST PRESENT", F_BOLD(11)),
                       ("ONE FOLK SONG AT", F_BOLD(11)),
                       ("BORDER CONTROL", F_BOLD(11)),
                       ("Art. 17, Border Code", F_REG(9))],
                      red, -2, box_w=252, box_h=88)
    img.paste(cond, (px + 96, py + 514), cond)
    # fee stamp: single-line strip at the bottom of the page
    fee = make_stamp([("MOUNTAIN PASS FEE — 12 KRON — PAID", F_BOLD(12))],
                     green, 3, box_w=300, box_h=30)
    img.paste(fee, (px + 85, py + 668), fee)

def main():
    img = Image.new("RGB", (W, H), (52, 66, 74))
    # desk texture: faint horizontal grain
    d = ImageDraw.Draw(img)
    for y in range(0, H, 4):
        d.line([0, y, W, y], fill=(56, 70, 78))
    # soft shadows under the spread
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([36, 140, 988, 900], radius=6, fill=(0, 0, 0, 90))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow), (0, 0))
    draw_data_page(img, 40, 132, 470, 760)
    draw_visa_page(img, 514, 132, 470, 760)
    # centre gutter shadow
    gd = ImageDraw.Draw(img, "RGBA")
    for i in range(10):
        gd.line([510 - i, 132, 510 - i, 892], fill=(0, 0, 0, 18 - i))
        gd.line([514 + i, 132, 514 + i, 892], fill=(0, 0, 0, 18 - i))
    img.save("entry.png", optimize=True)
    print("saved entry.png")

if __name__ == "__main__":
    main()
