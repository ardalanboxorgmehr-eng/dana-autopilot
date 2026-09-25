import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POP=os.path.join(_FD,"Poppins-Medium.ttf")
POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf")
VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
RED=(255,92,92); AMB=(255,206,84); TEAL=(72,214,196)

def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))

def base(size, c1=(24,12,16), c2=(6,6,10), tint=(70,26,34)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=62)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)

def cross(d,cx,cy,r,col,w):
    d.line([(cx-r,cy-r),(cx+r,cy+r)],fill=col,width=w)
    d.line([(cx-r,cy+r),(cx+r,cy-r)],fill=col,width=w)

def tick(d,cx,cy,r,col,w):
    d.line([(cx-r,cy+r*0.1),(cx-r*0.2,cy+r*0.8)],fill=col,width=w)
    d.line([(cx-r*0.2,cy+r*0.8),(cx+r,cy-r*0.8)],fill=col,width=w)

def padlock(d,cx,cy,s,col,dark=(26,20,24)):
    """s = body half-width. Shackle is drawn first so the body overlaps its feet."""
    bw,bh=s*2.0,s*1.6
    top=cy-bh/2
    d.arc([cx-s*0.78,top-s*1.45,cx+s*0.78,top+s*0.55],180,360,fill=col,width=int(s*0.34))
    d.rounded_rectangle([cx-bw/2,top,cx+bw/2,cy+bh/2],radius=s*0.34,fill=col)
    d.ellipse([cx-s*0.19,cy-s*0.26,cx+s*0.19,cy+s*0.12],fill=dark)
    d.rounded_rectangle([cx-s*0.09,cy+s*0.02,cx+s*0.09,cy+s*0.44],radius=s*0.09,fill=dark)

def doc(d,x,y,w,h,col,lines=4):
    f=w*0.3
    d.polygon([(x,y),(x+w-f,y),(x+w,y+f),(x+w,y+h),(x,y+h)],fill=col)
    d.polygon([(x+w-f,y),(x+w,y+f),(x+w-f,y+f)],fill=(30,30,36))
    for i in range(lines):
        yy=y+h*0.36+i*(h*0.14)
        d.rounded_rectangle([x+w*0.16,yy,x+w*0.74,yy+h*0.055],radius=h*0.03,fill=(34,32,38))

def arrow(d,x1,y1,x2,y2,col,w,head=20):
    d.line([(x1,y1),(x2,y2)],fill=col,width=w)
    a=math.atan2(y2-y1,x2-x1)
    for s in (0.6,-0.6):
        d.line([(x2,y2),(x2-head*math.cos(a-s),y2-head*math.sin(a-s))],fill=col,width=w)

# ---------- cover: three refused requests, one way around ----------
def cover(path):
    W,H=1080,900
    im=base((W,H))
    wx=W*0.47; wtop=H*0.26; wbot=H*0.88
    ARC=[W*0.10, H*0.05, W*0.90, H*0.78]      # fully inside the canvas
    def wall(d,pad=0):
        d.rounded_rectangle([wx-40-pad,wtop-pad,wx+40+pad,wbot+pad],radius=28,fill=(96,104,124))
    def glowbits(d):
        wall(d,10)
        for yy in (0.44,0.60,0.76):
            d.line([(90,H*yy),(wx-70,H*yy)],fill=RED,width=26)
        d.arc(ARC,188,352,fill=AMB,width=26)
    im=ImageChops.add(im, glowlayer((W,H),glowbits,blur=30), scale=1.5)
    d=ImageDraw.Draw(im)
    wall(d)
    for y in range(int(wtop)+26,int(wbot)-12,48):
        d.line([(wx-34,y),(wx+34,y)],fill=(70,76,94),width=3)
    padlock(d,wx,H*0.58,46,(226,230,240))
    for yy in (0.44,0.60,0.76):
        y=H*yy
        arrow(d,90,y,wx-84,y,RED,11,22)
        cross(d,wx-50,y,17,RED,9)
    d.arc(ARC,188,352,fill=AMB,width=12)
    # the arc ends near the right, drop an arrow from there into the file
    cx0,cy0=(ARC[0]+ARC[2])/2,(ARC[1]+ARC[3])/2
    rx,ry=(ARC[2]-ARC[0])/2,(ARC[3]-ARC[1])/2
    ex,ey=cx0+rx*math.cos(math.radians(352)), cy0+ry*math.sin(math.radians(352))
    arrow(d,ex,ey,ex+16,ey+74,AMB,12,24)
    doc(d,W*0.79,H*0.46,160,208,(236,238,244))
    im.save(path,quality=95)

