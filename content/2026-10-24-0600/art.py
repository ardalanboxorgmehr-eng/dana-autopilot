import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(150,100,30)
C1=(40,28,12); C2=(10,7,4)
ORG=(255,160,70)
def arrowhead(d,x1,y1,ux,uy,col,hl=26):
    bx,by=x1-ux*hl,y1-uy*hl
    d.polygon([(x1,y1),(bx-uy*hl*0.6,by+ux*hl*0.6),(bx+uy*hl*0.6,by-ux*hl*0.6)],fill=col)
def bubble(d,box,t,f,col,tc=WHITE):
    x0,y0,x1,y1=box; lines=[]; cur=""
    for w in t.split(" "):
        tt=(cur+" "+w).strip()
        if d.textlength(tt,font=f)<=x1-x0-50: cur=tt
        else: lines.append(cur); cur=w
    lines.append(cur)
    y1=y0+34+len(lines)*f.size*1.35
    d.rounded_rectangle([x0,y0,x1,y1],radius=26,fill=col)
    for i,l in enumerate(lines): d.text((x0+25,y0+16+i*f.size*1.35),l,font=f,fill=tc)
    return y1
def bulb(d,cx,cy,s,col):
    d.ellipse([cx-s,cy-s,cx+s,cy+s],fill=col)
    d.rounded_rectangle([cx-s*0.5,cy+s*0.75,cx+s*0.5,cy+s*1.35],radius=8,fill=col)
    for k in range(3): d.line([(cx-s*0.5,cy+s*(0.95+k*0.17)),(cx+s*0.5,cy+s*(0.95+k*0.17))],fill=(60,40,20),width=4)
    for a in range(-150,-20,26):
        r=math.radians(a); d.line([(cx+math.cos(r)*s*1.3,cy+math.sin(r)*s*1.3),(cx+math.cos(r)*s*1.65,cy+math.sin(r)*s*1.65)],fill=col,width=7)
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:(d.ellipse([60,100,560,600],fill=(255,180,60)),d.ellipse([560,180,1060,700],fill=(80,160,255))),130,0.45)
    d=ImageDraw.Draw(im)
    bulb(d,250,330,120,AMB)
    d.text((250,600),"explain it simply",font=F(POPB,40),fill=WHITE,anchor="mm")
    x0,y0,x1,y1=phone(d,560,90,420,640)
    y=y0+40
    y=bubble(d,[x1-340,y,x1-10,0],"Plants make food from light.",F(POP,30),(150,95,30))+40
    for t in ["Why light?","What does 'make food' mean?","Where does the food go?"]:
        y=bubble(d,[x0+10,y,x0+320,0],t,F(POPB,30),(40,64,110))+28
    im.save(path,quality=95)
def prompt(path):
    W,H=1000,440; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[40,30,W-40,H-30],r=30,fill=(26,22,18),outline=(110,90,60))
    d.text((90,70),"PROMPT",font=F(POPB,28),fill=AMB)
    f=F(POP,36); t="I'll explain a topic. Act like a curious 12-year-old. Ask me why, point out gaps, and don't explain it for me."
    lines=[];cur=""
    for w in t.split(" "):
        tt=(cur+" "+w).strip()
        if d.textlength(tt,font=f)<=W-180: cur=tt
        else: lines.append(cur); cur=w
    lines.append(cur)
    for i,l in enumerate(lines): d.text((90,130+i*58),l,font=f,fill=WHITE)
    im.save(path,quality=95)
def cycle(path):
    W,H=1000,560; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    cx,cy,R=W/2,H/2,165
    nodes=[(-90,"1","Explain simply",AMB),(0,"2","Find the gaps",ORG),(90,"3","Back to the source",BLUE),(180,"4","Simplify, repeat",GR)]
    # clockwise arcs with arrowheads
    for a0 in (-90,0,90,180):
        a1=a0+90; s0,s1=a0+20,a1-20
        d.arc([cx-R,cy-R,cx+R,cy+R],s0,s1,fill=(200,200,210),width=8)
        r=math.radians(s1); ex,ey=cx+R*math.cos(r),cy+R*math.sin(r)
        arrowhead(d,ex,ey,-math.sin(r),math.cos(r),(200,200,210))
    for ang,n,t,c in nodes:
        r=math.radians(ang); x,y=cx+R*math.cos(r),cy+R*math.sin(r)
        d.ellipse([x-42,y-42,x+42,y+42],fill=c)
        d.text((x,y),n,font=F(POPB,44),fill=(20,14,8),anchor="mm")
    fl=F(POPB,30)
    d.text((cx,cy-R-62),"Explain simply",font=fl,fill=WHITE,anchor="mm")
    d.text((cx+R+60,cy),"Find the gaps",font=fl,fill=WHITE,anchor="lm")
    d.text((cx,cy+R+62),"Back to the source",font=fl,fill=WHITE,anchor="mm")
    d.text((cx-R-60,cy),"Simplify, repeat",font=fl,fill=WHITE,anchor="rm")
    im.save(path,quality=95)
def chat(path):
    W,H=1000,500; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    d.text((W-70,40),"YOU (teacher)",font=F(POPB,26),fill=AMB,anchor="ra")
    bubble(d,[300,80,W-60,200],"Inflation is when money buys less over time.",F(POP,30),(150,95,30))
    d.text((70,230),"AI (curious student)",font=F(POPB,26),fill=BLUE)
    bubble(d,[60,270,720,450],"Why does money buy less? Who decides that? Can you give me an example?",F(POP,30),(40,64,110))
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); cycle("d1.png"); chat("d2.png"); prompt("d3.png"); print("art ok")
