import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (40, 140, 70)
SG = (33, 115, 70)


def sheet(d, box, headers, rows, fx, hi=None, cw=None):
    x0, y0, x1, y1 = box
    panel(d, box, r=24, fill=(250, 251, 252), outline=(120, 170, 140), w=4)
    # formula bar
    d.rounded_rectangle([x0 + 20, y0 + 20, x1 - 20, y0 + 74], radius=10, fill=(232, 240, 234), outline=(170, 200, 180), width=2)
    d.text((x0 + 36, y0 + 47), "fx", font=F(POPB, 26), fill=SG, anchor="lm")
    d.text((x0 + 80, y0 + 47), fx, font=fiten(d, fx, POPB, x1 - x0 - 120, 26), fill=(30, 34, 40), anchor="lm")
    n = len(headers); cw = cw or [(x1 - x0 - 40) / n] * n
    ty = y0 + 96; rh = 52
    x = x0 + 20
    for j, h in enumerate(headers):
        d.rectangle([x, ty, x + cw[j], ty + rh], fill=(222, 234, 226), outline=(190, 200, 194))
        d.text((x + 14, ty + rh / 2), h, font=F(POPB, 24), fill=(40, 60, 50), anchor="lm")
        x += cw[j]
    for i, r in enumerate(rows):
        x = x0 + 20; y = ty + rh * (i + 1)
        for j, v in enumerate(r):
            fill = (255, 255, 255)
            if hi and (i, j) == hi: fill = (210, 245, 220)
            d.rectangle([x, y, x + cw[j], y + rh], fill=fill, outline=(214, 220, 216))
            d.text((x + 14, y + rh / 2), v, font=F(POP, 24), fill=(30, 34, 40), anchor="lm")
            x += cw[j]
    if hi:
        i, j = hi; x = x0 + 20 + sum(cw[:j]); y = ty + rh * (i + 1)
        d.rectangle([x, y, x + cw[j], y + rh], outline=SG, width=4)


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (12, 36, 22), (4, 8, 6), T)
    im = addglow(im, lambda d: (d.ellipse([40, 300, 640, 820], fill=(60, 220, 120)), d.ellipse([560, 80, 1060, 520], fill=(90, 160, 255))), 120, 0.45)
    d = ImageDraw.Draw(im)
    # chat bubble (question) top right
    d.rounded_rectangle([430, 110, 1020, 290], radius=30, fill=(44, 64, 110))
    for i, t in enumerate(["Sum sales for North", "since Jan 2026"]):
        d.text((460, 140 + i * 56), t, font=F(POP, 40), fill=WHITE)
    # arrow down from bubble to sheet
    d.rectangle([715, 300, 735, 345], fill=WHITE); d.polygon([(700, 342), (750, 342), (725, 372)], fill=WHITE)
    sheet(d, [60, 380, 1020, 760], ["A  Region", "B  Date", "C  Sales"], [["North", "2026-02-01", "20"], ["South", "2026-02-03", "45"], ["North", "2025-12-01", "30"]],
          '=SUMIFS(C:C,A:A,"North",B:B,">="&DATE(2026,1,1))')
    im.save(path, quality=95)


def lookup(path):
    W, H = 1000, 380
    im = base((W, H), (12, 36, 22), (4, 8, 6), T); d = ImageDraw.Draw(im)
    sheet(d, [40, 30, W - 40, H - 30], ["A  Code", "B  Price"], [["X1", "100"], ["X2", "250"], ["X9", "Not found"]],
          '=XLOOKUP(A2,Prices!A:A,Prices!B:B,"Not found")', hi=(0, 1))
    im.save(path, quality=95)


def sumifs(path):
    W, H = 1000, 420
    im = base((W, H), (12, 36, 22), (4, 8, 6), T); d = ImageDraw.Draw(im)
    parts = [("C:C", "what to add", GR), ("A:A, \"North\"", "condition 1", BLUE), ("B:B, \">=\"&DATE(2026,1,1)", "condition 2", AMB)]
    d.text((60, 40), "=SUMIFS(", font=F(POPB, 40), fill=WHITE)
    for i, (code, lab, col) in enumerate(parts):
        y = 110 + i * 92
        d.rounded_rectangle([100, y, 700, y + 72], radius=18, fill=(20, 30, 24), outline=col, width=4)
        d.text((125, y + 36), code, font=fiten(d, code, POPB, 560, 32), fill=col, anchor="lm")
        d.text((730, y + 36), lab, font=F(POP, 30), fill=WHITE, anchor="lm")
    d.text((60, 385), ")", font=F(POPB, 40), fill=WHITE, anchor="ls")
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); lookup("d1.png"); sumifs("d2.png"); print("art ok")
