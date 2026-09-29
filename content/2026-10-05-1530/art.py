import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POP=os.path.join(_FD,"Poppins-Medium.ttf"); POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf"); VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf"); VK=os.path.join(_FD,"Vazirmatn-Black.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))
def base(size, c1=(18,22,40), c2=(6,6,10), tint=(40,60,130)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=62)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)
def fatext(d,xy,t,f,fill,anchor="ra"):
    d.text(xy,t,font=f,fill=fill,anchor=anchor,**FA)
BL=(70,130,255); GR=(60,200,150); AMB=(255,206,84); PAPER=(245,246,250)
def docwin(d,x0,y0,w,h,side=True):
    d.rounded_rectangle([x0,y0,x0+w,y0+h],radius=24,fill=(34,38,52))
    d.rounded_rectangle([x0,y0,x0+w,y0+54],radius=24,fill=(46,90,190)); d.rectangle([x0,y0+30,x0+w,y0+54],fill=(46,90,190))
    for k,c in enumerate([(255,95,87),(255,189,46),(40,200,64)]): d.ellipse([x0+22+k*30,y0+18,x0+40+k*30,y0+36],fill=c)
    sw=w*0.34 if side else 0
    px0,py0,px1,py1=x0+40,y0+84,x0+w-sw-30,y0+h-30
    d.rectangle([px0,py0,px1,py1],fill=PAPER)
    d.rectangle([px0+40,py0+40,px0+(px1-px0)*0.55,py0+62],fill=(40,44,60))
    random.seed(4)
    y=py0+100
    while y<py1-40:
        ww=random.uniform(0.6,0.95)*(px1-px0-80)
        d.rectangle([px1-40-ww,y,px1-40,y+12],fill=(190,196,210)); y+=30
    if side:
        sx0=x0+w-sw-10; d.rounded_rectangle([sx0,y0+84,x0+w-20,y0+h-30],radius=18,fill=(22,26,36),outline=GR,width=3)
        d.text((sx0+22,y0+106),"ChatGPT",font=F(POPB,30),fill=GR)
        by=y0+170
        for k,(bw,me) in enumerate([(0.8,1),(0.9,0),(0.6,1),(0.85,0)]):
            bx1=x0+w-40; bx0=bx1-(sw-60)*bw
            if not me: bx0=sx0+20; bx1=bx0+(sw-60)*bw
            d.rounded_rectangle([bx0,by,bx1,by+70],radius=16,fill=(50,56,76) if me else (32,60,52))
            by+=100
def cover(path):
    W,H=1080,900
    im=base((W,H),(16,22,44),(4,4,10),(40,70,160))
    def glow(d): d.rounded_rectangle([90,120,990,800],radius=40,fill=(60,110,255))
    im=ImageChops.add(im,glowlayer((W,H),glow,70),scale=0.7)
    d=ImageDraw.Draw(im); docwin(d,90,120,900,680)
    im.save(path,quality=95)
def uses(path):
    W,H=1080,420
    im=base((W,H),(16,22,44),(4,4,10),(40,70,160)); d=ImageDraw.Draw(im)
    items=[("خلاصه",GR),("پیش‌نویس",BL),("بازنویسی",AMB)]
    cw=290; gap=40; x=W-60-cw
    for t,col in items:
        d.rounded_rectangle([x,40,x+cw,380],radius=28,fill=(28,32,46),outline=col,width=4)
        cx=x+cw/2
        if t=="خلاصه":
            for k in range(5): d.rectangle([cx-90,90+k*26,cx+90-(k%2)*50,104+k*26],fill=(150,156,170))
            d.polygon([(cx-10,230),(cx+10,230),(cx,250)],fill=col)
            for k in range(2): d.rectangle([cx-70,262+k*22,cx+70,274+k*22],fill=col)
        elif t=="پیش‌نویس":
            for k in range(3): d.ellipse([cx-100+k*20,100+k*40,cx-80+k*20,120+k*40],fill=(150,156,170)); d.rectangle([cx-60+k*20,104+k*40,cx+60,116+k*40],fill=(150,156,170))
            d.rounded_rectangle([cx-80,230,cx+80,290],radius=8,fill=PAPER); d.rectangle([cx-60,245,cx+40,255],fill=col); d.rectangle([cx-60,265,cx+60,272],fill=(150,156,170))
        else:
            d.rectangle([cx-100,110,cx+100,128],fill=(255,120,110)); d.line([(cx-104,119),(cx+104,119)],fill=(40,20,20),width=3)
            d.rectangle([cx-80,150,cx+80,168],fill=col)
            d.rectangle([cx-100,200,cx+100,214],fill=(150,156,170)); d.rectangle([cx-60,240,cx+100,254],fill=(150,156,170))
        fatext(d,(cx,345),t,F(VB,40),(240,244,255),"ms")
        x-=cw+gap
    im.save(path,quality=95)
def steps(path):
    W,H=1080,400
    im=base((W,H),(16,22,44),(4,4,10),(40,70,160)); d=ImageDraw.Draw(im)
    labs=[("۱","Microsoft Marketplace","Get it now"),("۲","Word","ChatGPT"),("۳","Sign in","Free")]
    cw=300; gap=40; x=W-60-cw
    for n,a,b in labs:
        d.rounded_rectangle([x,50,x+cw,350],radius=28,fill=(28,32,46),outline=BL,width=3)
        d.ellipse([x+cw/2-40,76,x+cw/2+40,156],fill=BL); fatext(d,(x+cw/2,118),n,F(VK,48),(255,255,255),"mm")
        fa=F(POPB,30)
        while d.textlength(a,font=fa)>cw-30: fa=F(POPB,fa.size-2)
        d.text((x+cw/2,210),a,font=fa,fill=(235,238,245),anchor="mm")
        d.rounded_rectangle([x+50,255,x+cw-50,315],radius=30,fill=GR if n!="۲" else (46,90,190))
        d.text((x+cw/2,285),b,font=F(POPB,28),fill=(10,16,20) if n!="۲" else (255,255,255),anchor="mm")
        if x>200: d.polygon([(x-32,200),(x-10,186),(x-10,214)],fill=(200,206,220))
        x-=cw+gap
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); uses("d1.png"); steps("d2.png"); print("art ok")
