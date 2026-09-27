import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POP=os.path.join(_FD,"Poppins-Medium.ttf"); POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf"); VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
AMB=(255,206,84); TEAL=(90,210,200); WOOD=(120,78,44); WOOD2=(92,58,32); KEY=(34,32,30)

def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))

def base(size, c1=(30,24,16), c2=(6,6,8), tint=(90,64,28)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=62)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)

LETTERS="QWERTZUIOASDFGHJKPYXCVBNML"
def machine(d,x0,y0,w,lit=None):
    """Generic rotor cipher machine seen from above: wooden box, rotors, lampboard, keyboard."""
    h=w*0.82
    d.rounded_rectangle([x0,y0,x0+w,y0+h],radius=w*0.04,fill=WOOD,outline=WOOD2,width=int(w*0.012))
    # inner metal plate
    px0,py0,px1,py1=x0+w*0.05,y0+w*0.05,x0+w*0.95,y0+h-w*0.05
    d.rounded_rectangle([px0,py0,px1,py1],radius=w*0.03,fill=(40,38,36))
    # three rotors with letter windows
    rw=w*0.11; ry=py0+w*0.05
    for i in range(3):
        rx=x0+w*0.34+i*rw*1.3
        d.rounded_rectangle([rx,ry,rx+rw,ry+w*0.12],radius=rw*0.2,fill=(70,68,64))
        for k in range(5):
            yy=ry+w*0.012+k*w*0.02
            d.line([(rx+rw*0.1,yy),(rx+rw*0.9,yy)],fill=(100,96,90),width=2)
        d.rectangle([rx+rw*0.28,ry+w*0.13,rx+rw*0.72,ry+w*0.175],fill=(230,224,205))
        d.text((rx+rw*0.5,ry+w*0.152),"MVU"[i],font=F(POPB,int(w*0.03)),fill=(30,26,20),anchor="mm")
    # lampboard + keyboard rows
    rows=["QWERTZUIO","ASDFGHJK","PYXCVBNML"]
    r=w*0.028
    for block,(top,fill) in enumerate(((py0+w*0.27,"lamp"),(py0+w*0.49,"key"))):
        for ri,row in enumerate(rows):
            n=len(row); sp=w*0.085
            sx=x0+w/2-(n-1)*sp/2
            for ci,ch in enumerate(row):
                cx=sx+ci*sp; cy=top+ri*w*0.068
                if fill=="lamp":
                    on=(lit and ch in lit)
                    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=AMB if on else (58,56,52),outline=(90,86,80),width=2)
                    d.text((cx,cy),ch,font=F(POPB,int(r*1.1)),fill=(40,30,10) if on else (150,146,138),anchor="mm")
                else:
                    d.ellipse([cx-r*1.05,cy-r*1.05,cx+r*1.05,cy+r*1.05],fill=KEY,outline=(170,166,158),width=3)
                    d.text((cx,cy),ch,font=F(POPB,int(r*1.0)),fill=(225,222,214),anchor="mm")
    return h

def cover(path):
    W,H=1080,900
    im=base((W,H))
    mw=600; mx=(W-mw)/2; my=120
    def glow(d):
        d.rounded_rectangle([mx-20,my-20,mx+mw+20,my+mw*0.82+20],radius=40,fill=(255,170,60))
    im=ImageChops.add(im, glowlayer((W,H),glow,blur=60), scale=0.9)
    d=ImageDraw.Draw(im)
    machine(d,mx,my,mw,lit="ROSENW")
    # scrambled letter strips drifting into the machine from the left, clean text out on the right
    random.seed(7)
    fs=F(POPB,34)
    for k in range(7):
        y=my+40+k*70
        s="".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(4))
        d.text((40,y),s,font=fs,fill=(150,130,100))
    d.rounded_rectangle([W/2-250,my+mw*0.82+36,W/2+250,my+mw*0.82+104],radius=22,fill=(30,24,14),outline=AMB,width=3)
    d.text((W/2,my+mw*0.82+70),"ROSENOW  ROSENOW",font=F(POPB,40),fill=AMB,anchor="mm")
    d.text((W/2,70),"1941",font=F(POPB,58),fill=(235,225,200),anchor="mm")
    im.save(path,quality=95)

