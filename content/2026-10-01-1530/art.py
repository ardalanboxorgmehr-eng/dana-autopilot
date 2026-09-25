import math, os, random
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
POP="/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
POPB="/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
def F(p,s): return ImageFont.truetype(p,s)
MINT=(110,230,190); BLU=(120,170,255); AMB=(255,206,84); VIO=(160,140,255)
def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); fn(ImageDraw.Draw(l)); return l.filter(ImageFilter.GaussianBlur(blur))
def base(size, c1=(14,20,34), c2=(5,7,12), tint=(30,50,90)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H; d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.8],fill=64)
    return Image.composite(Image.new("RGB",size,tint),im,g.filter(ImageFilter.GaussianBlur(160)))

def cover(path):
    W,H=1080,900
    im=base((W,H)); cx,cy=W//2,int(H*0.42)
    def rings(d,w=4):
        for i,r in enumerate([150,215,285,360]):
            col=[MINT,BLU,VIO,(80,110,190)][i]
            d.ellipse([cx-r,cy-r,cx+r,cy+r],outline=col,width=w)
    im=ImageChops.add(im, glowlayer((W,H),lambda d:rings(d,14),blur=34), scale=1.5)
    d=ImageDraw.Draw(im); rings(d)
    d.ellipse([cx-92,cy-92,cx+92,cy+92],fill=(16,26,42),outline=MINT,width=5)
    # mic glyph
    d.rounded_rectangle([cx-24,cy-46,cx+24,cy+16],radius=24,fill=MINT)
    d.arc([cx-44,cy-22,cx+44,cy+44],start=0,end=180,fill=MINT,width=8)
    d.line([(cx,cy+44),(cx,cy+64)],fill=MINT,width=8)
    # waveform band
    random.seed(11); y0=int(H*0.80)
    def bars(d,pad=0):
        x=40
        while x<W-40:
            h=int(18+abs(math.sin(x/61.0))*120*random.uniform(0.45,1.0))
            col=MINT if (x//86)%2 else BLU
            d.rounded_rectangle([x-pad,y0-h//2-pad,x+16+pad,y0+h//2+pad],radius=9,fill=col)
            x+=30
    im=ImageChops.add(im, glowlayer((W,H),lambda d:bars(d,6),blur=22), scale=1.7)
    d=ImageDraw.Draw(im); bars(d)
    im.save(path,quality=95)

def plugins(path):
    W,H=1080,360
    im=base((W,H),(12,20,32),(6,9,15)); d=ImageDraw.Draw(im)
    items=[("Email",MINT,"mail"),("Calendar",BLU,"cal"),("Slack",VIO,"chat")]
    bw=320; gap=40; x0=(W-(bw*3+gap*2))//2
    for i,(lab,col,gl) in enumerate(items):
        x=x0+i*(bw+gap); y=70
        d.rounded_rectangle([x,y,x+bw,y+200],radius=28,fill=(20,26,40),outline=col,width=4)
        ix,iy=x+bw//2,y+78
        if gl=="mail":
            d.rounded_rectangle([ix-46,iy-30,ix+46,iy+30],radius=10,outline=col,width=6)
            d.line([(ix-46,iy-30),(ix,iy+6),(ix+46,iy-30)],fill=col,width=6)
        elif gl=="cal":
            d.rounded_rectangle([ix-44,iy-32,ix+44,iy+32],radius=10,outline=col,width=6)
            d.line([(ix-44,iy-8),(ix+44,iy-8)],fill=col,width=6)
            d.line([(ix-22,iy-46),(ix-22,iy-20)],fill=col,width=6); d.line([(ix+22,iy-46),(ix+22,iy-20)],fill=col,width=6)
        else:
            d.rounded_rectangle([ix-46,iy-32,ix+46,iy+26],radius=16,outline=col,width=6)
            d.polygon([(ix-16,iy+24),(ix+6,iy+24),(ix-8,iy+48)],fill=col)
        d.text((ix,y+140),lab,font=F(POPB,40),fill=(235,242,250),anchor="ma")
    im.save(path,quality=95)

def flow(path):
    W,H=1080,420
    im=base((W,H),(12,20,32),(6,9,15)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([40,150,300,270],radius=26,fill=(22,34,30),outline=MINT,width=4)
    d.text((170,178),"you talk",font=F(POPB,40),fill=MINT,anchor="ma")
    d.text((170,224),"voice",font=F(POP,28),fill=(150,170,182),anchor="ma")
    d.polygon([(322,188),(364,210),(322,232)],fill=(90,104,120))
    d.rounded_rectangle([384,144,706,276],radius=26,fill=(20,28,46),outline=BLU,width=4)
    d.text((545,174),"Work agent",font=F(POPB,40),fill=BLU,anchor="ma")
    d.text((545,222),"runs in the background",font=F(POP,24),fill=(150,170,182),anchor="ma")
    d.polygon([(722,188),(764,210),(722,232)],fill=(90,104,120))
    outs=["document","slides","sheet","browser"]
    y=60
    for i,o in enumerate(outs):
        d.rounded_rectangle([790,y,W-40,y+68],radius=18,fill=(26,22,40),outline=VIO,width=3)
        d.text((905,y+18),o,font=F(POP,32),fill=(225,232,242),anchor="ma"); y+=84
    im.save(path,quality=95)

def tiers(path):
    W,H=1080,420
    im=base((W,H),(12,20,32),(6,9,15)); d=ImageDraw.Draw(im)
    rows=[("Free","limited",190,(110,125,145)),
          ("Go","3 hours, small model",330,BLU),
          ("Plus","3 hours, full model",500,MINT),
          ("Pro","15 hours or unlimited",670,AMB)]
    y=40
    for name,note,w,col in rows:
        d.rounded_rectangle([40,y,40+w,y+76],radius=18,fill=tuple(int(c*0.22) for c in col),outline=col,width=3)
        d.text((66,y+16),name,font=F(POPB,40),fill=col)
        d.text((40+w+24,y+24),note,font=F(POP,28),fill=(170,185,198))
        y+=94
    im.save(path,quality=95)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
cover("s1.png"); plugins("d1.png"); flow("d2.png"); tiers("d3.png")
print("art ok")
