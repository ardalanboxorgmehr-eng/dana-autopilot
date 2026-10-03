import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(90,70,200)
BOLT=(255,236,140); BLD=(36,40,60)
def bolt(d,x,y,s,col=BOLT):
    # top at (x,y), points downward
    d.polygon([(x,y),(x+s*0.35,y),(x+s*0.15,y+s*0.45),(x+s*0.42,y+s*0.45),(x-s*0.1,y+s*1.1),(x+s*0.05,y+s*0.6),(x-s*0.2,y+s*0.6)],fill=col)
def cloud(d,x,y,s,col=(70,74,96)):
    for dx,dy,r in ((0,0,0.5),(0.45,-0.2,0.6),(0.95,0,0.5),(0.45,0.15,0.55)):
        d.ellipse([x+dx*s-r*s,y+dy*s-r*s,x+dx*s+r*s,y+dy*s+r*s],fill=col)
def tower(d,cx,base,h,col=BLD):
    w=150
    d.rectangle([cx-w,base-h*0.45,cx+w,base],fill=col)
    d.rectangle([cx-w*0.75,base-h*0.7,cx+w*0.75,base-h*0.45],fill=col)
    d.rectangle([cx-w*0.5,base-h*0.85,cx+w*0.5,base-h*0.7],fill=col)
    d.rectangle([cx-w*0.25,base-h*0.93,cx+w*0.25,base-h*0.85],fill=col)
    d.rectangle([cx-8,base-h,cx+8,base-h*0.93],fill=col)
    for r in range(12):
        for c in range(6):
            yy=base-h*0.43+r*h*0.035; xx=cx-w+20+c*48
            d.rectangle([xx,yy,xx+22,yy+10],fill=(230,200,110) if (r*7+c)%5==0 else (60,66,90))
def cover(path):
    W,H=1080,900; im=base((W,H),(20,18,44),(4,4,10),T)
    im=addglow(im,lambda d:d.ellipse([300,0,800,520],fill=(200,190,255)),110,0.5)
    d=ImageDraw.Draw(im)
    cloud(d,330,90,200,(60,62,86)); cloud(d,620,70,170,(54,56,80))
    tower(d,540,690,420)
    bolt(d,553,128,138)
    d.ellipse([520,262,560,302],fill=(255,250,210))
    d.text((860,330),"~23",font=F(POPB,96),fill=AMB,anchor="mm")
    d.text((860,400),"strikes / year",font=F(POPB,34),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def count(path):
    W,H=1000,450; im=base((W,H),(20,18,44),(4,4,10),T); d=ImageDraw.Draw(im)
    for i in range(23):
        x=90+(i%8)*110; y=30+(i//8)*115
        bolt(d,x,y,95,AMB if i<23 else GREY)
    d.text((W/2,430),"average per year: 23",font=F(POPB,32),fill=WHITE,anchor="ms")
    im.save(path,quality=95)
def distance(path):
    W,H=1000,460; im=base((W,H),(20,18,44),(4,4,10),T); d=ImageDraw.Draw(im)
    cloud(d,130,110,110,(70,74,96))
    for k in range(7): d.line([(90+k*28,180),(75+k*28,240)],fill=(110,150,220),width=4)
    # clear sky on the right, bolt strikes far away
    bolt(d,800,60,190)
    d.line([(60,330),(940,330)],fill=(80,86,110),width=4)
    # double-headed distance arrow
    y=390; d.line([(150,y),(850,y)],fill=WHITE,width=6)
    d.polygon([(130,y),(165,y-18),(165,y+18)],fill=WHITE); d.polygon([(870,y),(835,y-18),(835,y+18)],fill=WHITE)
    d.rounded_rectangle([330,y-34,670,y+34],radius=30,fill=(30,30,56))
    d.text((500,y),"10-15 mi · 16-24 km",font=F(POPB,32),fill=AMB,anchor="mm")
    d.text((180,300),"storm",font=F(POPB,30),fill=GREY,anchor="ms")
    d.text((820,300),"clear sky",font=F(POPB,30),fill=GREY,anchor="ms")
    im.save(path,quality=95)
def temp(path):
    W,H=1000,400; im=base((W,H),(40,20,30),(6,4,6),(170,60,90)); d=ImageDraw.Draw(im)
    rows=[("Lightning",50000,BOLT,"~50,000°F"),("Sun's surface",10000,(255,170,60),"~10,000°F")]
    for i,(lab,v,col,vt) in enumerate(rows):
        y=50+i*160
        d.text((60,y),lab,font=F(POPB,34),fill=WHITE)
        by=y+55; d.rounded_rectangle([60,by,940,by+50],radius=25,fill=(38,42,54))
        bw=int(880*v/50000); d.rounded_rectangle([60,by,60+bw,by+50],radius=25,fill=col)
        if bw>300: d.text((80,by+25),vt,font=F(POPB,28),fill=(20,16,10),anchor="lm")
        else: d.text((60+bw+16,by+25),vt,font=F(POPB,28),fill=col,anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); count("d1.png"); distance("d2.png"); temp("d3.png"); print("art ok")
