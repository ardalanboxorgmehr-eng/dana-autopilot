import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,120,120)
COLS=[(240,90,90),(255,170,70),(255,220,90),(90,210,140),(80,190,230),(110,130,250),(190,110,240),(240,110,190)]
def cover(path):
    W,H=1080,900; im=base((W,H),(10,30,32),(4,8,8),T)
    im=addglow(im,lambda d:(d.ellipse([40,100,560,760],fill=(120,200,255)),d.ellipse([620,240,1040,700],fill=(80,220,170))),120,0.45)
    d=ImageDraw.Draw(im)
    # left: many colored dots (web), funnel, right: narrow single colour stream
    import random; r=random.Random(7)
    for i in range(70):
        x=r.randint(70,400); y=r.randint(160,720); s=r.randint(14,30)
        d.ellipse([x-s,y-s,x+s,y+s],fill=COLS[i%8])
    d.text((235,100),"Web",font=F(POPB,40),fill=WHITE,anchor="mm")
    # funnel
    d.polygon([(450,140),(640,360),(640,480),(450,700)],fill=(40,60,70),outline=(120,140,150))
    d.text((545,420),"AI",font=F(POPB,48),fill=WHITE,anchor="mm")
    # arrow left to right
    d.polygon([(660,400),(720,400),(720,370),(770,420),(720,470),(720,440),(660,440)],fill=WHITE)
    for i in range(6):
        y=300+i*48; d.ellipse([820,y,860,y+40],fill=COLS[4]); d.ellipse([890,y,930,y+40],fill=COLS[4] if i%3 else COLS[5])
    d.text((875,250),"Answer",font=F(POPB,40),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def stats(path):
    W,H=1000,440; im=base((W,H),(10,30,32),(4,8,8),T); d=ImageDraw.Draw(im)
    items=[("27","models"),("155","topics"),("12","countries"),("~70M","claims")]
    for i,(n,t) in enumerate(items):
        x=40+i*235
        panel(d,[x,60,x+215,380],r=26,fill=(16,26,28),outline=COLS[(i*2+3)%8],w=4)
        d.text((x+107,190),n,font=fiten(d,n,POPB,190,70),fill=WHITE,anchor="mm")
        d.text((x+107,290),t,font=F(POPB,30),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def compare(path):
    W,H=1000,420; im=base((W,H),(10,30,32),(4,8,8),T); d=ImageDraw.Draw(im)
    fa(d,(W-60,40),"تنوع اطلاعات",F(VB,38),(225,228,236))
    d.text((60,140),"Google Search",font=F(POPB,32),fill=WHITE)
    d.rounded_rectangle([60,190,940,240],radius=25,fill=BLUE)
    d.text((60,280),"GPT-5 (most diverse AI)",font=F(POPB,32),fill=WHITE)
    w=int(880*0.813)
    d.rounded_rectangle([60,330,940,380],radius=25,fill=(38,42,54))
    d.rounded_rectangle([60,330,60+w,380],radius=25,fill=AMB)
    d.text((940,300),"at least -18.7%",font=F(POPB,30),fill=RED,anchor="rm")
    im.save(path,quality=95)
def collapse(path):
    W,H=1000,400; im=base((W,H),(10,30,32),(4,8,8),T); d=ImageDraw.Draw(im)
    widths=[240,160,90]
    for i,wd in enumerate(widths):
        cx=180+i*320; cy=175
        n=8 if i==0 else (5 if i==1 else 2)
        d.rounded_rectangle([cx-wd/2,cy-wd/2,cx+wd/2,cy+wd/2],radius=30,fill=(16,26,28),outline=(90,120,120),width=3)
        for k in range(n):
            ang=k/n*6.283; import math
            rr=wd*0.28 if n>1 else 0
            x=cx+rr*math.cos(ang); y=cy+rr*math.sin(ang); s=max(12,wd*0.09)
            d.ellipse([x-s,y-s,x+s,y+s],fill=COLS[k])
        d.text((cx,355),f"Gen {i+1}",font=F(POPB,30),fill=GREY,anchor="mm")
        if i<2:
            nl=180+(i+1)*320-widths[i+1]/2
            a0=cx+wd/2+12; a1=nl-12; m=a1-22
            d.polygon([(a0,cy-9),(m,cy-9),(m,cy-24),(a1,cy),(m,cy+24),(m,cy+9),(a0,cy+9)],fill=WHITE)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); stats("d1.png"); compare("d2.png"); collapse("d3.png"); print("art ok")
