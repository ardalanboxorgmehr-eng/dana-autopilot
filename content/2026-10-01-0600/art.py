import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import os as _os
_FD=_os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),"build","fonts")
POP=_os.path.join(_FD,"Poppins-Medium.ttf")
POPB=_os.path.join(_FD,"Poppins-Bold.ttf")
def F(p,s): return ImageFont.truetype(p,s)
TEAL=(72,214,196); AMB=(255,206,84); VIO=(150,130,255)

def glowlayer(size, fn, blur=18, mult=1.0):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))

def base(size, c1=(8,18,26), c2=(4,8,14)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=60)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,(18,60,72)),im,g)

# ---------- cover: double helix + repeat array ----------
def cover(path):
    from PIL import ImageChops
    W,H=1080,900
    im=base((W,H))
    cy=H*0.40; A=118; k=2*math.pi/320
    def helix(d, w=9, rung=True):
        for ph,col in ((0,TEAL),(math.pi,(120,170,255))):
            pts=[(x, cy+A*math.sin(k*x+ph)) for x in range(-20,W+20,5)]
            d.line(pts, fill=col, width=w, joint="curve")
        if rung:
            for x in range(18,W,30):
                y1=cy+A*math.sin(k*x); y2=cy+A*math.sin(k*x+math.pi)
                m=(y1+y2)/2; f=0.62
                d.line([(x,m+(y1-m)*f),(x,m+(y2-m)*f)], fill=(120,145,168), width=3)
    im=ImageChops.add(im, glowlayer((W,H),lambda d:helix(d,20,False),blur=30), scale=1.35)
    d=ImageDraw.Draw(im); helix(d)
    # repeat array strip
    y0=H*0.76; x=40
    def arr(d,w=0):
        x=40
        while x<W-40:
            d.rounded_rectangle([x,y0-32-w,x+70+w*2,y0+32+w],radius=12,fill=AMB)
            x+=70+34
            d.polygon([(x+6,y0),(x+18,y0-20),(x+30,y0),(x+18,y0+20)],fill=(110,120,140))
            x+=44
    im=ImageChops.add(im, glowlayer((W,H),lambda d:arr(d,8),blur=24), scale=1.6)
    d=ImageDraw.Draw(im); arr(d)
    d.text((44,H-58),"ART  ·  array-associated reverse transcriptases",font=F(POP,30),fill=(150,170,180))
    im.save(path,quality=95)

# ---------- d1: gene map of the 3-part system ----------
def genemap(path):
    W,H=1080,300
    im=base((W,H),(10,22,30),(6,10,16)); d=ImageDraw.Draw(im)
    y=80; h=104
    d.line([(30,y+h/2),(W-30,y+h/2)],fill=(70,80,95),width=6)
    def box(x,w,col,label,sub):
        d.rounded_rectangle([x,y,x+w,y+h],radius=20,fill=col)
        d.text((x+w/2,y+h/2),label,font=F(POPB,40),fill=(10,14,18),anchor="mm")
        d.text((x+w/2,y+h+26),sub,font=F(POP,30),fill=(180,195,205),anchor="ma")
    box(46,300,TEAL,"RT enzyme","reverse transcriptase")
    box(386,210,VIO,"partner","partner gene")
    # repeat array
    x=636; d.rounded_rectangle([x,y,W-46,y+h],radius=20,outline=AMB,width=5)
    xx=x+22
    while xx<W-96:
        d.rounded_rectangle([xx,y+22,xx+34,y+h-22],radius=8,fill=AMB); xx+=34
        d.polygon([(xx+4,y+h/2-14),(xx+18,y+h/2),(xx+4,y+h/2+14)],fill=(110,120,140)); xx+=26
    d.text(((x+W-46)/2,y+h+26),"repeat array",font=F(POP,30),fill=(180,195,205),anchor="ma")
    im.save(path,quality=95)

# ---------- d2: funnel ----------
def funnel(path):
    W,H=1080,700
    im=base((W,H),(10,20,30),(6,10,16)); d=ImageDraw.Draw(im)
    rows=[("200,000+","reverse transcriptases gathered",TEAL,980),
          ("3,500","new candidate systems",(120,170,255),820),
          ("20","studied in detail",VIO,660),
          ("1","new enzyme system",AMB,560)]
    y=70
    for i,(n,lab,col,w) in enumerate(rows):
        x=(W-w)//2
        d.rounded_rectangle([x,y,x+w,y+110],radius=22,fill=tuple(int(c*0.22) for c in col),outline=col,width=4)
        d.text((x+34,y+22),n,font=F(POPB,54),fill=col)
        d.text((x+w-34,y+44),lab,font=F(POP,30),fill=(195,208,218),anchor="ra")
        if i<3:
            d.polygon([(W/2-20,y+124),(W/2+20,y+124),(W/2,y+152)],fill=(90,104,120))
        y+=160
    im.save(path,quality=95)

# ---------- d3: CRISPR array vs ART array ----------
def compare(path):
    W,H=1080,540
    im=base((W,H),(10,20,30),(6,10,16)); d=ImageDraw.Draw(im)
    def row(y,col,title,note):
        d.text((46,y-58),title,font=F(POPB,40),fill=(235,245,250))
        x=46
        while x<W-90:
            d.rounded_rectangle([x,y,x+56,y+76],radius=12,fill=col); x+=56
            d.rounded_rectangle([x+10,y+24,x+58,y+52],radius=8,fill=(96,106,122)); x+=72
        d.text((46,y+100),note,font=F(POP,30),fill=(155,172,184))
    row(150,(120,170,255),"CRISPR array","evenly spaced repeats  ·  programmable tool")
    row(400,AMB,"ART array","the same layout, function still unknown")
    im.save(path,quality=95)

os.chdir(os.path.dirname(os.path.abspath(__file__)))
cover("s1.png"); genemap("d1.png"); funnel("d2.png"); compare("d3.png")
print("art ok")
