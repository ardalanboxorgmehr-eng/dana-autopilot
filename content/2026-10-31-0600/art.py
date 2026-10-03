import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (50, 80, 180)


def icon_person(d, cx, cy, s, col):
    d.ellipse([cx - s * 0.3, cy - s, cx + s * 0.3, cy - s * 0.4], fill=col)
    d.rounded_rectangle([cx - s * 0.5, cy - s * 0.32, cx + s * 0.5, cy + s * 0.5], radius=int(s * 0.3), fill=col)


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (14, 20, 50), (4, 4, 12), T)
    im = addglow(im, lambda d: (d.ellipse([100, 120, 980, 760], fill=(80, 120, 255)), d.ellipse([560, 220, 900, 560], fill=(255, 190, 70))), 130, 0.4)
    d = ImageDraw.Draw(im)
    # 4 x 3 grid of people, one in each group of 4 highlighted -> 1 in 4
    cols, rows = 4, 3
    for r in range(rows):
        for c in range(cols):
            cx = 190 + c * 233; cy = 270 + r * 210
            hl = (c == (r + 1) % 4)
            if hl: d.rounded_rectangle([cx - 85, cy - 150, cx + 85, cy + 70], radius=26, fill=(60, 50, 20), outline=AMB, width=5)
            icon_person(d, cx, cy, 110, AMB if hl else (110, 120, 150))
            if hl:
                d.rounded_rectangle([cx + 20, cy - 30, cx + 80, cy + 20], radius=10, fill=(30, 30, 40), outline=AMB, width=3)
                d.text((cx + 50, cy - 5), "AI", font=F(POPB, 24), fill=AMB, anchor="mm")
    d.text((W / 2, 90), "1 in 4 jobs", font=F(POPB, 64), fill=WHITE, anchor="mm")
    d.text((W / 2, 790), "ILO global index · 2025", font=F(POPB, 30), fill=GREY, anchor="mm")
    im.save(path, quality=95)


def ranking(path):
    W, H = 1000, 440
    im = base((W, H), (14, 20, 50), (4, 4, 12), T); d = ImageDraw.Draw(im)
    fa(d, (W - 60, 30), "بیشترین مواجهه", F(VB, 34), WHITE)
    items = [("Clerical support", "data entry, documents, scheduling", AMB, "1"),
             ("Some digital jobs", "media, software, finance", BLUE, "2")]
    for i, (a, b, col, n) in enumerate(items):
        y = 110 + i * 160
        panel(d, [60, y, W - 60, y + 130], r=24, fill=(18, 22, 40), outline=col, w=4)
        d.ellipse([85, y + 37, 141, y + 93], fill=col)
        d.text((113, y + 65), n, font=F(POPB, 28), fill=(12, 12, 16), anchor="mm")
        d.text((165, y + 44), a, font=F(POPB, 34), fill=WHITE, anchor="lm")
        d.text((165, y + 92), b, font=F(POP, 26), fill=GREY, anchor="lm")
    im.save(path, quality=95)


def income(path):
    W, H = 1000, 470
    im = base((W, H), (14, 20, 50), (4, 4, 12), T); d = ImageDraw.Draw(im)
    bars(d, 60, 40, W - 120, [("کشورهای پردرآمد", 34, BLUE, "34%"), ("میانگین دنیا", 25, AMB, "25%"), ("کشورهای کم‌درآمد", 11, GR, "11%")], rowh=140, maxv=40)
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); ranking("d1.png"); income("d2.png"); print("art ok")
