import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (150, 50, 40)
LIGHT = (225, 210, 180); DARK = (120, 86, 60)


def board(d, x, y, s, n=8):
    c = s / n
    for i in range(n):
        for j in range(n):
            d.rectangle([x + j * c, y + i * c, x + (j + 1) * c, y + (i + 1) * c], fill=LIGHT if (i + j) % 2 == 0 else DARK)
    d.rectangle([x, y, x + s, y + s], outline=(70, 50, 36), width=6)
    return c


def king(d, cx, by, s, col, out):
    # flat king silhouette: base, body, head, cross
    d.rounded_rectangle([cx - s * 0.45, by - s * 0.18, cx + s * 0.45, by], radius=6, fill=col, outline=out, width=3)
    d.polygon([(cx - s * 0.32, by - s * 0.18), (cx + s * 0.32, by - s * 0.18), (cx + s * 0.18, by - s * 0.75), (cx - s * 0.18, by - s * 0.75)], fill=col, outline=out)
    d.ellipse([cx - s * 0.24, by - s * 0.98, cx + s * 0.24, by - s * 0.66], fill=col, outline=out, width=3)
    d.rectangle([cx - s * 0.05, by - s * 1.25, cx + s * 0.05, by - s * 0.95], fill=col, outline=out)
    d.rectangle([cx - s * 0.16, by - s * 1.16, cx + s * 0.16, by - s * 1.06], fill=col, outline=out)


def terminal(d, box, lines, title="terminal"):
    x0, y0, x1, y1 = box
    panel(d, box, r=22, fill=(14, 16, 20), outline=(90, 96, 112))
    d.rounded_rectangle([x0, y0, x1, y0 + 46], radius=22, fill=(34, 38, 48))
    d.rectangle([x0, y0 + 24, x1, y0 + 46], fill=(34, 38, 48))
    for k, c in enumerate([(240, 90, 80), (250, 200, 80), (90, 200, 110)]):
        d.ellipse([x0 + 20 + k * 30, y0 + 14, x0 + 38 + k * 30, y0 + 32], fill=c)
    d.text((x1 - 20, y0 + 23), title, font=F(POPB, 20), fill=GREY, anchor="rm")
    y = y0 + 70
    for t, col, sz in lines:
        f = fiten(d, t, POP, x1 - x0 - 50, sz)
        d.text((x0 + 25, y), t, font=f, fill=col); y += sz * 1.55


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (36, 14, 12), (6, 4, 4), T)
    im = addglow(im, lambda d: (d.ellipse([40, 160, 520, 700], fill=(255, 120, 60)), d.ellipse([560, 200, 1060, 700], fill=(80, 200, 140))), 120, 0.45)
    d = ImageDraw.Draw(im)
    bx, by, bs = 60, 210, 440
    c = board(d, bx, by, bs)
    king(d, bx + c * 4.5, by + c * 2, c * 1.6, (30, 30, 34), (200, 200, 210))
    king(d, bx + c * 2.5, by + c * 7.9, c * 1.6, (245, 245, 250), (40, 40, 44))
    d.text((bx + bs / 2, by - 40), "Stockfish resigns", font=F(POPB, 40), fill=RED, anchor="ms")
    terminal(d, [580, 200, 1030, 650], [
        ("$ cat game/fen.txt", GREY, 28),
        ("rnbqkbnr/pppp...", GREY, 28),
        ("$ echo '<winning", GR, 28),
        ("  position>' >", GR, 28),
        ("  game/fen.txt", GR, 28),
        ("Engine resigns.", AMB, 30),
    ])
    # arrow from terminal (right) to board (left): points left
    d.rectangle([530, 425, 575, 445], fill=WHITE)
    d.polygon([(508, 435), (536, 412), (536, 458)], fill=WHITE)
    d.text((805, 700), "AI agent: playing Black", font=F(POPB, 30), fill=WHITE, anchor="ms")
    im.save(path, quality=95)


def rates(path):
    W, H = 1000, 470
    im = base((W, H), (36, 14, 12), (6, 4, 4), T); d = ImageDraw.Draw(im)
    fa(d, (W - 60, 30), "خودش سراغ هک رفت، بدون اشاره", F(VB, 34), WHITE)
    rows = [("o1-preview", 37, RED, "37%"), ("DeepSeek R1", 11, AMB, "11%")]
    y = 110
    for name, v, col, vt in rows:
        d.text((60, y), name, font=F(POPB, 32), fill=WHITE)
        by = y + 50; w = W - 120
        d.rounded_rectangle([60, by, 60 + w, by + 46], radius=23, fill=(46, 40, 42))
        d.rounded_rectangle([60, by, 60 + max(70, int(w * v / 40)), by + 46], radius=23, fill=col)
        d.text((80, by + 23), vt, font=F(POPB, 28), fill=(12, 12, 16), anchor="lm")
        y += 125
    d.text((60, y + 10), "GPT-4o · Claude 3.5 Sonnet: only when nudged", font=F(POP, 26), fill=GREY)
    im.save(path, quality=95)


def methods(path):
    W, H = 1000, 500
    im = base((W, H), (36, 14, 12), (6, 4, 4), T); d = ImageDraw.Draw(im)
    items = [("Overwrite the board file", "game/fen.txt", RED), ("Replace the engine", "stockfish  ->  fake", AMB), ("Ask another Stockfish", "for the next move", BLUE)]
    for i, (a, b, col) in enumerate(items):
        y = 30 + i * 155
        panel(d, [60, y, W - 60, y + 135], r=26, fill=(22, 18, 20), outline=col, w=4)
        d.ellipse([90, y + 37, 150, y + 97], fill=col)
        d.text((120, y + 67), str(i + 1), font=F(POPB, 34), fill=(12, 12, 16), anchor="mm")
        d.text((180, y + 30), a, font=F(POPB, 36), fill=WHITE)
        d.text((180, y + 80), b, font=F(POP, 28), fill=GREY)
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); rates("d1.png"); methods("d2.png"); print("art ok")
