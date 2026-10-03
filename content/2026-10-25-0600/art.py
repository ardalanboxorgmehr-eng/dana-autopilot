import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,120,60)
C1=(12,30,18); C2=(3,8,5)
PH=(110,255,140)
def arrow(d,p0,p1,col,w=10,hl=34):
    (x0,y0),(x1,y1)=p0,p1; L=math.hypot(x1-x0,y1-y0); ux,uy=(x1-x0)/L,(y1-y0)/L
    bx,by=x1-ux*hl,y1-uy*hl
    d.line([(x0,y0),(bx,by)],fill=col,width=w)
    d.polygon([(x1,y1),(bx-uy*hl*0.6,by+ux*hl*0.6),(bx+uy*hl*0.6,by-ux*hl*0.6)],fill=col)
def heart(d,cx,cy,s,col):
    d.ellipse([cx-s,cy-s*0.6,cx,cy+s*0.4],fill=col); d.ellipse([cx,cy-s*0.6,cx+s,cy+s*0.4],fill=col)
    d.polygon([(cx-s*0.97,cy),(cx+s*0.97,cy),(cx,cy+s*1.1)],fill=col)
def gear(d,cx,cy,r,col,bg):
    for k in range(8):
        a=math.radians(k*45); d.line([(cx,cy),(cx+math.cos(a)*r*1.25,cy+math.sin(a)*r*1.25)],fill=col,width=int(r*0.45))
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col); d.ellipse([cx-r*0.4,cy-r*0.4,cx+r*0.4,cy+r*0.4],fill=bg)
def crt(d,x,y,w,h):
    d.rounded_rectangle([x,y,x+w,y+h],radius=40,fill=(190,180,150),outline=(120,112,90),width=6)
    d.rounded_rectangle([x+40,y+40,x+w-40,y+h-90],radius=30,fill=(6,22,10),outline=(40,60,40),width=6)
    d.rounded_rectangle([x+w*0.3,y+h,x+w*0.7,y+h+40],radius=8,fill=(150,140,115))
    d.ellipse([x+w-90,y+h-70,x+w-60,y+h-40],fill=(220,80,60))
    return (x+70,y+70)
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:d.ellipse([140,80,940,700],fill=(80,220,120)),130,0.4)
    d=ImageDraw.Draw(im)
    tx,ty=crt(d,140,60,800,600)
    f=F(POPB,34); g=F(POP,34)
    lines=[("> I am unhappy.",WHITE,g),("HOW LONG HAVE YOU BEEN",PH,f),("UNHAPPY?",PH,f),("> My boyfriend made me come here.",WHITE,g),("YOUR BOYFRIEND MADE YOU",PH,f),("COME HERE?",PH,f)]
    for i,(t,c,ff) in enumerate(lines): d.text((tx,ty+i*62),t,font=ff,fill=c)
    d.rectangle([tx,ty+6*62+6,tx+22,ty+6*62+42],fill=PH)
    d.text((W/2,770),"1966",font=F(POPB,90),fill=AMB,anchor="mm")
    im.save(path,quality=95)
def rule(path):
    W,H=1000,420; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[40,60,420,250],r=26,fill=(14,30,20),outline=(80,140,90))
    d.text((230,110),"you type",font=F(POP,28),fill=GREY,anchor="mm")
    d.text((230,170),"I am [X]",font=F(POPB,48),fill=WHITE,anchor="mm")
    arrow(d,(440,155),(560,155),WHITE,10)
    panel(d,[580,60,960,250],r=26,fill=(14,30,20),outline=PH)
    d.text((770,110),"ELIZA replies",font=F(POP,28),fill=GREY,anchor="mm")
    d.text((770,165),"How long have you",font=F(POPB,34),fill=PH,anchor="mm")
    d.text((770,210),"been [X]?",font=F(POPB,34),fill=PH,anchor="mm")
    d.text((W/2,320),"keyword in, template out",font=F(POPB,36),fill=AMB,anchor="mm")
    d.text((W/2,370),"no understanding at all",font=F(POP,30),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def effect(path):
    W,H=1000,440; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[40,40,480,H-40],r=30,fill=(40,16,22),outline=(240,110,130))
    heart(d,260,170,90,(240,90,120))
    d.text((260,330),"what people felt",font=F(POPB,32),fill=WHITE,anchor="mm")
    panel(d,[520,40,960,H-40],r=30,fill=(14,30,20),outline=PH)
    gear(d,690,170,56,PH,(14,30,20)); gear(d,800,230,38,(80,180,110),(14,30,20))
    d.text((740,330),"what it actually did",font=F(POPB,32),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def bars2(path):
    W,H=1000,400; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    d.text((60,40),"Judged human in a 2025 Turing test",font=F(POPB,32),fill=WHITE)
    rows=[("ELIZA (1966)",23,PH),("GPT-4o, no persona",21,(120,126,140))]
    x0,x1=60,940; y=110
    for lab,v,col in rows:
        d.text((x0,y),lab,font=F(POPB,30),fill=WHITE)
        by=y+48; d.rounded_rectangle([x0,by,x1,by+44],radius=22,fill=(34,44,38))
        bw=int((x1-x0)*v/100); d.rounded_rectangle([x0,by,x0+bw,by+44],radius=22,fill=col)
        d.text((x0+bw+16,by+22),f"{v}%",font=F(POPB,32),fill=WHITE,anchor="lm")
        y+=125
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); rule("d1.png"); effect("d2.png"); bars2("d3.png"); print("art ok")
