import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (190, 60, 120)
PINK = (250, 120, 170)


def scan(d, x, y, w, h, spot=None):
    # flat stylised mammogram tile: dark panel with a soft half-dome shape
    d.rounded_rectangle([x, y, x + w, y + h], radius=18, fill=(14, 14, 18), outline=(80, 84, 96), width=3)
    d.pieslice([x - w * 0.55, y + h * 0.08, x + w * 0.85, y + h * 0.92], -90, 90, fill=(70, 72, 82))
    d.pieslice([x - w * 0.4, y + h * 0.2, x + w * 0.65, y + h * 0.8], -90, 90, fill=(96, 98, 110))
    if spot:
        cx, cy = x + w * spot[0], y + h * spot[1]
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=(200, 200, 210))
        d.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=AMB, width=5)


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (44, 14, 30), (8, 4, 6), T)
    im = addglow(im, lambda d: (d.ellipse([60, 160, 560, 700], fill=(255, 100, 160)), d.ellipse([560, 200, 1060, 700], fill=(90, 160, 255))), 120, 0.45)
    d = ImageDraw.Draw(im)
    scan(d, 70, 150, 330, 470, spot=(0.42, 0.45))
    # risk score badge
    d.rounded_rectangle([90, 640, 380, 720], radius=40, fill=AMB)
    d.text((235, 680), "AI risk score: 10", font=F(POPB, 32), fill=(12, 12, 16), anchor="mm")
    # stats on right
    for i, (big, small, col) in enumerate([("+29%", "cancers detected", GR), ("-44%", "screen-reading workload", BLUE)]):
        y = 170 + i * 260
        panel(d, [470, y, 1010, y + 220], r=30, fill=(22, 18, 26), outline=col, w=4)
        d.text((740, y + 95), big, font=F(POPB, 100), fill=col, anchor="mm")
        d.text((740, y + 175), small, font=F(POP, 32), fill=WHITE, anchor="mm")
    d.text((740, 720), "MASAI trial · Sweden", font=F(POPB, 30), fill=GREY, anchor="mm")
    im.save(path, quality=95)


def doc(d, cx, cy, col):
    person(d, cx, cy, 46, col)


def triage(path):
    W, H = 1000, 520
    im = base((W, H), (44, 14, 30), (8, 4, 6), T); d = ImageDraw.Draw(im)
    scan(d, 50, 150, 160, 220)
    # arrow right to AI box
    d.rectangle([220, 250, 262, 268], fill=WHITE); d.polygon([(258, 240), (290, 259), (258, 278)], fill=WHITE)
    panel(d, [300, 180, 470, 340], r=24, fill=(30, 22, 34), outline=AMB, w=4)
    d.text((385, 235), "AI", font=F(POPB, 48), fill=AMB, anchor="mm")
    d.text((385, 295), "score 1-10", font=F(POP, 24), fill=WHITE, anchor="mm")
    # branches
    for (ty, lab, n, col) in [(120, "score 1-9", 1, GR), (400, "score 10", 2, RED)]:
        d.line([(470, 260), (560, 260), (560, ty), (600, ty)], fill=WHITE, width=6)
        d.polygon([(596, ty - 14), (624, ty), (596, ty + 14)], fill=WHITE)
        panel(d, [630, ty - 80, 960, ty + 80], r=24, fill=(22, 18, 26), outline=col, w=4)
        d.text((655, ty - 50), lab, font=F(POPB, 30), fill=col)
        for k in range(n): person(d, 680 + k * 62, ty + 22, 30, (200, 205, 220))
        fa(d, (940, ty + 30), "یه رادیولوژیست" if n == 1 else "دو رادیولوژیست", F(VB, 26), WHITE, "rm")
    im.save(path, quality=95)


def results(path):
    W, H = 1000, 500
    im = base((W, H), (44, 14, 30), (8, 4, 6), T); d = ImageDraw.Draw(im)
    d.text((60, 40), "Cancers detected per 1,000 women", font=F(POPB, 32), fill=WHITE)
    rows = [("Standard double reading", 5.0, (130, 136, 150)), ("AI-supported", 6.4, GR)]
    for i, (n, v, col) in enumerate(rows):
        y = 110 + i * 120
        d.text((60, y), n, font=F(POP, 28), fill=WHITE)
        d.rounded_rectangle([60, y + 42, 940, y + 92], radius=25, fill=(40, 34, 40))
        d.rounded_rectangle([60, y + 42, 60 + 880 * v / 7, y + 92], radius=25, fill=col)
        d.text((80, y + 67), f"{v}", font=F(POPB, 30), fill=(12, 12, 16), anchor="lm")
    d.text((60, 375), "False positives: 1.4% vs 1.5%", font=F(POPB, 30), fill=AMB)
    d.text((60, 425), "The Lancet Digital Health, 2025", font=F(POP, 26), fill=GREY)
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); triage("d1.png"); results("d2.png"); print("art ok")
