import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (200, 110, 30)
ORG = (255, 160, 60)


def page(d, x, y, w, h, lab, col, lines=7):
    panel(d, [x, y, x + w, y + h], r=16, fill=(236, 238, 244), outline=col, w=4)
    for i in range(lines): d.rounded_rectangle([x + 22, y + 62 + i * 30, x + w - 22 - (i % 3) * 40, y + 74 + i * 30], radius=6, fill=(190, 196, 210))
    tw = d.textlength(lab, font=F(POPB, 24))
    d.rounded_rectangle([x + 14, y + 14, x + 14 + tw + 24, y + 48], radius=12, fill=col)
    d.text((x + 26, y + 31), lab, font=F(POPB, 24), fill=WHITE, anchor="lm")


def play(d, x, y, w, h):
    panel(d, [x, y, x + w, y + h], r=22, fill=(30, 30, 38), outline=(120, 126, 140))
    cx, cy = x + w / 2, y + h / 2 - 10
    d.ellipse([cx - 44, cy - 44, cx + 44, cy + 44], fill=RED)
    d.polygon([(cx - 14, cy - 22), (cx - 14, cy + 22), (cx + 24, cy)], fill=WHITE)
    d.rounded_rectangle([x + 20, y + h - 30, x + w - 20, y + h - 20], radius=5, fill=(70, 74, 86))
    d.text((x + w - 20, y + h - 40), "1:02:14", font=F(POPB, 22), fill=GREY, anchor="rs")


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (44, 26, 10), (8, 6, 4), T)
    im = addglow(im, lambda d: (d.ellipse([40, 140, 560, 760], fill=(255, 150, 60)), d.ellipse([620, 200, 1060, 700], fill=(80, 200, 140))), 120, 0.45)
    d = ImageDraw.Draw(im)
    # stack of pages
    for k in range(4, 0, -1):
        page(d, 70 + k * 16, 140 + k * 16, 300, 380, "PDF", (220, 70, 70), lines=9)
    page(d, 70, 140, 300, 380, "PDF", (220, 70, 70), lines=9)
    d.rounded_rectangle([210, 154, 356, 190], radius=18, fill=(40, 40, 50))
    d.text((283, 172), "100 pages", font=F(POPB, 22), fill=WHITE, anchor="mm")
    play(d, 90, 620, 300, 190)
    # arrow left -> right
    d.rectangle([450, 440, 545, 462], fill=WHITE); d.polygon([(540, 425), (585, 451), (540, 477)], fill=WHITE)
    # summary card
    panel(d, [610, 220, 1020, 690], r=30, fill=(20, 26, 22), outline=GR, w=4)
    d.text((640, 255), "Summary", font=F(POPB, 40), fill=GR)
    for i in range(5):
        y = 335 + i * 66
        d.ellipse([642, y + 4, 666, y + 28], fill=AMB)
        d.rounded_rectangle([684, y + 8, 990 - (i % 2) * 70, y + 24], radius=8, fill=(90, 100, 96))
        d.text((990, y + 16), f"p.{[3, 12, 27, 41, 88][i]}", font=F(POPB, 20), fill=GREY, anchor="rm") if i % 2 else None
    d.text((815, 730), "2 min read", font=F(POPB, 32), fill=WHITE, anchor="mm")
    im.save(path, quality=95)


def goals(path):
    W, H = 1000, 480
    im = base((W, H), (44, 26, 10), (8, 6, 4), T); d = ImageDraw.Draw(im)
    page(d, 50, 80, 220, 300, "PDF", (220, 70, 70), lines=6)
    outs = [("For my exam", "key ideas + quiz", GR), ("For a decision", "pros, cons, risks", BLUE), ("Worth reading?", "3 lines + verdict", AMB)]
    for i, (a, b, col) in enumerate(outs):
        y = 40 + i * 140
        d.line([(285, 230), (380, y + 60)], fill=WHITE, width=5)
        d.polygon([(380, y + 60), (360, y + 44 + (i - 1) * 6), (356, y + 70 + (i - 1) * 6)], fill=WHITE)
        panel(d, [395, y, W - 50, y + 120], r=24, fill=(26, 22, 18), outline=col, w=4)
        d.text((425, y + 38), a, font=F(POPB, 34), fill=WHITE, anchor="lm")
        d.text((425, y + 84), b, font=F(POP, 28), fill=GREY, anchor="lm")
    im.save(path, quality=95)


def transcript(path):
    W, H = 1000, 500
    im = base((W, H), (44, 26, 10), (8, 6, 4), T); d = ImageDraw.Draw(im)
    play(d, 50, 50, 380, 240)
    panel(d, [50, 320, 430, 450], r=22, fill=(26, 26, 32), outline=(90, 96, 112))
    d.text((80, 350), "Description", font=F(POPB, 26), fill=GREY)
    d.rounded_rectangle([80, 392, 330, 432], radius=20, fill=(60, 64, 76))
    d.text((205, 412), "Show transcript", font=F(POPB, 22), fill=WHITE, anchor="mm")
    d.rectangle([450, 245, 500, 263], fill=WHITE); d.polygon([(496, 232), (526, 254), (496, 276)], fill=WHITE)
    panel(d, [540, 50, W - 50, H - 50], r=26, fill=(20, 20, 24), outline=ORG, w=4)
    d.text((570, 80), "Transcript", font=F(POPB, 30), fill=ORG)
    for i, t in enumerate(["0:00", "0:42", "3:15", "7:58", "12:30"]):
        y = 140 + i * 58
        d.text((570, y), t, font=F(POPB, 24), fill=BLUE)
        d.rounded_rectangle([650, y + 6, W - 80 - (i % 3) * 50, y + 22], radius=8, fill=(80, 84, 96))
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); goals("d1.png"); transcript("d2.png"); print("art ok")
