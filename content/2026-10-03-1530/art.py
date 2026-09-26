import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POP=os.path.join(_FD,"Poppins-Medium.ttf"); POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf"); VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
RED=(255,96,96); AMB=(255,206,84); TEAL=(90,210,200); MAROON=(150,36,52); BLACKCAR=(38,40,48)

def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))

def base(size, c1=(14,20,30), c2=(5,6,10), tint=(30,54,80)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=62)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)

def suv(d,x,y,w,col,outline=None):
    """Side view of a boxy SUV, x,y = bottom-left of body."""
    h=w*0.34
    d.rounded_rectangle([x,y-h,x+w,y],radius=h*0.22,fill=col,outline=outline,width=4 if outline else 0)
    d.polygon([(x+w*0.18,y-h),(x+w*0.30,y-h*1.62),(x+w*0.80,y-h*1.62),(x+w*0.90,y-h)],fill=col)
    wc=(160,190,220) if col!=BLACKCAR else (110,130,150)
    d.polygon([(x+w*0.24,y-h*1.02),(x+w*0.33,y-h*1.52),(x+w*0.52,y-h*1.52),(x+w*0.52,y-h*1.02)],fill=wc)
    d.polygon([(x+w*0.56,y-h*1.02),(x+w*0.56,y-h*1.52),(x+w*0.77,y-h*1.52),(x+w*0.85,y-h*1.02)],fill=wc)
    for wx in (0.22,0.78):
        cx=x+w*wx; r=h*0.42
        d.ellipse([cx-r,y-r*0.7,cx+r,y+r*1.3],fill=(18,18,22))
        d.ellipse([cx-r*0.45,y-r*0.7+r*0.55,cx+r*0.45,y+r*1.3-r*0.55],fill=(120,124,134))

def camera(d,x,y,s):
    d.line([(x,y),(x,y+s*3.4)],fill=(90,96,110),width=int(s*0.22))
    d.rounded_rectangle([x-s*1.3,y-s*0.55,x+s*0.25,y+s*0.55],radius=s*0.18,fill=(200,206,218))
    d.ellipse([x-s*1.55,y-s*0.35,x-s*0.85,y+s*0.35],fill=(30,34,44))
    d.ellipse([x-s*1.36,y-s*0.16,x-s*1.04,y+s*0.16],fill=(80,170,255))

def cover(path):
    W,H=1080,900
    im=base((W,H))
    cx,cy=W*0.82,H*0.20
    def beam(d):
        d.polygon([(cx-60,cy),(W*0.08,H*0.66),(W*0.62,H*0.74)],fill=(60,150,255))
    im=ImageChops.add(im, glowlayer((W,H),beam,blur=40), scale=0.55)
    d=ImageDraw.Draw(im)
    # road
    d.rectangle([0,H*0.74,W,H*0.80],fill=(34,36,44))
    for x in range(20,W,120): d.rectangle([x,H*0.768,x+60,H*0.776],fill=(210,200,120))
    suv(d,W*0.14,H*0.74,440,BLACKCAR,outline=(90,96,112))
    # scan box on the car
    bx0,by0,bx1,by1=W*0.12,H*0.38,W*0.58,H*0.78
    for (a,b,c,e) in ((bx0,by0,bx0+50,by0),(bx0,by0,bx0,by0+50),(bx1-50,by0,bx1,by0),(bx1,by0,bx1,by0+50),
                      (bx0,by1-50,bx0,by1),(bx0,by1,bx0+50,by1),(bx1,by1-50,bx1,by1),(bx1-50,by1,bx1,by1)):
        d.line([(a,b),(c,e)],fill=AMB,width=8)
    d.rounded_rectangle([bx0,by0-66,bx0+330,by0-12],radius=12,fill=AMB)
    d.text((bx0+315,by0-40),"تطبیق پیدا شد",font=F(VB,34),fill=(30,24,10),anchor="rm",**FA)
    camera(d,cx,cy,52)
    im.save(path,quality=95)

def colours(path):
    W,H=1080,400
    im=base((W,H),(14,20,30),(5,6,10),(30,54,80)); d=ImageDraw.Draw(im)
    pw=(W-3*34)/2
    def panel(x,head,sub,col,car):
        d.rounded_rectangle([x,24,x+pw,H-24],radius=28,fill=(20,24,32),outline=col,width=3)
        d.text((x+pw-30,48),head,font=F(VB,32),fill=col,anchor="ra",**FA)
        suv(d,x+pw/2-140,H*0.63,280,car,outline=(100,106,122) if car==BLACKCAR else None)
        d.text((x+pw/2,H-42),sub,font=F(VS,28),fill=(206,212,224),anchor="ms",**FA)
    panel(34*2+pw,"شاهدها دیدن","دوج دورانگو زرشکی",(220,110,120),MAROON)
    panel(34,"دوربین ثبت کرد","دوج دورانگو مشکیِ لیندزی",TEAL,BLACKCAR)
    im.save(path,quality=95)

def timeline(path):
    W,H=1080,360
    im=base((W,H),(14,20,30),(5,6,10),(30,54,80)); d=ImageDraw.Draw(im)
    y=H*0.44
    d.line([(120,y),(W-120,y)],fill=(74,82,96),width=6)
    nodes=[("اکتبر ۲۰۲۵","تصادف مرگبار",RED),
           ("آوریل ۲۰۲۶","بازداشت",AMB),
           ("۱۳ روز","زندان",AMB),
           ("مه ۲۰۲۶","اتهام‌ها لغو شد",TEAL),
           ("سپتامبر ۲۰۲۶","شهادت در سنا",TEAL)]
    xs=[W-120-i*((W-240)/4) for i in range(5)]
    for (lab,sub,col),x in zip(nodes,xs):
        d.ellipse([x-16,y-16,x+16,y+16],fill=col)
        d.ellipse([x-28,y-28,x+28,y+28],outline=col,width=3)
        d.text((x,y-50),lab,font=F(VB,30),fill=(238,240,246),anchor="ms",**FA)
        d.text((x,y+76),sub,font=F(VS,26),fill=(160,168,184),anchor="ms",**FA)
    im.save(path,quality=95)

def stat(path):
    W,H=1080,340
    im=base((W,H),(14,20,30),(5,6,10),(30,54,80)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([30,24,W-30,H-24],radius=30,fill=(20,24,32),outline=(62,70,86),width=3)
    d.text((W-80,70),"بیش از ۲۰۰ هزار",font=F(VB,74),fill=AMB,anchor="ra",**FA)
    d.text((W-80,176),"دوربین Flock فقط تو آمریکا نصب شده",font=F(VS,38),fill=(226,230,240),anchor="ra",**FA)
    d.text((W-80,236),"مدیرهای Flock دعوت سنا برای شهادت رو قبول نکردن",font=F(VS,30),fill=(160,168,184),anchor="ra",**FA)
    for i in range(6):
        camera(d,110+i*62,92,16)
    im.save(path,quality=95)

if __name__=="__main__":
    cover("s1.png"); colours("d1.png"); timeline("d2.png"); stat("d3.png")
    print("art ok")
