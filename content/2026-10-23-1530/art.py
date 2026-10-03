import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(30,120,140)
C1=(10,32,40); C2=(3,8,10)
TEAL=(70,210,200)
PAL=[(70,210,200),(255,206,84),(240,110,110),(120,160,255),(180,130,255),(110,220,130)]
def arrow(d,p0,p1,col,w=10,hl=34):
    (x0,y0),(x1,y1)=p0,p1; L=math.hypot(x1-x0,y1-y0); ux,uy=(x1-x0)/L,(y1-y0)/L
    bx,by=x1-ux*hl,y1-uy*hl
    d.line([(x0,y0),(bx,by)],fill=col,width=w)
    d.polygon([(x1,y1),(bx-uy*hl*0.6,by+ux*hl*0.6),(bx+uy*hl*0.6,by-ux*hl*0.6)],fill=col)
def folded(d,cx,cy,R,n=46,seed=4,r=17):
    rnd=random.Random(seed); pts=[]
    for i in range(n):
        t=i/n*math.pi*4.2
        rr=R*(0.35+0.6*abs(math.sin(i*0.37)))
        pts.append((cx+rr*math.cos(t)+rnd.uniform(-12,12),cy+rr*0.8*math.sin(t*1.1)+rnd.uniform(-12,12)))
    d.line(pts,fill=(200,210,220),width=5,joint="curve")
    for i,(x,y) in enumerate(pts):
        d.ellipse([x-r,y-r,x+r,y+r],fill=PAL[i%len(PAL)],outline=(10,20,24),width=2)
def chain(d,x0,y,n,step,r,amp=0,seed=1):
    pts=[(x0+i*step,y+amp*math.sin(i*0.9)) for i in range(n)]
    d.line(pts,fill=(200,210,220),width=5)
    for i,(x,yy) in enumerate(pts):
        d.ellipse([x-r,yy-r,x+r,yy+r],fill=PAL[(i*5)%len(PAL)],outline=(10,20,24),width=2)
def medal(d,cx,cy,s):
    d.polygon([(cx-s*0.55,cy-s*1.9),(cx-s*0.15,cy-s*1.9),(cx+s*0.2,cy-s*0.8),(cx-s*0.2,cy-s*0.8)],fill=(70,110,200))
    d.polygon([(cx+s*0.55,cy-s*1.9),(cx+s*0.15,cy-s*1.9),(cx-s*0.2,cy-s*0.8),(cx+s*0.2,cy-s*0.8)],fill=(90,140,230))
    d.ellipse([cx-s,cy-s,cx+s,cy+s],fill=(235,190,70),outline=(255,225,130),width=6)
    d.ellipse([cx-s*0.72,cy-s*0.72,cx+s*0.72,cy+s*0.72],outline=(190,145,40),width=4)
    d.text((cx,cy),"2024",font=F(POPB,int(s*0.45)),fill=(90,60,10),anchor="mm")
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:d.ellipse([520,120,1060,700],fill=(60,220,200)),130,0.5)
    d=ImageDraw.Draw(im)
    chain(d,70,420,9,46,19,amp=30)
    d.text((70,330),"sequence",font=F(POPB,34),fill=GREY)
    arrow(d,(470,420),(570,420),WHITE,10)
    folded(d,800,400,210)
    d.text((800,660),"3D structure",font=F(POPB,34),fill=GREY,anchor="mm")
    medal(d,180,640,70)
    im.save(path,quality=95)
def problem(path):
    W,H=1000,460; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[40,30,W-40,H-30],r=30,fill=(12,26,30),outline=(60,120,120))
    letters="MKTAYIAKQRQISFV"
    for i,ch in enumerate(letters):
        x=95+i*58; d.ellipse([x-24,90-24,x+24,90+24],fill=PAL[(i*5)%6])
        d.text((x,90),ch,font=F(POPB,26),fill=(10,20,24),anchor="mm")
    d.text((W/2,160),"20 kinds of amino acids, in a chain",font=F(POP,28),fill=GREY,anchor="mm")
    arrow(d,(W/2,195),(W/2,265),WHITE,8,26)
    d.text((W/2,330),"what shape does it fold into?",font=F(POPB,40),fill=WHITE,anchor="mm")
    d.text((W/2,390),"a 50-year-old problem",font=F(POPB,32),fill=AMB,anchor="mm")
    im.save(path,quality=95)
def scale(path):
    W,H=1000,480; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    rnd=random.Random(7)
    for i in range(14):
        for j in range(5):
            x=60+i*65; y=250+j*42
            d.ellipse([x,y,x+30,y+30],fill=PAL[(i+j)%6]); d.ellipse([x+16,y+8,x+44,y+36],fill=PAL[(i+j+2)%6])
    d.text((W/2,90),"200,000,000",font=F(POPB,96),fill=TEAL,anchor="mm")
    d.text((W/2,170),"protein structures predicted",font=F(POP,32),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def split(path):
    W,H=1000,480; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    cx,cy,R=250,240,190
    d.pieslice([cx-R,cy-R,cx+R,cy+R],90,270,fill=AMB)
    d.pieslice([cx-R,cy-R,cx+R,cy+R],270,360,fill=TEAL)
    d.pieslice([cx-R,cy-R,cx+R,cy+R],0,90,fill=(120,160,255))
    d.line([(cx,cy-R),(cx,cy+R)],fill=(10,20,24),width=8); d.line([(cx,cy),(cx+R,cy)],fill=(10,20,24),width=8)
    d.text((cx-95,cy),"1/2",font=F(POPB,54),fill=(40,30,10),anchor="mm")
    d.text((cx+90,cy-75),"1/4",font=F(POPB,40),fill=(10,30,30),anchor="mm")
    d.text((cx+90,cy+75),"1/4",font=F(POPB,40),fill=(10,20,50),anchor="mm")
    rows=[(AMB,"David Baker","protein design"),(TEAL,"Demis Hassabis","structure prediction"),((120,160,255),"John Jumper","structure prediction")]
    for i,(c,n,w) in enumerate(rows):
        y=90+i*120; d.rounded_rectangle([500,y,540,y+40],radius=10,fill=c)
        d.text((565,y-4),n,font=F(POPB,36),fill=WHITE); d.text((565,y+42),w,font=F(POP,26),fill=GREY)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); problem("d1.png"); scale("d2.png"); split("d3.png"); print("art ok")
