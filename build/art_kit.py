# Shared drawing helpers for Dana AI carousels. art.py files import this.
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
FD = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
POP = os.path.join(FD, "Poppins-Medium.ttf"); POPB = os.path.join(FD, "Poppins-Bold.ttf")
VB = os.path.join(FD, "Vazirmatn-Bold.ttf"); VS = os.path.join(FD, "Vazirmatn-SemiBold.ttf"); VK = os.path.join(FD, "Vazirmatn-Black.ttf")
FA = dict(direction="rtl", language="fa")
GR = (60, 200, 150); RED = (240, 80, 80); AMB = (255, 206, 84); BLUE = (90, 160, 240); WHITE = (240, 242, 248); GREY = (150, 156, 170)


def F(p, s):
    return ImageFont.truetype(p, s)


def base(size, c1=(18, 22, 40), c2=(6, 6, 10), tint=(40, 60, 130)):
    W, H = size
    im = Image.new("RGB", size, c2); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3)))
    g = Image.new("L", size, 0); ImageDraw.Draw(g).ellipse([-W * 0.3, -H * 0.6, W * 1.3, H * 0.75], fill=62)
    g = g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB", size, tint), im, g)


def glow(im, fn, blur=60, scale=0.5):
    l = Image.new("RGB", im.size, (0, 0, 0)); fn(ImageDraw.Draw(l))
    return ImageChops.add(im, l.filter(ImageFilter.GaussianBlur(blur)), scale=1 / scale if scale else 1)


def addglow(im, fn, blur=60, amount=0.45):
    l = Image.new("RGB", im.size, (0, 0, 0)); fn(ImageDraw.Draw(l))
    l = l.filter(ImageFilter.GaussianBlur(blur))
    l = Image.eval(l, lambda v: int(v * amount))
    return ImageChops.add(im, l)


def fa(d, xy, t, f, fill, anchor="ra"):
    d.text(xy, t, font=f, fill=fill, anchor=anchor, **FA)


def fitfa(d, t, p, maxw, start):
    s = start
    while s > 16:
        f = F(p, s)
        if d.textlength(t, font=f, **FA) <= maxw:
            return f
        s -= 2
    return F(p, 16)


def fiten(d, t, p, maxw, start):
    s = start
    while s > 14:
        f = F(p, s)
        if d.textlength(t, font=f) <= maxw:
            return f
        s -= 2
    return F(p, 14)


def panel(d, box, r=28, fill=(22, 24, 32), outline=(70, 76, 92), w=3):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=w)


def phone(d, x, y, w, h, fill=(16, 18, 24), outline=(90, 96, 112)):
    d.rounded_rectangle([x, y, x + w, y + h], radius=int(w * 0.12), fill=fill, outline=outline, width=6)
    d.rounded_rectangle([x + w * 0.38, y + 18, x + w * 0.62, y + 34], radius=8, fill=(40, 44, 54))
    return (x + 24, y + 56, x + w - 24, y + h - 30)


def bars(d, x0, y0, w, items, rowh=120, maxv=None, fsize=34):
    """items: list of (label_fa, value, color, value_text). Horizontal bars, RTL labels above."""
    maxv = maxv or max(v for _, v, _, _ in items)
    y = y0
    for lab, v, col, vt in items:
        fa(d, (x0 + w, y), lab, F(VB, fsize), (225, 228, 236))
        by = y + fsize + 18
        d.rounded_rectangle([x0, by, x0 + w, by + 44], radius=22, fill=(38, 42, 54))
        bw = max(60, int(w * v / maxv))
        d.rounded_rectangle([x0 + w - bw, by, x0 + w, by + 44], radius=22, fill=col)
        d.text((x0 + w - bw + 20, by + 22), vt, font=F(POPB, 28), fill=(12, 12, 16), anchor="lm")
        y += rowh
    return y


def waveform(d, x0, y0, w, h, col, n=48, seed=3, phase=0.0):
    import random
    r = random.Random(seed)
    step = w / n
    for i in range(n):
        a = abs(math.sin(i * 0.45 + phase)) * 0.7 + r.random() * 0.3
        bh = max(8, a * h)
        cx = x0 + i * step + step / 2
        d.rounded_rectangle([cx - step * 0.28, y0 + (h - bh) / 2, cx + step * 0.28, y0 + (h + bh) / 2], radius=int(step * 0.28), fill=col)


def person(d, cx, cy, s, col, head=None):
    """Simple bust silhouette centred at cx, cy (shoulders baseline cy+s)."""
    head = head or col
    d.ellipse([cx - s * 0.32, cy - s * 0.9, cx + s * 0.32, cy - s * 0.26], fill=head)
    d.rounded_rectangle([cx - s * 0.62, cy - s * 0.18, cx + s * 0.62, cy + s * 0.7], radius=int(s * 0.5), fill=col)


def save(im, path):
    im.save(path, quality=95)
