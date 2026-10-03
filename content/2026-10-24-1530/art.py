import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(200,100,30)
GOLD=(255,140,40); GOLD2=(255,180,80)
def fish(d,x,y,s,col=GOLD,face=1):
    # face=1 -> head on the right
    f=face
    d.polygon([(x-f*s*0.75,y),(x-f*s*1.35,y-s*0.55),(x-f*s*1.15,y),(x-f*s*1.35,y+s*0.55)],fill=GOLD2)
    d.ellipse([x-s,y-s*0.6,x+s,y+s*0.6],fill=col)
    d.polygon([(x-f*s*0.1,y-s*0.55),(x-f*s*0.5,y-s*0.95),(x-f*s*0.55,y-s*0.5)],fill=GOLD2)
    d.ellipse([x+f*s*0.5-s*0.13,y-s*0.25,x+f*s*0.5+s*0.13,y+s*0.01],fill=WHITE)
    d.ellipse([x+f*s*0.53-s*0.06,y-s*0.18,x+f*s*0.53+s*0.06,y-s*0.06],fill=(20,20,30))
def cover(path):
    W,H=1080,900; im=base((W,H),(44,24,8),(8,5,3),T)
    im=addglow(im,lambda d:d.ellipse([200,80,880,700],fill=(255,150,40)),120,0.5)
    d=ImageDraw.Draw(im)
    # bowl
    d.ellipse([260,120,820,660],fill=(30,60,90),outline=(160,200,230),width=8)
    d.chord([260,120,820,660],25,155,fill=(120,96,60))
    d.line([(330,215),(750,215)],fill=(160,200,230),width=6)
    fish(d,540,430,120)
    for bx,by,r in ((690,330,14),(720,280,10),(705,240,7)): d.ellipse([bx-r,by-r,bx+r,by+r],outline=(180,220,255),width=3)
    # crossed-out 3 sec tag
    d.rounded_rectangle([40,120,250,220],radius=24,fill=(60,24,24))
    d.text((145,170),"3 sec",font=F(POPB,54),fill=(240,120,120),anchor="mm")
    d.line([(50,215),(240,125)],fill=RED,width=10)
    d.rounded_rectangle([800,560,1050,670],radius=24,fill=(24,60,40))
    d.text((925,615),"3+ months",font=F(POPB,44),fill=GR,anchor="mm")
    im.save(path,quality=95)
def lever(path):
    W,H=1000,500; im=base((W,H),(44,24,8),(8,5,3),T); d=ImageDraw.Draw(im)
    # clock with 1-hour window highlighted (24h dial)
    cx,cy,r=760,240,180
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=(30,32,44),outline=(150,156,170),width=6)
    d.pieslice([cx-r+8,cy-r+8,cx+r-8,cy+r-8],-90+15*9,-90+15*10,fill=GR)
    for k in range(24):
        a=math.radians(-90+k*15); L=20 if k%6==0 else 10
        d.line([(cx+math.cos(a)*(r-8),cy+math.sin(a)*(r-8)),(cx+math.cos(a)*(r-8-L),cy+math.sin(a)*(r-8-L))],fill=GREY,width=4)
    d.text((cx,cy-60),"1 h / 24 h",font=F(POPB,34),fill=WHITE,anchor="mm")
    # tank + lever
    panel(d,[60,90,470,400],r=24,fill=(20,44,70),outline=(120,170,210),w=4)
    fish(d,190,260,70)
    d.line([(400,380),(330,190)],fill=(200,200,210),width=12); d.ellipse([310,165,350,205],fill=RED)
    d.rectangle([370,370,450,400],fill=(120,126,140))
    d.text((265,460),"press = food",font=F(POPB,30),fill=AMB,anchor="ms")
    im.save(path,quality=95)
def months(path):
    W,H=1000,420; im=base((W,H),(44,24,8),(8,5,3),T); d=ImageDraw.Draw(im)
    for i in range(3):
        x=90+i*290
        panel(d,[x,60,x+240,320],r=24,fill=(30,32,44),outline=GR,w=4)
        d.rectangle([x+3,63,x+237,120],fill=(40,110,80))
        for k in range(15):
            gx=x+30+(k%5)*40; gy=150+(k//5)*50
            d.rounded_rectangle([gx,gy,gx+26,gy+26],radius=6,fill=GR if (k+i)%3 else (60,66,84))
    d.text((500,385),"memory: at least 3 months",font=F(POPB,36),fill=WHITE,anchor="ms")
    im.save(path,quality=95)
def cones(path):
    W,H=1000,460; im=base((W,H),(44,24,8),(8,5,3),T); d=ImageDraw.Draw(im)
    rows=[("ماهی قرمز",[(230,60,60),(60,190,90),(70,120,240),(170,90,255)],["R","G","B","UV"]),("آدم",[(230,60,60),(60,190,90),(70,120,240)],["R","G","B"])]
    for i,(lab,cols,ls) in enumerate(rows):
        y=60+i*200
        fa(d,(940,y+40),lab,F(VB,44),WHITE)
        for k,(c,l) in enumerate(zip(cols,ls)):
            x=80+k*150
            d.ellipse([x,y,x+110,y+110],fill=c)
            d.text((x+55,y+55),l,font=F(POPB,36),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); lever("d1.png"); months("d2.png"); cones("d3.png"); print("art ok")
