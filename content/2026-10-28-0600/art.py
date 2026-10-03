import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (30, 110, 170)


def pin(d, x, y, col, n=None):
    d.ellipse([x - 26, y - 70, x + 26, y - 18], fill=col)
    d.polygon([(x - 22, y - 36), (x + 22, y - 36), (x, y)], fill=col)
    if n: d.text((x, y - 44), str(n), font=F(POPB, 28), fill=(12, 12, 16), anchor="mm")
    else: d.ellipse([x - 10, y - 54, x + 10, y - 34], fill=(12, 12, 16))


def suitcase(d, x, y, w, h):
    d.rounded_rectangle([x + w * 0.32, y - 40, x + w * 0.68, y + 10], radius=18, outline=(230, 140, 60), width=10)
    d.rounded_rectangle([x, y, x + w, y + h], radius=30, fill=(230, 140, 60))
    for k in (0.3, 0.7): d.rectangle([x + w * k - 8, y, x + w * k + 8, y + h], fill=(190, 105, 40))
    d.ellipse([x + 20, y + h - 6, x + 60, y + h + 30], fill=(40, 40, 46)); d.ellipse([x + w - 60, y + h - 6, x + w - 20, y + h + 30], fill=(40, 40, 46))


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (12, 30, 50), (4, 6, 12), T)
    im = addglow(im, lambda d: (d.ellipse([60, 120, 640, 700], fill=(60, 160, 255)), d.ellipse([640, 300, 1060, 760], fill=(255, 150, 60))), 120, 0.45)
    d = ImageDraw.Draw(im)
    # map card
    panel(d, [60, 120, 640, 720], r=34, fill=(222, 232, 222), outline=(120, 160, 140), w=4)
    d.polygon([(60, 520), (260, 430), (420, 560), (640, 470), (640, 720), (60, 720)], fill=(150, 200, 230))
    d.ellipse([380, 180, 560, 320], fill=(180, 214, 170))
    pts = [(150, 300), (300, 250), (470, 400), (360, 560)]
    for a, b in zip(pts, pts[1:]):
        for k in range(10):
            t0, t1 = k / 10, (k + 0.5) / 10
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=(40, 70, 120), width=7)
    for i, (x, y) in enumerate(pts, 1): pin(d, x, y, (230, 80, 70) if i == 1 else BLUE, i)
    # checklist card
    panel(d, [690, 120, 1020, 470], r=30, fill=(20, 28, 44), outline=GR, w=4)
    d.text((720, 150), "Day 1", font=F(POPB, 36), fill=GR)
    for i, t in enumerate(["Morning", "Afternoon", "Evening"]):
        y = 220 + i * 76
        d.rounded_rectangle([720, y, 760, y + 40], radius=8, fill=GR)
        d.line([(728, y + 20), (738, y + 32), (754, y + 8)], fill=(12, 12, 16), width=5)
        d.text((780, y + 20), t, font=F(POP, 32), fill=WHITE, anchor="lm")
    suitcase(d, 740, 560, 230, 170)
    im.save(path, quality=95)


def days(path):
    W, H = 1000, 500
    im = base((W, H), (12, 30, 50), (4, 6, 12), T); d = ImageDraw.Draw(im)
    cols = [("Day 1", ["Old town walk", "Museum", "Night market"]), ("Day 2", ["Park + lake", "Lunch nearby", "Sunset view"]), ("Day 3", ["Day trip", "Train back", "Free evening"])]
    cw = (W - 120 - 40) / 3
    for i, (h, items) in enumerate(cols):
        x = 60 + i * (cw + 20)
        panel(d, [x, 40, x + cw, H - 40], r=26, fill=(18, 26, 42), outline=BLUE, w=3)
        d.text((x + 24, 70), h, font=F(POPB, 36), fill=AMB)
        for k, t in enumerate(items):
            y = 140 + k * 100
            d.rounded_rectangle([x + 20, y, x + cw - 20, y + 80], radius=16, fill=(32, 44, 66))
            d.text((x + 40, y + 40), t, font=fiten(d, t, POP, cw - 80, 28), fill=WHITE, anchor="lm")
    im.save(path, quality=95)


def budget(path):
    W, H = 1000, 520
    im = base((W, H), (12, 30, 50), (4, 6, 12), T); d = ImageDraw.Draw(im)
    panel(d, [60, 30, W - 60, H - 30], r=30, fill=(18, 24, 36), outline=(90, 110, 140))
    d.text((100, 60), "Budget (estimate)", font=F(POPB, 36), fill=WHITE)
    rows = [("Stay", 40, BLUE), ("Food", 25, GR), ("Transport", 15, AMB), ("Tickets", 10, (200, 120, 240)), ("Emergency", 10, RED)]
    for i, (n, v, col) in enumerate(rows):
        y = 130 + i * 68
        d.text((100, y + 22), n, font=F(POP, 30), fill=WHITE, anchor="lm")
        d.rounded_rectangle([330, y + 4, 800, y + 40], radius=18, fill=(40, 46, 60))
        d.rounded_rectangle([330, y + 4, 330 + 470 * v / 40, y + 40], radius=18, fill=col)
        d.text((W - 100, y + 22), f"{v}%", font=F(POPB, 30), fill=col, anchor="rm")
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); days("d1.png"); budget("d2.png"); print("art ok")
