import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POP=os.path.join(_FD,"Poppins-Medium.ttf"); POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf"); VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
BLUE=(90,150,255); AMB=(255,206,84); MINT=(110,225,170); VIO=(170,140,255); PINK=(255,130,180)

def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))

def base(size, c1=(14,20,40), c2=(5,6,12), tint=(40,60,130)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=62)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)

def key(d,x,y,w,h,label,hot=False):
    d.rounded_rectangle([x,y+8,x+w,y+h+8],radius=18,fill=(20,24,40))
    d.rounded_rectangle([x,y,x+w,y+h],radius=18,fill=(236,240,250) if hot else (54,60,84),outline=BLUE if hot else (90,96,120),width=4)
    d.text((x+w/2,y+h/2),label,font=F(POPB,int(h*0.34)),fill=(20,26,50) if hot else (220,226,240),anchor="mm")

def laptop(d,cx,cy,w):
    h=w*0.6
    d.rounded_rectangle([cx-w/2,cy-h/2,cx+w/2,cy+h/2],radius=w*0.03,fill=(40,44,60),outline=(120,126,150),width=5)
    sx0,sy0,sx1,sy1=cx-w/2+w*0.03,cy-h/2+w*0.03,cx+w/2-w*0.03,cy+h/2-w*0.03
    d.rectangle([sx0,sy0,sx1,sy1],fill=(18,22,36))
    # a document the user is working in
    d.rectangle([sx0+w*0.05,sy0+w*0.05,sx0+w*0.5,sy1-w*0.05],fill=(230,232,240))
    for k in range(7):
        yy=sy0+w*0.09+k*w*0.042
        d.line([(sx0+w*0.08,yy),(sx0+w*(0.47 if k%3 else 0.36),yy)],fill=(160,166,184),width=int(w*0.012))
    # the assistant panel floating on top
    px0,py0,px1,py1=sx0+w*0.42,sy0+w*0.1,sx1-w*0.04,sy1-w*0.08
    d.rounded_rectangle([px0,py0,px1,py1],radius=w*0.03,fill=(34,40,70),outline=BLUE,width=4)
    d.rounded_rectangle([px0+w*0.03,py0+w*0.04,px1-w*0.08,py0+w*0.11],radius=w*0.02,fill=(70,90,160))
    d.rounded_rectangle([px0+w*0.08,py0+w*0.14,px1-w*0.03,py0+w*0.21],radius=w*0.02,fill=(230,234,246))
    d.rounded_rectangle([px0+w*0.03,py1-w*0.08,px1-w*0.03,py1-w*0.025],radius=w*0.02,fill=(18,22,40),outline=(90,110,180),width=2)
    # base
    d.polygon([(cx-w*0.58,cy+h/2),(cx+w*0.58,cy+h/2),(cx+w*0.5,cy+h/2+w*0.05),(cx-w*0.5,cy+h/2+w*0.05)],fill=(80,86,108))

def cover(path):
    W,H=1080,900
    im=base((W,H))
    def glow(d): d.rounded_rectangle([W*0.5-60,120,W*0.5+360,520],radius=60,fill=(70,120,255))
    im=ImageChops.add(im, glowlayer((W,H),glow,blur=70), scale=0.8)
    d=ImageDraw.Draw(im)
    laptop(d,W/2,330,720)
    kw,kh=250,120
    key(d,W/2+30,640,kw,kh,"Space",hot=True)
    d.text((W/2,700),"+",font=F(POPB,70),fill=(230,236,250),anchor="mm")
    key(d,W/2-30-200,640,200,kh,"Alt",hot=True)
    im.save(path,quality=95)

def keys(path):
    W,H=1080,360
    im=base((W,H),(14,18,34),(5,6,12),(30,50,110)); d=ImageDraw.Draw(im)
    key(d,W/2+40,80,300,140,"Space",hot=True)
    d.text((W/2,150),"+",font=F(POPB,80),fill=(230,236,250),anchor="mm")
    key(d,W/2-40-230,80,230,140,"Alt",hot=True)
    d.text((W/2,H-30),"روی مک: Option + Space",font=F(VS,32),fill=(180,190,215),anchor="ms",**FA)
    im.save(path,quality=95)

def uses(path):
    W,H=1080,400
    im=base((W,H),(14,18,34),(5,6,12),(30,50,110)); d=ImageDraw.Draw(im)
    items=[("جواب سریع",BLUE),("نوشتن پیام و ایمیل",MINT),("ایده‌پردازی",AMB),("ساختن عکس",PINK),("تحقیق عمیق",VIO),("جیمیل و درایو",(120,210,255))]
    cols=2; bw=(W-150)/2; bh=96
    for i,(lab,col) in enumerate(items):
        r,c=divmod(i,cols)
        x1=W-50-c*(bw+50); x0=x1-bw; y0=30+r*(bh+24)
        d.rounded_rectangle([x0,y0,x1,y0+bh],radius=26,fill=(24,28,50),outline=col,width=3)
        d.ellipse([x1-70,y0+bh/2-16,x1-38,y0+bh/2+16],fill=col)
        d.text((x1-90,y0+bh/2),lab,font=F(VB,36),fill=(236,240,250),anchor="rm",**FA)
    im.save(path,quality=95)

def steps(path):
    W,H=1080,420
    im=base((W,H),(14,18,34),(5,6,12),(30,50,110)); d=ImageDraw.Draw(im)
    st=[("۱","برو به","gemini.google/desktop"),("۲","دانلود و نصب","Windows 10 / 11"),("۳","ورود با گوگل","Alt + Space")]
    bw=(W-160)/3
    for i,(n,t,s) in enumerate(st):
        x1=W-50-i*(bw+30); x0=x1-bw
        d.rounded_rectangle([x0,40,x1,360],radius=30,fill=(24,28,50),outline=(90,110,180),width=3)
        d.ellipse([(x0+x1)/2-44,70,(x0+x1)/2+44,158],fill=BLUE)
        d.text(((x0+x1)/2,114),n,font=F(VB,52),fill=(10,16,40),anchor="mm",**FA)
        d.text(((x0+x1)/2,210),t,font=F(VB,40),fill=(236,240,250),anchor="mm",**FA)
        fs=F(POPB,32)
        while d.textlength(s,font=fs)>bw-30 and fs.size>16: fs=F(POPB,fs.size-2)
        d.text(((x0+x1)/2,290),s,font=fs,fill=(170,190,235),anchor="mm")
    im.save(path,quality=95)

if __name__=="__main__":
    cover("s1.png"); keys("d1.png"); uses("d2.png"); steps("d3.png")
    print("art ok")