# ---------- d1: how long the silence lasted ----------
def timeline(path):
    W,H=1080,340
    im=base((W,H),(20,14,18),(7,7,11),(54,28,36)); d=ImageDraw.Draw(im)
    y=H*0.44
    d.line([(150,y),(W-150,y)],fill=(74,78,92),width=6)
    # right to left, the way the page reads
    nodes=[("۱۸ ژوئن","اتفاق افتاد",RED),
           ("۱۱ آگوست","خودشون فهمیدن",AMB),
           ("۱۰ سپتامبر","ایمیل زدن",AMB),
           ("۲۴ سپتامبر","عمومی شد",TEAL)]
    xs=[W-150-i*((W-300)/3) for i in range(4)]
    for (lab,sub,col),x in zip(nodes,xs):
        d.ellipse([x-17,y-17,x+17,y+17],fill=col)
        d.ellipse([x-30,y-30,x+30,y+30],outline=col,width=3)
        d.text((x,y-52),lab,font=ImageFont.truetype(VB,34),fill=(240,240,245),anchor="ms",**FA)
        d.text((x,y+80),sub,font=ImageFont.truetype(VS,27),fill=(155,160,172),anchor="ms",**FA)
    d.text((W/2,H-22),"سه ماه از اتفاق تا خبر دادن",
           font=ImageFont.truetype(VS,28),fill=(150,140,148),anchor="ms",**FA)
    im.save(path,quality=95)

# ---------- d2: what it touched, what stayed out of reach ----------
def touched(path):
    W,H=1080,420
    im=base((W,H),(20,14,18),(7,7,11),(54,28,36)); d=ImageDraw.Draw(im)
    pw=(W-3*34)/2
    def panel(x,col,head,items,mark):
        r=x+pw-32                     # right edge for RTL text
        d.rounded_rectangle([x,26,x+pw,H-26],radius=28,fill=(24,24,30),outline=col,width=3)
        d.text((r,48),head,font=ImageFont.truetype(VB,33),fill=col,anchor="ra",**FA)
        yy=124
        for it in items:
            if mark=="dot": d.ellipse([r-58,yy+12,r-40,yy+30],fill=col)
            else: tick(d,r-49,yy+20,13,col,7)
            for ln in it:
                d.text((r-84,yy),ln,font=ImageFont.truetype(VS,30),fill=(214,216,224),anchor="ra",**FA)
                yy+=42
            yy+=18
    panel(34*2+pw,AMB,"چی رو دید",
          [["آمار کلی سلامت"],
           ["اسم فایل‌های داخلی"],
           ["روی سرورها فایل هم نوشت",
            "(در حال بررسی)"]],"dot")
    panel(34,TEAL,"چی امن موند",
          [["پرونده‌های شخصی مدیکر"],
           ["بقیه‌ی شبکه‌ی",
            "سرویسز استرالیا"]],"tick")
    im.save(path,quality=95)

# ---------- d3: OpenAI's own words ----------
def quote(path):
    W,H=1080,360
    im=base((W,H),(20,14,18),(7,7,11),(54,28,36)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([30,26,W-30,H-26],radius=30,fill=(24,24,30),outline=(62,62,72),width=3)
    d.text((72,40),"“",font=F(POPB,140),fill=AMB)
    d.text((150,118),"took actions we did not intend",font=F(POPB,50),fill=(240,240,245))
    d.text((W-60,196),"حرف خود OpenAI درباره‌ی کاری که مدل‌هاش کردن",font=ImageFont.truetype(VS,30),fill=(168,172,184),anchor="ra",**FA)
    d.text((W-60,244),"یعنی کاری کردن که نمی‌خواستیم",font=ImageFont.truetype(VS,30),fill=(168,172,184),anchor="ra",**FA)
    im.save(path,quality=95)

if __name__=="__main__":
    cover("s1.png"); timeline("d1.png"); touched("d2.png"); quote("d3.png")
    print("art ok")
