import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
_FD=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),"build","fonts")
POP=os.path.join(_FD,"Poppins-Medium.ttf"); POPB=os.path.join(_FD,"Poppins-Bold.ttf")
VB=os.path.join(_FD,"Vazirmatn-Bold.ttf"); VS=os.path.join(_FD,"Vazirmatn-SemiBold.ttf")
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
GRN=(88,214,124); RED=(255,110,110); AMB=(255,206,84); TEAL=(96,200,255)

def glowlayer(size, fn, blur=18):
    l=Image.new("RGB",size,(0,0,0)); d=ImageDraw.Draw(l); fn(d)
    return l.filter(ImageFilter.GaussianBlur(blur))

def base(size, c1=(12,20,34), c2=(5,7,12), tint=(26,56,92)):
    W,H=size; im=Image.new("RGB",size,c2); d=ImageDraw.Draw(im)
    for y in range(H):
        t=y/H
        d.line([(0,y),(W,y)],fill=tuple(int(c1[i]*(1-t)+c2[i]*t) for i in range(3)))
    g=Image.new("L",size,0); ImageDraw.Draw(g).ellipse([-W*0.3,-H*0.6,W*1.3,H*0.75],fill=62)
    g=g.filter(ImageFilter.GaussianBlur(160))
    return Image.composite(Image.new("RGB",size,tint),im,g)

def tick(d,cx,cy,r,col,w):
    d.line([(cx-r,cy+r*0.1),(cx-r*0.2,cy+r*0.8)],fill=col,width=w)
    d.line([(cx-r*0.2,cy+r*0.8),(cx+r,cy-r*0.8)],fill=col,width=w)

def cross(d,cx,cy,r,col,w):
    d.line([(cx-r,cy-r),(cx+r,cy+r)],fill=col,width=w)
    d.line([(cx-r,cy+r),(cx+r,cy-r)],fill=col,width=w)

def arrow(d,x1,y1,x2,y2,col,w,head=20):
    d.line([(x1,y1),(x2,y2)],fill=col,width=w)
    a=math.atan2(y2-y1,x2-x1)
    for s in (0.6,-0.6):
        d.line([(x2,y2),(x2-head*math.cos(a-s),y2-head*math.sin(a-s))],fill=col,width=w)

def cardface(d,x,y,w,h,fill,accent=None,radius=34):
    d.rounded_rectangle([x,y,x+w,y+h],radius=radius,fill=fill)
    if accent:
        d.rounded_rectangle([x+w*0.30,y+h-26,x+w*0.70,y+h-14],radius=6,fill=accent)

# ---------- cover: a card caught mid flip ----------
def cover(path):
    W,H=1080,900
    im=base((W,H))
    cw,ch=560,360
    cx,cy=W/2,H*0.48
    def glowbits(d):
        d.rounded_rectangle([cx-cw/2-14,cy-ch/2-14,cx+cw/2+14,cy+ch/2+14],radius=44,fill=(60,120,190))
        d.arc([cx-cw*0.78,cy-ch*0.95,cx+cw*0.78,cy+ch*1.05],200,340,fill=AMB,width=22)
    im=ImageChops.add(im, glowlayer((W,H),glowbits,blur=34), scale=1.35)
    d=ImageDraw.Draw(im)
    # two cards behind, fanned
    cardface(d,cx-cw/2-64,cy-ch/2-70,cw,ch,(44,52,70))
    cardface(d,cx-cw/2-32,cy-ch/2-35,cw,ch,(74,86,112))
    # the front card
    cardface(d,cx-cw/2,cy-ch/2,cw,ch,(240,243,250),accent=(198,206,222))
    d.text((cx,cy-70),"اهرام جیزه کِی ساخته شد؟",font=F(VB,46),fill=(22,26,34),anchor="ma",**FA)
    d.line([(cx-190,cy+6),(cx+190,cy+6)],fill=(210,216,228),width=3)
    d.text((cx,cy+34),"برای دیدن جواب، ضربه بزن",font=F(VS,34),fill=(120,128,146),anchor="ma",**FA)
    # flip arc over the top
    d.arc([cx-cw*0.78,cy-ch*0.95,cx+cw*0.78,cy+ch*1.05],200,340,fill=AMB,width=11)
    arrow(d,cx+cw*0.70,cy-ch*0.30,cx+cw*0.74,cy-ch*0.06,AMB,11,22)
    im.save(path,quality=95)

# ---------- d1: two ways in ----------
def twoways(path):
    W,H=1080,380
    im=base((W,H),(12,20,34),(5,7,12),(26,56,92)); d=ImageDraw.Draw(im)
    # target card on the LEFT, sources on the RIGHT (reads right to left)
    cardface(d,70,96,250,188,(240,243,250),accent=(198,206,222),radius=26)
    d.text((195,150),"فلش‌کارت",font=F(VB,40),fill=(22,26,34),anchor="ma",**FA)
    d.text((195,206),"آماده",font=F(VS,32),fill=(120,128,146),anchor="ma",**FA)
    def src(y,label,col):
        d.rounded_rectangle([W-470,y,W-70,y+110],radius=24,fill=(26,32,46),outline=col,width=3)
        d.text((W-100,y+30),label,font=F(VS,34),fill=(226,230,240),anchor="ra",**FA)
        arrow(d,W-490,y+55,350,y+55,col,7,18)
    src(52,"اسم یه موضوع رو بگو",TEAL)
    src(214,"یا جزوه‌ات رو آپلود کن",AMB)
    im.save(path,quality=95)

# ---------- d2: how the review works ----------
def review(path):
    W,H=1080,400
    im=base((W,H),(12,20,34),(5,7,12),(26,56,92)); d=ImageDraw.Draw(im)
    cw,ch=360,230
    cx=W*0.30
    cardface(d,cx-cw/2,60,cw,ch,(240,243,250),accent=(198,206,222),radius=28)
    d.text((cx,150),"جواب",font=F(VB,52),fill=(22,26,34),anchor="ma",**FA)
    d.text((cx,H-58),"ضربه بزن تا برگرده",font=F(VS,30),fill=(150,158,176),anchor="ma",**FA)
    def btn(x,y,col,mark,label):
        d.ellipse([x-52,y-52,x+52,y+52],fill=(24,30,44),outline=col,width=4)
        if mark=="tick": tick(d,x,y,22,col,10)
        else: cross(d,x,y,20,col,10)
        d.text((x,y+92),label,font=F(VS,30),fill=(206,212,226),anchor="ma",**FA)
    btn(W*0.62,140,GRN,"tick","بلدم")
    btn(W*0.84,140,RED,"cross","بازم تمرین")
    d.rounded_rectangle([W*0.56,286,W*0.92,362],radius=26,fill=(24,30,44),outline=AMB,width=3)
    d.text((W*0.74,302),"ترتیبشون رو به هم بزن",font=F(VS,32),fill=AMB,anchor="ma",**FA)
    im.save(path,quality=95)

if __name__=="__main__":
    cover("s1.png"); twoways("d1.png"); review("d2.png")
    print("art ok")
