import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T = (170, 130, 30)
PUR = (180, 130, 255)


def blocks(d, x0, y0, w, rows, hstep=78, lab_w=110):
    for i, (t, name, col) in enumerate(rows):
        y = y0 + i * hstep
        d.text((x0, y + hstep / 2 - 4), t, font=F(POPB, 26), fill=GREY, anchor="lm")
        if name:
            d.rounded_rectangle([x0 + lab_w, y + 6, x0 + w, y + hstep - 6], radius=16, fill=col)
            d.text((x0 + lab_w + 22, y + hstep / 2 - 2), name, font=F(POPB, 28), fill=(12, 12, 16), anchor="lm")
        else:
            d.line([(x0 + lab_w, y + hstep / 2), (x0 + w, y + hstep / 2)], fill=(60, 60, 70), width=2)


def cover(path):
    W, H = 1080, 900
    im = base((W, H), (40, 32, 10), (8, 6, 2), T)
    im = addglow(im, lambda d: (d.ellipse([40, 160, 460, 700], fill=(255, 120, 80)), d.ellipse([500, 120, 1060, 760], fill=(255, 210, 90))), 120, 0.4)
    d = ImageDraw.Draw(im)
    # messy list
    panel(d, [60, 170, 400, 690], r=26, fill=(236, 232, 220), outline=(200, 190, 160), w=4)
    d.text((90, 200), "To do", font=F(POPB, 38), fill=(40, 36, 30))
    for i in range(9):
        y = 270 + i * 44
        d.rectangle([90, y, 112, y + 22], outline=(120, 110, 90), width=3)
        d.rounded_rectangle([128, y + 4, 360 - (i * 37) % 120, y + 18], radius=6, fill=(170, 160, 140))
    # arrow right
    d.rectangle([420, 420, 500, 442], fill=WHITE); d.polygon([(496, 406), (536, 431), (496, 456)], fill=WHITE)
    # calendar day
    panel(d, [560, 140, 1020, 740], r=30, fill=(20, 20, 26), outline=AMB, w=4)
    d.text((590, 175), "Today", font=F(POPB, 38), fill=AMB)
    blocks(d, 590, 230, 400, [("9:00", "Report", BLUE), ("10:30", "Break", (120, 126, 140)), ("11:00", "Emails", GR), ("12:00", "Lunch", (120, 126, 140)), ("13:00", "Study", PUR), ("14:30", "Buffer", AMB), ("15:00", "Calls", (240, 130, 110))], hstep=70, lab_w=100)
    im.save(path, quality=95)


def inputs(path):
    W, H = 1000, 500
    im = base((W, H), (40, 32, 10), (8, 6, 2), T); d = ImageDraw.Draw(im)
    items = [("Tasks + deadlines", BLUE), ("Working hours", GR), ("Fixed meetings", (240, 130, 110)), ("Best focus time", PUR)]
    for i, (t, col) in enumerate(items):
        y = 40 + i * 108
        panel(d, [50, y, 470, y + 90], r=22, fill=(26, 24, 18), outline=col, w=4)
        d.text((80, y + 45), t, font=F(POPB, 30), fill=WHITE, anchor="lm")
        d.line([(470, y + 45), (560, 250)], fill=(150, 150, 160), width=4)
    d.polygon([(556, 228), (592, 250), (556, 272)], fill=WHITE)
    panel(d, [610, 120, 950, 380], r=30, fill=(26, 24, 18), outline=AMB, w=5)
    d.text((780, 200), "AI", font=F(POPB, 64), fill=AMB, anchor="mm")
    d.text((780, 300), "time-blocked day", font=F(POPB, 28), fill=WHITE, anchor="mm")
    im.save(path, quality=95)


def week(path):
    W, H = 1000, 460
    im = base((W, H), (40, 32, 10), (8, 6, 2), T); d = ImageDraw.Draw(im)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    cw = (W - 100) / 5
    plan = [[BLUE, GR, None, PUR], [GR, None, BLUE, AMB], [PUR, BLUE, GR, None], [BLUE, None, AMB, GR], [GR, PUR, None, None]]
    for i, dname in enumerate(days):
        x = 50 + i * cw
        d.text((x + cw / 2, 50), dname, font=F(POPB, 30), fill=WHITE, anchor="mm")
        for k, col in enumerate(plan[i]):
            y = 90 + k * 85
            if col: d.rounded_rectangle([x + 10, y, x + cw - 10, y + 72], radius=14, fill=col)
            else:
                d.rounded_rectangle([x + 10, y, x + cw - 10, y + 72], radius=14, outline=(120, 120, 130), width=3)
                d.text((x + cw / 2, y + 36), "free", font=F(POP, 22), fill=GREY, anchor="mm")
    im.save(path, quality=95)


if __name__ == "__main__":
    cover("s1.png"); inputs("d1.png"); week("d2.png"); print("art ok")
