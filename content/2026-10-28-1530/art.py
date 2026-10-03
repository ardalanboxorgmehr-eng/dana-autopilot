import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (120, 60, 170)
PUR = (180, 130, 255)


def bubble(d, box, lines, col, f, fill=WHITE):
    d.rounded_rectangle(box, radius=28, fill=col)
    x0, y0, x1, y1 = box
    for i, t in enumerate(lines): d.text((x0 + 30, y0 + 28 + i * f.size * 1.4), t, font=f, fill=fill)


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (30, 16, 50), (6, 4, 12), T)
    im = addglow(im, lambda d: (d.ellipse([140, 100, 760, 700], fill=(150, 90, 255)), d.ellipse([600, 380, 1060, 800], fill=(255, 80, 80))), 120, 0.45)
    d = ImageDraw.Draw(im)
    bubble(d, [380, 130, 1010, 240], ["Who wrote this paper?"], (52, 70, 120), F(POP, 40))
    bubble(d, [70, 290, 830, 520], ["It was written by", "Dr. A. Example in 2019,", "published in Journal X."], (40, 36, 58), F(POP, 40))
    # confident badge
    d.rounded_rectangle([90, 545, 470, 610], radius=32, fill=GR)
    d.text((280, 578), "100% confident", font=F(POPB, 32), fill=(12, 12, 16), anchor="mm")
    # stamp: NOT REAL
    st = Image.new("RGBA", (520, 170), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    sd.rounded_rectangle([6, 6, 514, 164], radius=24, outline=RED + (255,), width=10)
    sd.text((260, 85), "DOES NOT EXIST", font=F(POPB, 54), fill=RED + (255,), anchor="mm")
    st = st.rotate(-12, expand=True, resample=Image.BICUBIC)
    im.paste(st, (520, 520), st)
    im.save(path, quality=95)


def exam(path):
    W, H = 1000, 470
    im = base((W, H), (30, 16, 50), (6, 4, 12), T); d = ImageDraw.Draw(im)
    for i, (head, lab, pts, col) in enumerate([("Lucky guess", "", "+1", GR), ("\"I don't know\"", "", "0", RED)]):
        x = 60 + i * 450
        panel(d, [x, 30, x + 430, H - 80], r=28, fill=(22, 18, 36), outline=col, w=4)
        d.text((x + 215, 110), head, font=F(POPB, 40), fill=WHITE, anchor="mm")
        d.text((x + 215, 230), pts, font=F(POPB, 110), fill=col, anchor="mm")
        d.text((x + 215, 320), "points", font=F(POP, 30), fill=GREY, anchor="mm")
    fa(d, (W / 2, H - 20), "نمره‌دهی که فقط جواب درست رو حساب می‌کنه", F(VB, 30), WHITE, "ms")
    im.save(path, quality=95)


def stacked(path):
    W, H = 1000, 520
    im = base((W, H), (30, 16, 50), (6, 4, 12), T); d = ImageDraw.Draw(im)
    rows = [("o4-mini", [(24, GR), (75, RED), (1, GREY)]), ("gpt-5-thinking-mini", [(22, GR), (26, RED), (52, GREY)])]
    x0, w = 60, W - 120
    for i, (n, segs) in enumerate(rows):
        y = 50 + i * 170
        d.text((x0, y), n, font=F(POPB, 34), fill=WHITE)
        x = x0; by = y + 55
        for v, col in segs:
            sw = w * v / 100
            d.rectangle([x, by, x + sw, by + 70], fill=col)
            if v >= 10: d.text((x + sw / 2, by + 35), f"{v}%", font=F(POPB, 30), fill=(12, 12, 16), anchor="mm")
            x += sw
    ly = 420
    for k, (lab, col) in enumerate([("Right", GR), ("Wrong", RED), ("\"I don't know\"", GREY)]):
        lx = 60 + k * 300
        d.rounded_rectangle([lx, ly, lx + 36, ly + 36], radius=8, fill=col)
        d.text((lx + 50, ly + 18), lab, font=F(POP, 30), fill=WHITE, anchor="lm")
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); exam("d1.png"); stacked("d2.png"); print("art ok")
