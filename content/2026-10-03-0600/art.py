import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POP=os.path.join(_FD,"Poppins-Medium.ttf"); POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf"); VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
PINK=(255,120,180); AMB=(255,206,84); SKY=(110,190,255); MINT=(110,225,170); VIO=(170,140,255)

def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))

def base(size, c1=(26,16,40), c2=(7,6,12), tint=(70,40,110)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=62)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)

def face(d,cx,cy,r,skin,kind="jolly"):
    """Tiny cartoon avatars drawn from shapes."""
    if kind=="mango":
        d.ellipse([cx-r,cy-r*1.15,cx+r,cy+r*0.95],fill=(255,170,60))
        d.ellipse([cx-r*0.2,cy-r*1.35,cx+r*0.35,cy-r*1.0],fill=(90,190,90))
    elif kind=="dog":
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(214,170,120))
        d.ellipse([cx-r*1.15,cy-r*0.6,cx-r*0.55,cy+r*0.5],fill=(170,120,80))
        d.ellipse([cx+r*0.55,cy-r*0.6,cx+r*1.15,cy+r*0.5],fill=(170,120,80))
        d.ellipse([cx-r*0.18,cy+r*0.15,cx+r*0.18,cy+r*0.42],fill=(40,30,30))
    elif kind=="toast":
        d.rounded_rectangle([cx-r,cy-r*0.9,cx+r,cy+r],radius=r*0.35,fill=(230,180,110))
        d.rounded_rectangle([cx-r*0.82,cy-r*0.72,cx+r*0.82,cy+r*0.85],radius=r*0.28,fill=(250,225,170))
    else:
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=skin)
    # eyes
    ey=cy-r*0.12
    if kind=="toast":
        d.rounded_rectangle([cx-r*0.72,ey-r*0.2,cx-r*0.08,ey+r*0.16],radius=r*0.1,fill=(20,20,26))
        d.rounded_rectangle([cx+r*0.08,ey-r*0.2,cx+r*0.72,ey+r*0.16],radius=r*0.1,fill=(20,20,26))
        d.line([(cx-r*0.08,ey-r*0.05),(cx+r*0.08,ey-r*0.05)],fill=(20,20,26),width=max(2,int(r*0.08)))
    else:
        for sx in (-1,1):
            d.ellipse([cx+sx*r*0.36-r*0.13,ey-r*0.16,cx+sx*r*0.36+r*0.13,ey+r*0.1],fill=(22,22,30))
    d.arc([cx-r*0.4,cy+r*0.05,cx+r*0.4,cy+r*0.55],15,165,fill=(22,22,30),width=max(3,int(r*0.1)))

def charm(d,cx,cy,w,h,screen=True,kind="jolly"):
    d.rounded_rectangle([cx-w/2,cy-h/2,cx+w/2,cy+h/2],radius=w*0.26,fill=(232,234,242))
    sw,sh=w*0.78,h*0.7
    d.rounded_rectangle([cx-sw/2,cy-sh/2-h*0.04,cx+sw/2,cy+sh/2-h*0.04],radius=w*0.18,fill=(20,18,34))
    if screen: face(d,cx,cy-h*0.06,sw*0.3,(255,214,120),kind)
    fx,fy=cx+w*0.34,cy+h*0.40
    d.ellipse([fx-w*0.07,fy-w*0.07,fx+w*0.07,fy+w*0.07],fill=(180,184,198))
    for k in (0.02,0.04):
        d.arc([fx-w*k*1.4,fy-w*k*1.4,fx+w*k*1.4,fy+w*k*1.4],200,340,fill=(120,124,140),width=2)

def cover(path):
    W,H=1080,900
    im=base((W,H))
    cx,cy=W*0.5,H*0.52; w,h=300,340
    def glow(d):
        d.rounded_rectangle([cx-w/2-18,cy-h/2-18,cx+w/2+18,cy+h/2+18],radius=90,fill=(150,90,220))
    im=ImageChops.add(im, glowlayer((W,H),glow,blur=46), scale=1.2)
    d=ImageDraw.Draw(im)
    # lanyard
    d.line([(cx,cy-h/2-6),(cx-150,40)],fill=(255,120,180),width=14)
    d.line([(cx,cy-h/2-6),(cx+150,40)],fill=(255,120,180),width=14)
    d.ellipse([cx-22,cy-h/2-40,cx+22,cy-h/2+4],outline=(220,222,232),width=9)
    charm(d,cx,cy,w,h,kind="jolly")
    # little sparkles
    for sx,sy,s in ((0.2,0.35,14),(0.8,0.3,18),(0.75,0.7,12),(0.24,0.72,16)):
        x,y=W*sx,H*sy
        d.line([(x-s,y),(x+s,y)],fill=AMB,width=4); d.line([(x,y-s),(x,y+s)],fill=AMB,width=4)
    im.save(path,quality=95)