def timeline(path):
    W,H=1080,360
    im=base((W,H),(26,20,14),(6,6,8),(70,50,24)); d=ImageDraw.Draw(im)
    pts=[("۱۹۴۱","فرستاده شد",(200,190,170)),("۲۰۰۵","منتشر شد، حل‌نشده",(255,120,100)),("۲۰۲۶","شکسته شد",AMB)]
    y=150; d.line([(120,y),(W-120,y)],fill=(90,84,74),width=6)
    xs=[W-150,W/2,150]
    for (yr,lab,col),x in zip(pts,xs):
        d.ellipse([x-26,y-26,x+26,y+26],fill=col)
        d.text((x,y-50),yr,font=F(VB,50),fill=(240,236,226),anchor="ms",**FA)
        d.text((x,y+80),lab,font=F(VS,34),fill=col,anchor="ms",**FA)
    d.text((W/2,H-30),"پیام شماره‌ی ۱۷۲ · ۸۲ حرف",font=F(VS,30),fill=(180,172,158),anchor="ms",**FA)
    im.save(path,quality=95)

def crib(path):
    W,H=1080,380
    im=base((W,H),(26,20,14),(6,6,8),(70,50,24)); d=ImageDraw.Draw(im)
    # right box: solved message from the same day
    d.rounded_rectangle([W*0.54,40,W-50,230],radius=26,fill=(30,26,20),outline=TEAL,width=3)
    d.text((W-80,64),"پیام حل‌شده‌ی همون روز",font=F(VB,32),fill=TEAL,anchor="ra",**FA)
    d.text((W*0.77,160),"ROSENOW ROSENOW",font=F(POPB,40),fill=(235,230,220),anchor="mm")
    # arrow
    d.line([(W*0.52,135),(W*0.47,135)],fill=(220,210,190),width=6)
    d.polygon([(W*0.45,135),(W*0.48,120),(W*0.48,150)],fill=(220,210,190))
    # left box: code the model wrote
    d.rounded_rectangle([50,40,W*0.44,230],radius=26,fill=(30,26,20),outline=AMB,width=3)
    d.text((W*0.44-30,64),"کدی که خودش نوشت",font=F(VB,32),fill=AMB,anchor="ra",**FA)
    d.text((80,125),"Python  ·  C++",font=F(POPB,34),fill=(235,230,220))
    d.text((80,172),"simulator + bombe",font=F(POP,30),fill=(190,182,168))
    d.text((W/2,H-40),"حدس زد همین کلمه تو پیام ۱۷۲ هم هست",font=F(VS,32),fill=(200,192,176),anchor="ms",**FA)
    im.save(path,quality=95)

def funnel(path):
    W,H=1080,400
    im=base((W,H),(26,20,14),(6,6,8),(70,50,24)); d=ImageDraw.Draw(im)
    d.polygon([(90,50),(W-90,50),(W/2+70,300),(W/2-70,300)],fill=(52,44,34),outline=(120,106,84))
    random.seed(3)
    for _ in range(170):
        t=random.random(); y=60+t*200; half=(W/2-90)*(1-t)+70*t-20
        x=W/2+random.uniform(-half,half)
        d.ellipse([x-5,y-5,x+5,y+5],fill=(160,146,120))
    tw=d.textlength("۴٫۲۹ میلیارد حالت",font=F(VB,50),**FA)
    d.rounded_rectangle([W/2-tw/2-30,78,W/2+tw/2+30,146],radius=24,fill=(20,16,12),outline=(120,106,84),width=2)
    d.text((W/2,112),"۴٫۲۹ میلیارد حالت",font=F(VB,50),fill=(245,240,230),anchor="mm",**FA)
    d.rounded_rectangle([W/2-150,310,W/2+150,380],radius=30,fill=AMB)
    d.text((W/2,345),"۱ کلید",font=F(VB,44),fill=(30,22,8),anchor="mm",**FA)
    im.save(path,quality=95)

if __name__=="__main__":
    cover("s1.png"); timeline("d1.png"); crib("d2.png"); funnel("d3.png")
    print("art ok")
