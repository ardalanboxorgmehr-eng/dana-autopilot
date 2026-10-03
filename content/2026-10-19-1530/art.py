import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(60,110,170)
BONE=(236,230,214); CART=(120,190,230)
def bone(d,x0,y0,x1,y1,w,col=BONE):
    a=math.atan2(y1-y0,x1-x0); nx,ny=-math.sin(a),math.cos(a)
    d.line([(x0,y0),(x1,y1)],fill=col,width=int(w))
    r=w*0.62
    for (x,y) in ((x0,y0),(x1,y1)):
        for sgn in (-1,1):
            cx,cy=x+nx*sgn*w*0.45,y+ny*sgn*w*0.45
            d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
def arrow_r(d,x0,x1,y,col=WHITE,h=40):
    d.rectangle([x0,y-h*0.25,x1-h,y+h*0.25],fill=col); d.polygon([(x1-h,y-h*0.7),(x1,y),(x1-h,y+h*0.7)],fill=col)
def cover(path):
    W,H=1080,900; im=base((W,H),(14,26,44),(4,6,10),T)
    im=addglow(im,lambda d:(d.ellipse([60,140,480,620],fill=(80,160,255)),d.ellipse([600,140,1020,620],fill=(240,220,180))),120,0.45)
    d=ImageDraw.Draw(im)
    import random; r=random.Random(4)
    # many small pieces on the left (baby)
    for i in range(34):
        x=110+(i%6)*55+r.randint(-8,8); y=200+(i//6)*58+r.randint(-8,8)
        ang=r.random()*math.pi; L=24+r.randint(0,10)
        bone(d,x-math.cos(ang)*L/2,y-math.sin(ang)*L/2,x+math.cos(ang)*L/2,y+math.sin(ang)*L/2,9,BONE if i%4 else CART)
    d.text((260,620),"~270-300",font=F(POPB,64),fill=CART,anchor="ms")
    d.text((260,670),"at birth",font=F(POP,34),fill=GREY,anchor="ms")
    arrow_r(d,480,600,400)
    # few big bones on the right (adult)
    bone(d,700,230,940,230,30); bone(d,700,330,940,330,30); bone(d,700,430,940,430,30); bone(d,700,530,940,530,30)
    d.text((820,620),"206",font=F(POPB,72),fill=AMB,anchor="ms")
    d.text((820,670),"adult",font=F(POP,34),fill=GREY,anchor="ms")
    im.save(path,quality=95)
def counts(path):
    W,H=1000,400; im=base((W,H),(14,26,44),(4,6,10),T); d=ImageDraw.Draw(im)
    bars(d,60,40,W-120,[("نوزاد",300,CART,"~270-300"),("بزرگسال",206,AMB,"206")],rowh=150,maxv=300)
    im.save(path,quality=95)
def sacrum(path):
    W,H=1000,480; im=base((W,H),(14,26,44),(4,6,10),T); d=ImageDraw.Draw(im)
    # five separate vertebrae (left, child) -> one fused bone (right, adult)
    for i in range(5):
        y=50+i*66; w=170-i*22
        d.rounded_rectangle([250-w/2,y,250+w/2,y+52],radius=16,fill=CART if i%2 else BONE)
    d.text((250,440),"5 vertebrae",font=F(POPB,32),fill=WHITE,anchor="ms")
    arrow_r(d,410,560,215)
    d.polygon([(640,50),(860,50),(810,250),(750,370),(690,250)],fill=BONE)
    for i in range(1,5):
        y=50+i*62; d.line([(650+i*14,y),(850-i*14,y)],fill=(190,182,165),width=4)
    d.text((750,440),"1 sacrum",font=F(POPB,32),fill=AMB,anchor="ms")
    im.save(path,quality=95)
def skull(path):
    W,H=1000,520; im=base((W,H),(14,26,44),(4,6,10),T); d=ImageDraw.Draw(im)
    cx,cy=330,260
    d.ellipse([cx-170,cy-230,cx+170,cy+230],fill=BONE)
    d.line([(cx,cy-230),(cx,cy+230)],fill=(170,160,140),width=5)
    d.line([(cx-160,cy-60),(cx+160,cy-60)],fill=(170,160,140),width=5)
    d.line([(cx-150,cy+120),(cx+150,cy+120)],fill=(170,160,140),width=5)
    d.polygon([(cx,cy-130),(cx+60,cy-60),(cx,cy+10),(cx-60,cy-60)],fill=CART)
    d.polygon([(cx,cy+90),(cx+30,cy+120),(cx,cy+150),(cx-30,cy+120)],fill=CART)
    fa(d,(950,120),"ملاج جلو",F(VB,42),AMB); fa(d,(950,175),"۱۲ تا ۱۸ ماهگی",F(VS,36),WHITE)
    fa(d,(950,330),"ملاج پشت",F(VB,42),CART); fa(d,(950,385),"۲ تا ۳ ماهگی",F(VS,36),WHITE)
    d.line([(cx+70,cy-60),(560,145)],fill=AMB,width=3); d.line([(cx+40,cy+120),(560,355)],fill=CART,width=3)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); counts("d1.png"); sacrum("d2.png"); skull("d3.png"); print("art ok")
