import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf"); VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf"); VK=os.path.join(_FD,"Vazirmatn-Black.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
TEAL=(80,210,190); AMB=(255,206,84); PINK=(255,120,150); SKY=(120,180,255); SKIN=(240,190,150); WHITE=(240,240,245)
def base(size, c1=(14,34,40), c2=(5,8,10), tint=(30,110,120)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=70)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)
def glow(im,fn,blur=40,scale=0.6):
    l=Image.new("RGB",im.size,(0,0,0)); fn(ImageDraw.Draw(l))
    return ImageChops.add(im,l.filter(ImageFilter.GaussianBlur(blur)),scale=scale)
def fat(d,xy,t,f,fill,anchor="mm"): d.text(xy,t,font=f,fill=fill,anchor=anchor,**FA)
def head(d,cx,cy,r,col=SKIN,eyes="open",mouth="line"):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
    ey=cy-r*0.15
    for s in (-1,1):
        ex=cx+s*r*0.38
        if eyes=="open": d.ellipse([ex-r*0.09,ey-r*0.09,ex+r*0.09,ey+r*0.09],fill=(30,30,36))
        else: d.arc([ex-r*0.16,ey-r*0.12,ex+r*0.16,ey+r*0.12],20,160,fill=(30,30,36),width=max(3,int(r*0.06)))
    if mouth=="line": d.line([(cx-r*0.25,cy+r*0.42),(cx+r*0.25,cy+r*0.42)],fill=(30,30,36),width=max(3,int(r*0.06)))
    elif mouth=="yawn": d.ellipse([cx-r*0.22,cy+r*0.18,cx+r*0.22,cy+r*0.72],fill=(90,30,40))
    elif mouth=="sneeze": d.ellipse([cx-r*0.12,cy+r*0.3,cx+r*0.12,cy+r*0.52],fill=(90,30,40))
def icon_bed(d,x,y,s):
    d.rounded_rectangle([x,y+s*0.45,x+s*1.6,y+s*0.75],radius=int(s*0.08),fill=(70,90,140))
    d.rectangle([x,y+s*0.75,x+s*0.08,y+s],fill=(70,90,140)); d.rectangle([x+s*1.52,y+s*0.75,x+s*1.6,y+s],fill=(70,90,140))
    d.rounded_rectangle([x+s*0.05,y+s*0.3,x+s*0.45,y+s*0.5],radius=int(s*0.08),fill=WHITE)
    head(d,x+s*0.28,y+s*0.18,s*0.16,eyes="closed",mouth="none")
    d.rounded_rectangle([x+s*0.4,y+s*0.3,x+s*1.55,y+s*0.52],radius=int(s*0.1),fill=SKY)
def sun(d,cx,cy,r,col=AMB):
    for k in range(12):
        a=math.radians(k*30); d.line([(cx+math.cos(a)*r*1.3,cy+math.sin(a)*r*1.3),(cx+math.cos(a)*r*1.75,cy+math.sin(a)*r*1.75)],fill=col,width=max(4,int(r*0.14)))
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
def cone(d,cx,cy,s):
    d.polygon([(cx-s*0.35,cy),(cx+s*0.35,cy),(cx,cy+s*1.1)],fill=(214,160,90))
    for k in range(1,4): d.line([(cx-s*0.35+k*s*0.15,cy),(cx,cy+s*1.1)],fill=(180,125,70),width=3)
    d.ellipse([cx-s*0.45,cy-s*0.55,cx+s*0.45,cy+s*0.2],fill=(255,190,210)); d.ellipse([cx-s*0.3,cy-s*0.85,cx+s*0.3,cy-s*0.25],fill=(170,230,210))
def flake(d,cx,cy,r,col=SKY,w=6):
    for k in range(6):
        a=math.radians(k*60); ex,ey=cx+math.cos(a)*r,cy+math.sin(a)*r
        d.line([(cx,cy),(ex,ey)],fill=col,width=w)
        for s in (-1,1):
            b=a+s*math.radians(35); mx,my=cx+math.cos(a)*r*0.6,cy+math.sin(a)*r*0.6
            d.line([(mx,my),(mx+math.cos(b)*r*0.3,my+math.sin(b)*r*0.3)],fill=col,width=max(2,w-2))
def hand(d,x,y,s,wr=True):
    d.rounded_rectangle([x,y+s*0.9,x+s*1.1,y+s*1.9],radius=int(s*0.3),fill=SKIN)
    for i in range(4):
        fx=x+s*0.05+i*s*0.27; top=y+[0.25,0.05,0.12,0.35][i]*s
        d.rounded_rectangle([fx,top,fx+s*0.22,y+s*1.1],radius=int(s*0.11),fill=SKIN)
        if wr:
            for k in range(4):
                yy=top+s*0.08+k*s*0.07
                d.arc([fx+s*0.03,yy,fx+s*0.19,yy+s*0.06],0,180,fill=(190,130,100),width=3)
    d.rounded_rectangle([x+s*0.95,y+s*1.0,x+s*1.4,y+s*1.25],radius=int(s*0.12),fill=SKIN)
def drop(d,cx,cy,r,col=SKY):
    d.polygon([(cx,cy-r*1.8),(cx-r*0.85,cy-r*0.3),(cx+r*0.85,cy-r*0.3)],fill=col); d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
