import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(30,100,170)
DOL=(120,160,200); SLEEP=(70,80,130); AWAKE=(255,206,84)
def brain(d,cx,cy,r,left_col,right_col):
    # top view: two hemispheres separated by a gap
    d.ellipse([cx-r,cy-r*0.8,cx-6,cy+r*0.8],fill=left_col)
    d.rectangle([cx-r*0.5,cy-r*0.8,cx-6,cy+r*0.8],fill=left_col)
    d.ellipse([cx+6,cy-r*0.8,cx+r,cy+r*0.8],fill=right_col)
    d.rectangle([cx+6,cy-r*0.8,cx+r*0.5,cy+r*0.8],fill=right_col)
    for side,col in ((-1,left_col),(1,right_col)):
        dark=tuple(max(0,c-40) for c in col)
        for k in range(3):
            y=cy-r*0.45+k*r*0.45
            x0=cx+side*r*0.2; x1=cx+side*r*0.75
            d.arc([min(x0,x1),y-r*0.12,max(x0,x1),y+r*0.12],0 if k%2 else 180,180 if k%2 else 360,fill=dark,width=5)
def zz(d,x,y,s,col):
    for i,(dx,dy,k) in enumerate(((0,0,1.0),(s*0.7,-s*0.8,0.75),(s*1.25,-s*1.45,0.55))):
        f=F(POPB,int(s*k)); d.text((x+dx,y+dy),"z",font=f,fill=col,anchor="mm")
def eye(d,x,y,s,open_):
    if open_:
        d.ellipse([x-s,y-s*0.6,x+s,y+s*0.6],fill=WHITE); d.ellipse([x-s*0.35,y-s*0.35,x+s*0.35,y+s*0.35],fill=(20,24,36))
    else:
        d.arc([x-s,y-s*0.6,x+s,y+s*0.6],10,170,fill=WHITE,width=6)
def dolphin(d,x,y,s,col):
    belly=(200,215,230)
    d.chord([x-s,y-s*0.34,x+s*0.9,y+s*0.34],0,180,fill=belly)
    d.chord([x-s,y-s*0.34,x+s*0.9,y+s*0.34],180,360,fill=col)
    d.rectangle([x-s*0.95,y-2,x+s*0.88,y+s*0.06],fill=col)
    d.ellipse([x+s*0.4,y-s*0.36,x+s*1.0,y+s*0.12],fill=col)  # melon (rounded forehead)
    d.rounded_rectangle([x+s*0.85,y-s*0.02,x+s*1.18,y+s*0.11],radius=int(s*0.06),fill=col)  # short beak
    d.arc([x+s*0.75,y-s*0.04,x+s*1.12,y+s*0.12],20,120,fill=(60,80,110),width=4)  # smile
    d.polygon([(x-s*0.05,y-s*0.3),(x-s*0.3,y-s*0.62),(x-s*0.38,y-s*0.6),(x-s*0.32,y-s*0.3)],fill=col)  # curved dorsal fin
    d.polygon([(x-s*0.9,y-s*0.05),(x-s*1.35,y-s*0.35),(x-s*1.2,y),(x-s*1.35,y+s*0.3),(x-s*0.9,y+s*0.08)],fill=col)  # tail flukes
    d.polygon([(x+s*0.15,y+s*0.18),(x-s*0.05,y+s*0.5),(x+s*0.32,y+s*0.24)],fill=col)  # flipper
def cover(path):
    W,H=1080,900; im=base((W,H),(10,24,44),(3,6,12),T)
    im=addglow(im,lambda d:(d.ellipse([560,0,1040,420],fill=(255,190,60)),d.ellipse([40,380,640,860],fill=(40,120,220))),120,0.45)
    d=ImageDraw.Draw(im)
    sea=Image.new("RGB",(W,H-380),(14,46,84)); m=Image.new("L",(W,H-380),150); im.paste(sea,(0,380),m); d=ImageDraw.Draw(im)
    for k in range(7): d.arc([k*170-60,355,k*170+110,405],180,360,fill=(90,150,210),width=5)
    dolphin(d,380,560,230,DOL)
    d.ellipse([548,500,572,524],fill=(20,30,50))
    brain(d,780,175,150,SLEEP,AWAKE)
    zz(d,590,70,60,(170,190,255))
    d.text((700,340),"asleep",font=F(POPB,32),fill=(170,190,255),anchor="ms")
    d.text((870,340),"awake",font=F(POPB,32),fill=AWAKE,anchor="ms")
    im.save(path,quality=95)
def halves(path):
    W,H=1000,460; im=base((W,H),(10,24,44),(3,6,12),T); d=ImageDraw.Draw(im)
    # each eye is wired to the opposite half of the brain
    def dashed(p0,p1,col):
        n=14
        for i in range(0,n,2):
            a=i/n; b=(i+1)/n
            d.line([(p0[0]+(p1[0]-p0[0])*a,p0[1]+(p1[1]-p0[1])*a),(p0[0]+(p1[0]-p0[0])*b,p0[1]+(p1[1]-p0[1])*b)],fill=col,width=5)
    dashed((600,330),(150,280),AWAKE); dashed((400,330),(850,280),(170,190,255))
    brain(d,500,200,190,SLEEP,AWAKE)
    eye(d,150,220,70,True); eye(d,850,220,70,False)
    d.text((150,350),"eye open",font=F(POPB,30),fill=AWAKE,anchor="ms")
    d.text((850,350),"eye closed",font=F(POPB,30),fill=GREY,anchor="ms")
    d.text((500,440),"each eye is wired to the opposite half",font=F(POP,26),fill=GREY,anchor="ms")
    im.save(path,quality=95)
def frigate(path):
    W,H=1000,500; im=base((W,H),(10,24,44),(3,6,12),T); d=ImageDraw.Draw(im)
    # bird silhouette
    d.polygon([(500,90),(380,40),(250,70),(380,60),(470,110),(500,125),(530,110),(620,60),(750,70),(620,40)],fill=(40,44,60),outline=(150,160,190))
    d.polygon([(490,120),(510,120),(500,170)],fill=(200,50,60))
    x0,w=60,W-120
    for i,(lab,v,col,vt) in enumerate((("روزی تو پرواز",42,AMB,"~42 min"),("روزی روی خشکی",720,(150,160,190),"12+ h"))):
        y=200+i*140
        fa(d,(x0+w,y),lab,F(VB,34),(225,228,236))
        by=y+52; d.rounded_rectangle([x0,by,x0+w,by+44],radius=22,fill=(38,42,54))
        bw=max(44,int(w*v/720)); d.rounded_rectangle([x0+w-bw,by,x0+w,by+44],radius=22,fill=col)
        if bw>200: d.text((x0+w-bw+20,by+22),vt,font=F(POPB,28),fill=(12,12,16),anchor="lm")
        else: d.text((x0+w-bw-16,by+22),vt,font=F(POPB,28),fill=col,anchor="rm")
    im.save(path,quality=95)
def firstnight(path):
    W,H=1000,480; im=base((W,H),(10,24,44),(3,6,12),T); d=ImageDraw.Draw(im)
    for x,lab,lc in ((740,"شب اول",AWAKE),(260,"شب دوم",SLEEP)):
        # brain viewed from above, front at top; left hemisphere drawn on the left
        brain(d,x,200,150,lc,SLEEP)
        fa(d,(x,400),lab,F(VB,44),WHITE,"ma")
    d.text((740,370),"left half on watch",font=F(POPB,26),fill=AWAKE,anchor="ms")
    zz(d,380,60,40,(170,190,255))
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); halves("d1.png"); frigate("d2.png"); firstnight("d3.png"); print("art ok")