def howto(path):
    W,H=1080,380
    im=base((W,H),(22,14,34),(7,6,12),(56,34,90)); d=ImageDraw.Draw(im)
    # right: finger tapping the corner sensor (reads first in RTL)
    charm(d,W*0.8,H*0.5,190,220,kind="jolly")
    fx,fy=W*0.8+190*0.34,H*0.5+220*0.40
    d.ellipse([fx-30,fy-30,fx+30,fy+30],outline=AMB,width=6)
    d.text((W*0.8,H-26),"لمس اثر انگشت",font=F(VS,28),fill=(210,200,230),anchor="ms",**FA)
    # arrow to speech
    d.line([(W*0.64,H*0.5),(W*0.5,H*0.5)],fill=(200,190,230),width=6)
    d.polygon([(W*0.5,H*0.5),(W*0.53,H*0.5-14),(W*0.53,H*0.5+14)],fill=(200,190,230))
    # left: speech bubble
    bx0,by0,bx1,by1=60,70,W*0.46,H*0.66
    d.rounded_rectangle([bx0,by0,bx1,by1],radius=34,fill=(240,236,250))
    d.polygon([(bx1-70,by1),(bx1-30,by1),(bx1-20,by1+40)],fill=(240,236,250))
    d.text((bx1-34,by0+34),"یه ایمیل برای",font=F(VB,36),fill=(30,24,48),anchor="ra",**FA)
    d.text((bx1-34,by0+84),"استادم بنویس",font=F(VB,36),fill=(30,24,48),anchor="ra",**FA)
    d.text(((bx0+bx1)/2,H-26),"فقط حرف بزن",font=F(VS,28),fill=(210,200,230),anchor="ms",**FA)
    im.save(path,quality=95)

def tasks(path):
    W,H=1080,380
    im=base((W,H),(22,14,34),(7,6,12),(56,34,90)); d=ImageDraw.Draw(im)
    items=[("نوشتن ایمیل",SKY,"mail"),("گرفتن وقت",MINT,"cal"),("پیدا کردن اشتراک‌های اضافه",AMB,"card")]
    y=40
    for label,col,ic in items:
        d.rounded_rectangle([60,y,W-60,y+92],radius=26,fill=(28,22,44),outline=col,width=3)
        ix,iy=W-120,y+46
        if ic=="mail":
            d.rounded_rectangle([ix-30,iy-20,ix+30,iy+20],radius=6,outline=col,width=5)
            d.line([(ix-30,iy-20),(ix,iy+4),(ix+30,iy-20)],fill=col,width=5)
        elif ic=="cal":
            d.rounded_rectangle([ix-28,iy-24,ix+28,iy+26],radius=6,outline=col,width=5)
            d.line([(ix-28,iy-10),(ix+28,iy-10)],fill=col,width=5)
            for gx in (-12,4,18):
                d.rectangle([ix+gx-4,iy+2,ix+gx+4,iy+10],fill=col)
        else:
            d.rounded_rectangle([ix-32,iy-20,ix+32,iy+20],radius=6,outline=col,width=5)
            d.line([(ix-32,iy-6),(ix+32,iy-6)],fill=col,width=6)
        d.text((W-176,y+22),label,font=F(VB,38),fill=(236,232,246),anchor="ra",**FA)
        y+=112
    im.save(path,quality=95)

def avatars(path):
    W,H=1080,360
    im=base((W,H),(22,14,34),(7,6,12),(56,34,90)); d=ImageDraw.Draw(im)
    kinds=[("jolly","خندون"),("mango","انبه"),("dog","سگ پشمالو"),("toast","نون تست")]
    xs=[W-150-i*((W-300)/3) for i in range(4)]
    for (k,lab),x in zip(kinds,xs):
        d.rounded_rectangle([x-95,40,x+95,250],radius=40,fill=(20,18,34),outline=(90,80,130),width=3)
        face(d,x,140,62,(255,214,120),k)
        d.text((x,H-40),lab,font=F(VS,30),fill=(220,210,240),anchor="ms",**FA)
    im.save(path,quality=95)

if __name__=="__main__":
    cover("s1.png"); howto("d1.png"); tasks("d2.png"); avatars("d3.png")
    print("art ok")
