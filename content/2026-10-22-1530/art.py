import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(30,90,150)
C1=(14,26,44); C2=(4,6,12)
def arrow(d,p0,p1,col,w=10,hl=34):
    (x0,y0),(x1,y1)=p0,p1; L=math.hypot(x1-x0,y1-y0); ux,uy=(x1-x0)/L,(y1-y0)/L
    bx,by=x1-ux*hl,y1-uy*hl
    d.line([(x0,y0),(bx,by)],fill=col,width=w)
    d.polygon([(x1,y1),(bx-uy*hl*0.6,by+ux*hl*0.6),(bx+uy*hl*0.6,by-ux*hl*0.6)],fill=col)
def bolt(d,cx,cy,s,col):
    pts=[(0.15,-1),(-0.55,0.1),(-0.05,0.1),(-0.2,1),(0.55,-0.15),(0.05,-0.15),(0.25,-1)]
    d.polygon([(cx+x*s,cy+y*s) for x,y in pts],fill=col)
def drop(d,cx,cy,s,col):
    d.ellipse([cx-s,cy-s*0.2,cx+s,cy+s*1.8],fill=col)
    d.polygon([(cx,cy-s*1.5),(cx-s*0.93,cy+0.45*s),(cx+s*0.93,cy+0.45*s)],fill=col)
    d.ellipse([cx-s*0.55,cy+s*0.5,cx-s*0.2,cy+s*1.0],fill=(200,235,255))
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:(d.ellipse([560,120,1040,460],fill=(255,200,60)),d.ellipse([560,450,1040,800],fill=(60,160,255))),120,0.5)
    d=ImageDraw.Draw(im)
    # prompt bubble (left)
    panel(d,[60,250,440,560],r=40,fill=(24,34,56),outline=(110,130,170),w=4)
    d.polygon([(120,555),(170,555),(110,620)],fill=(24,34,56))
    d.text((100,290),"1 prompt",font=F(POPB,48),fill=WHITE)
    for i,wd in enumerate([300,250,280,180]):
        d.rounded_rectangle([100,370+i*42,100+wd,392+i*42],radius=10,fill=(70,86,120))
    arrow(d,(470,405),(590,260),WHITE,10)
    arrow(d,(470,405),(590,600),WHITE,10)
    # energy card
    panel(d,[610,140,1030,380],r=34,fill=(30,30,20),outline=AMB,w=4)
    bolt(d,700,260,80,AMB)
    d.text((790,215),"0.24",font=F(POPB,84),fill=AMB)
    d.text((795,320),"watt-hours",font=F(POP,30),fill=GREY)
    # water card
    panel(d,[610,470,1030,710],r=34,fill=(16,30,46),outline=BLUE,w=4)
    drop(d,700,570,48,BLUE)
    d.text((790,545),"0.26",font=F(POPB,84),fill=BLUE)
    d.text((795,650),"millilitres",font=F(POP,30),fill=GREY)
    im.save(path,quality=95)
def drops(path):
    W,H=1000,440; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[50,40,W-50,H-40],r=30,fill=(14,22,36),outline=(70,100,150))
    for i in range(5):
        drop(d,170+i*80,170,32,BLUE)
    d.text((560,120),"0.26 ml",font=F(POPB,64),fill=BLUE)
    d.text((562,205),"about 5 drops",font=F(POP,32),fill=GREY)
    d.line([(100,275),(W-100,275)],fill=(60,70,90),width=3)
    bolt(d,160,340,46,AMB)
    d.text((230,300),"0.24 Wh",font=F(POPB,54),fill=AMB)
    d.text((560,315),"one median text prompt",font=F(POP,30),fill=GREY)
    im.save(path,quality=95)
def compare(path):
    W,H=1000,440; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    # TV
    panel(d,[50,40,480,H-40],r=30,fill=(14,22,36),outline=(70,100,150))
    d.rounded_rectangle([120,90,410,260],radius=16,fill=(30,40,60),outline=(170,180,200),width=6)
    d.rounded_rectangle([140,110,390,240],radius=8,fill=(50,90,150))
    d.polygon([(230,260),(300,260),(320,290),(210,290)],fill=(170,180,200))
    d.text((265,345),"under 9 s",font=F(POPB,50),fill=WHITE,anchor="ms")
    d.text((265,385),"of TV",font=F(POP,28),fill=GREY,anchor="ms")
    # microwave
    panel(d,[520,40,950,H-40],r=30,fill=(14,22,36),outline=(70,100,150))
    d.rounded_rectangle([580,100,890,270],radius=16,fill=(60,64,76),outline=(170,180,200),width=5)
    d.rounded_rectangle([600,120,790,250],radius=10,fill=(255,190,80))
    for k in range(3): d.ellipse([815,125+k*45,855,165+k*45],fill=(150,156,170))
    d.text((735,345),"about 1 s",font=F(POPB,50),fill=WHITE,anchor="ms")
    d.text((735,385),"of a microwave",font=F(POP,28),fill=GREY,anchor="ms")
    im.save(path,quality=95)
def check(d,x,y,col):
    d.line([(x,y+14),(x+12,y+28),(x+34,y)],fill=col,width=8)
def cross(d,x,y,col):
    d.line([(x,y),(x+28,y+28)],fill=col,width=8); d.line([(x+28,y),(x,y+28)],fill=col,width=8)
def scope(path):
    W,H=1000,500; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[40,30,490,H-30],r=30,fill=(14,30,26),outline=GR)
    panel(d,[510,30,960,H-30],r=30,fill=(36,16,18),outline=RED)
    d.text((75,60),"COUNTED",font=F(POPB,36),fill=GR)
    d.text((545,60),"NOT COUNTED",font=F(POPB,36),fill=RED)
    for i,t in enumerate(["AI chips","CPU and memory","Idle backup machines","Cooling and water"]):
        y=145+i*78; check(d,75,y,GR); d.text((130,y+14),t,font=F(POP,30),fill=WHITE,anchor="lm")
    for i,t in enumerate(["Training the model","Images and video","Total daily prompts","Power-plant water"]):
        y=145+i*78; cross(d,548,y,RED); d.text((600,y+14),t,font=F(POP,30),fill=WHITE,anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); drops("d1.png"); compare("d2.png"); scope("d3.png"); print("art ok")
