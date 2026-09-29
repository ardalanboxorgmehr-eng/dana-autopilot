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
CY=(90,200,255); VIO=(170,120,255); AMB=(255,206,84)
def cover(path):
    W,H=1080,900
    im=base((W,H),(14,18,40),(4,4,10),(40,50,140))
    cx,cy=W/2,470
    def glow(d):
        d.ellipse([cx-90,cy-90,cx+90,cy+90],fill=(120,160,255))
        for k in range(6):
            a=math.radians(k*60+30); d.line([(cx,cy),(cx+420*math.cos(a),cy+330*math.sin(a))],fill=(80,120,255),width=26)
    im=ImageChops.add(im,glowlayer((W,H),glow,50),scale=0.9)
    d=ImageDraw.Draw(im)
    # nine nested loops
    for i in range(9):
        r=70+i*34
        col=tuple(int(CY[j]*(1-i/9)+VIO[j]*(i/9)) for j in range(3))
        d.ellipse([cx-r,cy-r*0.62,cx+r,cy+r*0.62],outline=col,width=4 if i<8 else 7)
    # six outgoing particles (hexagon)
    for k in range(6):
        a=math.radians(k*60+30); x=cx+400*math.cos(a); y=cy+400*math.sin(a)*0.78
        d.line([(cx,cy),(x,y)],fill=(230,236,255),width=4)
        d.ellipse([x-16,y-16,x+16,y+16],fill=AMB)
    d.ellipse([cx-46,cy-46,cx+46,cy+46],fill=(255,255,255))
    d.text((W/2,70),"9 LOOPS",font=F(POPB,64),fill=(240,244,255),anchor="mm")
    im.save(path,quality=95)
def ladder(path):
    W,H=1080,500
    im=base((W,H),(14,18,40),(4,4,10),(40,50,140)); d=ImageDraw.Draw(im)
    bw=76; gap=26; x0=W-80-bw
    for i in range(9):
        n=i+1; h=30+n*30; x=x0-i*(bw+gap); y1=420
        col=AMB if n==9 else (CY if n<=8 else CY)
        if n==9: col=AMB
        elif n==8: col=(120,170,255)
        else: col=(70,90,140)
        d.rounded_rectangle([x,y1-h,x+bw,y1],radius=12,fill=col)
        d.text((x+bw/2,y1+34),str(n),font=F(POPB,34),fill=(220,226,240),anchor="mm")
    xb=x0-7*(bw+gap)+bw/2; fatext(d,(xb,420-270-18),"انسان",F(VB,32),(150,190,255),"ms")
    xa=x0-8*(bw+gap)+bw/2; d.text((xa,420-300-18),"Claude",font=F(POPB,32),fill=AMB,anchor="ms")
    fatext(d,(W-80,40),"تعداد لوپ",F(VB,34),(200,206,220),"ra")
    im.save(path,quality=95)
def cpus(path):
    W,H=1080,400
    im=base((W,H),(14,18,40),(4,4,10),(40,50,140)); d=ImageDraw.Draw(im)
    cols,rows=16,6; s=34; g=10; gw=cols*s+(cols-1)*g; x0=(W-gw)/2; y0=40
    for r in range(rows):
        for c in range(cols):
            x=x0+c*(s+g); y=y0+r*(s+g)
            d.rounded_rectangle([x,y,x+s,y+s],radius=6,fill=(40,60,110),outline=CY,width=2)
            d.rectangle([x+11,y+11,x+s-11,y+s-11],fill=CY)
    fatext(d,(W/2,y0+rows*(s+g)+56),"۹۶ پردازنده، یک هفته، بی‌وقفه",F(VB,40),(240,244,255),"mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); ladder("d1.png"); cpus("d2.png"); print("art ok")