def dog(d,cx,cy,r,mouth="yawn"):
    col=(200,150,100)
    for s in (-1,1): d.ellipse([cx+s*r*0.95-r*0.3,cy-r*0.9,cx+s*r*0.95+r*0.3,cy+r*0.2],fill=(150,100,65))
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
    d.ellipse([cx-r*0.5,cy+r*0.05,cx+r*0.5,cy+r*0.85],fill=(235,205,170))
    for s in (-1,1): d.arc([cx+s*r*0.38-r*0.15,cy-r*0.35,cx+s*r*0.38+r*0.15,cy-r*0.12],20,160,fill=(30,30,36),width=5)
    d.ellipse([cx-r*0.14,cy+r*0.05,cx+r*0.14,cy+r*0.25],fill=(40,30,30))
    if mouth=="yawn": d.ellipse([cx-r*0.2,cy+r*0.35,cx+r*0.2,cy+r*0.8],fill=(90,30,40))


class Shift:
    def __init__(s,d,dy): s.d=d; s.dy=dy
    def _sh(s,a):
        if isinstance(a,(list,tuple)) and a and isinstance(a[0],(list,tuple)): return [(p[0],p[1]+s.dy) for p in a]
        if isinstance(a,(list,tuple)): return [v+(s.dy if i%2 else 0) for i,v in enumerate(a)]
        return a
    def __getattr__(s,n):
        f=getattr(s.d,n)
        def g(a,*r,**k): return f(s._sh(a),*r,**k)
        return g
    def textlength(s,*a,**k): return s.d.textlength(*a,**k)
def canvas(tint=(30,110,120),H=600,dy=90):
    im=base((1080,H),tint=tint); return im, Shift(ImageDraw.Draw(im),dy)

def cover(path):
    W,H=1080,900; im=base((W,H))
    im=glow(im,lambda d:d.ellipse([340,180,740,580],fill=(40,160,150)),80,0.7); d=ImageDraw.Draw(im)
    # central silhouette
    d.ellipse([440,170,640,370],fill=(30,70,80)); d.rounded_rectangle([390,380,690,760],radius=110,fill=(30,70,80))
    d.ellipse([478,208,602,332],outline=TEAL,width=4)
    fat(d,(540,560),"؟",F(VK,210),TEAL)
    # five icons around
    icon_bed(d,70,120,150)
    sun(d,905,190,55)
    cone(d,150,470,110)
    head(d,930,420,75,mouth="yawn",eyes="closed")
    hand(d,800,520,80)
    for (x,y) in [(760,560),(960,600)]: drop(d,x,y,14)
    im.save(path,quality=95)
def jerk(path):
    W,H=1080,420; im,d=canvas()
    icon_bed(d,380,70,320)
    # jolt lines
    for (x,y) in [(430,60),(570,40),(710,55)]:
        d.line([(x,y),(x+20,y+30),(x-5,y+45),(x+18,y+80)],fill=AMB,width=8)
    fat(d,(960,110),"Zz",F(POPB,70),SKY)
    fat(d,(170,210),"۷۰ درصد",F(VK,72),AMB); fat(d,(170,300),"تجربه‌اش کردن",F(VB,44),WHITE)
    im.save(path,quality=95)
def sneeze(path):
    W,H=1080,420; im,d=canvas((120,100,30))
    sun(d,880,200,85)
    head(d,560,210,110,eyes="closed",mouth="sneeze")
    for k in range(7):
        a=math.radians(160+k*14); d.line([(490+math.cos(a)*40,260+math.sin(a)*20),(490+math.cos(a)*130,260+math.sin(a)*80)],fill=WHITE,width=5)
    fat(d,(150,180),"۱۸ تا ۳۵",F(VK,72),AMB); fat(d,(150,260),"درصد آدم‌ها",F(VB,44),WHITE)
    im.save(path,quality=95)
def freeze(path):
    W,H=1080,420; im,d=canvas((40,90,170))
    head(d,640,230,130,eyes="closed",mouth="line")
    flake(d,640,150,55,col=(200,230,255),w=7)
    cone(d,330,210,130)
    d.line([(760,300),(900,300)],fill=TEAL,width=6); d.polygon([(760,300),(790,284),(790,316)],fill=TEAL)
    fat(d,(1000,370),"زبون به سقف دهن",F(VB,44),TEAL,"ra")
    im.save(path,quality=95)
def yawn(path):
    W,H=1080,420; im,d=canvas()
    head(d,720,200,120,eyes="closed",mouth="yawn")
    dog(d,380,220,110)
    d.line([(560,200),(500,200)],fill=AMB,width=6); d.polygon([(495,200),(520,186),(520,214)],fill=AMB)
    fat(d,(150,170),"۲۱ از ۲۹",F(VK,64),AMB); fat(d,(150,250),"سگ",F(VB,46),WHITE)
    im.save(path,quality=95)
def fingers(path):
    W,H=1080,440; im=base((W,600),tint=(30,90,160))
    im=glow(im,lambda dd:dd.rectangle([0,400,W,600],fill=(20,80,140)),30,0.8); d=Shift(ImageDraw.Draw(im),80)
    hand(d,560,40,190)
    for (x,y) in [(440,120),(500,260),(920,150),(980,300)]: drop(d,x,y,14)
    # nerve line
    pts=[(640+i*20,420-abs(math.sin(i*0.9))*18) for i in range(10)]
    d.line(pts,fill=AMB,width=6)
    fat(d,(230,170),"کار عصب‌هاست",F(VK,52),AMB); fat(d,(230,250),"نه آب",F(VB,48),WHITE)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); jerk("d1.png"); sneeze("d2.png"); freeze("d3.png"); yawn("d4.png"); fingers("d5.png"); print("art ok")
