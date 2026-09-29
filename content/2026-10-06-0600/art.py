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
RED=(235,70,70); AMB=(255,206,84); TEAL=(80,210,190); PINK=(255,110,150)
def scene(d,x0,y0,w,h):
    d.rounded_rectangle([x0,y0,x0+w,y0+h],radius=26,fill=(60,66,80))
    rw=w*0.26; d.rectangle([x0,y0+h/2-rw/2,x0+w,y0+h/2+rw/2],fill=(38,40,48)); d.rectangle([x0+w/2-rw/2,y0,x0+w/2+rw/2,y0+h],fill=(38,40,48))
    for k in range(6):
        xx=x0+w/2+rw/2+10+k*22; d.rectangle([xx,y0+h/2+rw/2+4,xx+12,y0+h/2+rw/2+60],fill=(230,230,236))
    # generic octagon stop sign
    sx,sy,r=x0+w*0.78,y0+h*0.2,h*0.1
    d.line([(sx,sy),(sx,sy+r*2.4)],fill=(180,180,190),width=6)
    d.polygon([(sx+r*math.cos(math.radians(22.5+45*i)),sy+r*math.sin(math.radians(22.5+45*i))) for i in range(8)],fill=RED,outline=(255,255,255))
    # car
    cx,cy=x0+w*0.42,y0+h/2-rw*0.18
    d.rounded_rectangle([cx-70,cy-34,cx+70,cy+34],radius=16,fill=RED); d.rounded_rectangle([cx-30,cy-26,cx+30,cy+26],radius=8,fill=(120,170,220))
    # pedestrian
    px,py=x0+w*0.66,y0+h/2+rw*0.62
    d.ellipse([px-14,py-70,px+14,py-42],fill=AMB); d.line([(px,py-42),(px,py)],fill=AMB,width=10)
    d.line([(px,py),(px-16,py+34)],fill=AMB,width=9); d.line([(px,py),(px+16,py+34)],fill=AMB,width=9)
    d.line([(px,py-30),(px-22,py-8)],fill=AMB,width=8); d.line([(px,py-30),(px+22,py-8)],fill=AMB,width=8)
def cover(path):
    W,H=1080,900
    im=base((W,H),(30,16,30),(6,4,8),(120,40,90))
    d=ImageDraw.Draw(im)
    scene(d,70,150,620,460)
    def glow(d2): d2.rounded_rectangle([560,380,1020,800],radius=30,fill=(255,90,150))
    im=ImageChops.add(im,glowlayer((W,H),glow,50),scale=0.6); d=ImageDraw.Draw(im)
    d.rounded_rectangle([560,380,1020,800],radius=30,fill=(30,26,36),outline=PINK,width=4)
    d.text((600,420),"AI SUMMARY",font=F(POPB,32),fill=PINK)
    y=490
    for k in range(7):
        if k in (2,3):
            for xx in range(600,980,26): d.rectangle([xx,y,xx+12,y+14],fill=(110,90,110))
        else: d.rectangle([600,y,980-(k%3)*60,y+14],fill=(200,196,210))
        y+=40
    im.save(path,quality=95)
def flow(path):
    W,H=1080,380
    im=base((W,H),(30,16,30),(6,4,8),(120,40,90)); d=ImageDraw.Draw(im)
    labs=[("ویدیوی تصادف",TEAL),("خلاصه‌ی هوش مصنوعی",PINK),("تست حافظه",AMB)]
    cw=290; gap=50; x=W-60-cw
    for i,(t,col) in enumerate(labs):
        d.rounded_rectangle([x,40,x+cw,300],radius=26,fill=(30,26,36),outline=col,width=4)
        cx=x+cw/2
        if i==0:
            d.rounded_rectangle([cx-90,80,cx+90,190],radius=12,fill=(60,66,80)); d.polygon([(cx-20,110),(cx-20,160),(cx+25,135)],fill=(255,255,255))
        elif i==1:
            for k in range(4):
                if k==2:
                    for xx in range(int(cx-90),int(cx+90),22): d.rectangle([xx,90+k*28,xx+10,102+k*28],fill=(110,90,110))
                else: d.rectangle([cx-90,90+k*28,cx+90-(k%2)*40,102+k*28],fill=(200,196,210))
        else:
            for k in range(3):
                d.ellipse([cx-90,86+k*36,cx-66,110+k*36],outline=col,width=3); d.rectangle([cx-50,94+k*36,cx+90,104+k*36],fill=(200,196,210))
            d.ellipse([cx-86,126,cx-70,142],fill=col)
        fa=F(VB,34)
        while d.textlength(t,font=fa,**FA)>cw-30: fa=F(VB,fa.size-2)
        fatext(d,(cx,260),t,fa,(240,240,245),"ms")
        if i<2: d.polygon([(x-gap+8,170),(x-12,154),(x-12,186)],fill=(220,210,220))
        x-=cw+gap
    im.save(path,quality=95)
def bars(path):
    W,H=1080,460
    im=base((W,H),(30,16,30),(6,4,8),(120,40,90)); d=ImageDraw.Draw(im)
    data=[("خلاصه‌ی درست",83.6,TEAL,"۸۳٫۶٪"),("خلاصه‌ی گمراه‌کننده",44.8,PINK,"۴۴٫۸٪")]
    y=60
    for lab,v,col,txt in data:
        fatext(d,(W-60,y),lab,F(VB,38),(235,235,240),"ra")
        d.rounded_rectangle([60,y+60,W-60,y+130],radius=35,fill=(44,38,50))
        x1=W-60; x0=x1-(W-120)*v/100
        d.rounded_rectangle([x0,y+60,x1,y+130],radius=35,fill=col)
        fatext(d,(x0+24,y+95),txt,F(VK,44),(20,14,20),"lm")
        y+=190
    fatext(d,(W/2,H-24),"جواب درست درباره‌ی تابلوی سر چهارراه",F(VS,30),(190,180,195),"ms")
    im.save(path,quality=95)
def donut(path):
    W,H=1080,420
    im=base((W,H),(30,16,30),(6,4,8),(120,40,90)); d=ImageDraw.Draw(im)
    cx,cy,r=W*0.72,H/2,160
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=PINK)
    d.pieslice([cx-r,cy-r,cx+r,cy+r],-90,-90+360*0.05,fill=TEAL)
    d.ellipse([cx-r*0.62,cy-r*0.62,cx+r*0.62,cy+r*0.62],fill=(30,20,32))
    fatext(d,(cx,cy),"۹۵٪",F(VK,76),(255,255,255),"mm")
    fatext(d,(W*0.36,cy-50),"اصلا تصادف رو",F(VB,44),(240,236,240),"mm")
    fatext(d,(W*0.36,cy+20),"ننوشته بودن",F(VB,44),PINK,"mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); flow("d1.png"); donut("d2.png"); bars("d3.png"); print("art ok")
