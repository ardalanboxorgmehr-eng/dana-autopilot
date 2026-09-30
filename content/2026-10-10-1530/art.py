import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,80,170)
def camera(d,x,y,s):
    d.rounded_rectangle([x,y,x+s*1.6,y+s*0.8],radius=int(s*0.15),fill=(220,224,232))
    d.ellipse([x+s*1.05,y+s*0.12,x+s*1.5,y+s*0.68],fill=(30,34,44)); d.ellipse([x+s*1.18,y+s*0.25,x+s*1.37,y+s*0.55],fill=(80,140,255))
    d.rectangle([x+s*0.3,y-s*0.5,x+s*0.45,y],fill=(160,166,180))
    d.ellipse([x+s*0.18,y+s*0.18,x+s*0.3,y+s*0.3],fill=RED)
def crowd(d,y,n,seed,box=True):
    r=random.Random(seed)
    for i in range(n):
        cx=60+i*(960/(n-1)); s=r.randint(70,95); cy=y+r.randint(-20,20)
        col=r.choice([(70,78,96),(84,90,110),(60,66,84)])
        person(d,cx,cy,s,col,(120,126,146))
        if box:
            c=GR
            d.rectangle([cx-s*0.42,cy-s*0.98,cx+s*0.42,cy-s*0.18],outline=c,width=3)
def cover(path):
    W,H=1080,900; im=base((W,H),(12,20,40),(4,5,10),T)
    im=addglow(im,lambda d:d.polygon([(760,140),(40,760),(1040,760)],fill=(60,120,255)),100,0.45)
    d=ImageDraw.Draw(im)
    d.rectangle([0,90,W,110],fill=(40,44,56))
    camera(d,700,150,130)
    crowd(d,640,9,4)
    d.rounded_rectangle([60,150,520,350],radius=30,fill=(18,22,34),outline=(90,110,160),width=3)
    d.text((290,215),"500,000+",font=F(POPB,72),fill=WHITE,anchor="mm")
    d.text((290,295),"faces scanned · 0 arrests",font=F(POPB,30),fill=AMB,anchor="mm")
    im.save(path,quality=95)
def match(path):
    W,H=1000,480; im=base((W,H),(12,20,40),(4,5,10),T); d=ImageDraw.Draw(im)
    panel(d,[40,60,420,420],r=26,fill=(18,22,34),outline=(90,110,160))
    person(d,230,300,150,(84,90,110),(130,136,156)); d.rectangle([230-65,300-150,230+65,300-35],outline=GR,width=4)
    d.text((230,400),"LIVE CAMERA",font=F(POPB,26),fill=GREY,anchor="ms")
    d.line([(440,240),(560,240)],fill=WHITE,width=5); d.polygon([(580,240),(555,225),(555,255)],fill=WHITE)
    panel(d,[600,60,960,420],r=26,fill=(18,22,34),outline=(160,90,90))
    d.text((780,105),"WATCHLIST",font=F(POPB,28),fill=RED,anchor="mm")
    for i in range(2):
        for j in range(2):
            x=640+j*160; y=150+i*125
            d.rounded_rectangle([x,y,x+120,y+105],radius=14,fill=(34,38,50)); person(d,x+60,y+80,48,(70,76,96),(110,116,136))
    im.save(path,quality=95)
def stats(path):
    W,H=1000,520; im=base((W,H),(12,20,40),(4,5,10),T); d=ImageDraw.Draw(im)
    tiles=[("500,000+","صورت اسکن‌شده",WHITE),("£320k","هزینه",AMB),("~100 h","وقت پلیس",BLUE),("1","هشدار، اونم اشتباه",RED)]
    for k,(v,l,c) in enumerate(tiles):
        x=60+(k%2)*450; y=40+(k//2)*235
        panel(d,[x,y,x+430,y+210],r=26,fill=(18,22,34),outline=(70,80,110))
        d.text((x+215,y+85),v,font=F(POPB,64),fill=c,anchor="mm")
        fa(d,(x+215,y+170),l,F(VB,34),GREY,"ms")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); match("d1.png"); stats("d2.png"); print("art ok")
