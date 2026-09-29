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
GR=(60,200,150); RED=(240,80,80); AMB=(255,206,84)
ROWS=[("MacBook · Chrome","Tehran",False),("iPhone · ChatGPT app","Tehran",False),("Windows · Edge","Unknown",True),("Android · ChatGPT app","Tehran",False)]
def sessions(d,x0,y0,w,rowh=96,title=True,btn=True):
    y=y0
    if title:
        d.text((x0+10,y),"Active sessions",font=F(POPB,40),fill=(240,242,248)); y+=70
    for dev,loc,bad in ROWS:
        d.rounded_rectangle([x0,y,x0+w,y+rowh-14],radius=18,fill=(58,24,28) if bad else (32,36,46),outline=RED if bad else (60,66,80),width=3)
        d.text((x0+26,y+14),dev,font=F(POPB,28),fill=(245,245,250))
        d.text((x0+26,y+48),loc,font=F(POP,24),fill=RED if bad else (160,166,180))
        if btn:
            bx=x0+w-150; d.rounded_rectangle([bx,y+20,bx+126,y+62],radius=20,fill=RED if bad else (52,56,70))
            d.text((bx+63,y+41),"Log out",font=F(POPB,22),fill=(255,255,255),anchor="mm")
        y+=rowh
    return y
def cover(path):
    W,H=1080,900
    im=base((W,H),(14,26,30),(4,6,8),(30,110,100))
    def glow(d): d.rounded_rectangle([160,90,920,860],radius=50,fill=(255,70,70))
    im=ImageChops.add(im,glowlayer((W,H),glow,90),scale=0.45)
    d=ImageDraw.Draw(im)
    d.rounded_rectangle([180,90,900,880],radius=48,fill=(18,20,26),outline=(80,86,100),width=5)
    d.rounded_rectangle([450,108,630,132],radius=12,fill=(40,44,54))
    sessions(d,220,180,640,rowh=130)
    # warning badge
    d.ellipse([820,420,940,540],fill=RED); d.text((880,478),"!",font=F(POPB,80),fill=(255,255,255),anchor="mm")
    im.save(path,quality=95)
def path_(path):
    W,H=1080,360
    im=base((W,H),(14,26,30),(4,6,8),(30,110,100)); d=ImageDraw.Draw(im)
    labs=["Settings","Security","Security history"]
    cw=290; gap=50; x=W-60-cw
    for i,t in enumerate(labs):
        col=GR if i==2 else (90,160,220)
        d.rounded_rectangle([x,60,x+cw,220],radius=26,fill=(26,32,40),outline=col,width=4)
        fa=F(POPB,34)
        while d.textlength(t,font=fa)>cw-30: fa=F(POPB,fa.size-2)
        d.text((x+cw/2,140),t,font=fa,fill=(240,244,248),anchor="mm")
        fatext(d,(x+cw/2,280),["تنظیمات","امنیت","تاریخچه‌ی امنیت"][i],F(VB,34),col,"ms")
        if i<2: d.polygon([(x-gap+8,140),(x-12,124),(x-12,156)],fill=(220,226,230))
        x-=cw+gap
    im.save(path,quality=95)
def list_(path):
    W,H=1080,590
    im=base((W,H),(14,26,30),(4,6,8),(30,110,100)); d=ImageDraw.Draw(im)
    y=sessions(d,90,30,900)
    d.rounded_rectangle([90,y+6,990,y+70],radius=30,fill=RED)
    d.text((540,y+38),"Log out of all sessions",font=F(POPB,30),fill=(255,255,255),anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); path_("d1.png"); list_("d2.png"); print("art ok")
