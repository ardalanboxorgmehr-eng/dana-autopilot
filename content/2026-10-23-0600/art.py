import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(110,50,150)
C1=(30,16,44); C2=(6,4,12)
PUR=(190,130,255)
def arrow(d,p0,p1,col,w=8,hl=28):
    (x0,y0),(x1,y1)=p0,p1; L=math.hypot(x1-x0,y1-y0); ux,uy=(x1-x0)/L,(y1-y0)/L
    bx,by=x1-ux*hl,y1-uy*hl
    d.line([(x0,y0),(bx,by)],fill=col,width=w)
    d.polygon([(x1,y1),(bx-uy*hl*0.6,by+ux*hl*0.6),(bx+uy*hl*0.6,by-ux*hl*0.6)],fill=col)
def chip(d,cx,cy,s,col):
    d.rounded_rectangle([cx-s,cy-s,cx+s,cy+s],radius=int(s*0.25),fill=(30,30,44),outline=col,width=5)
    d.rounded_rectangle([cx-s*0.5,cy-s*0.5,cx+s*0.5,cy+s*0.5],radius=int(s*0.12),fill=col)
    for k in (-0.5,0,0.5):
        for sx in (-1,1):
            d.line([(cx+sx*s,cy+k*s),(cx+sx*s*1.35,cy+k*s)],fill=col,width=6)
            d.line([(cx+k*s,cy+sx*s),(cx+k*s,cy+sx*s*1.35)],fill=col,width=6)
def bub(d,box,col):
    d.rounded_rectangle(box,radius=18,fill=col)
def window(d,x,y,w,h,label,col,lines):
    panel(d,[x,y,x+w,y+h],r=30,fill=(22,18,34),outline=col,w=5)
    d.rounded_rectangle([x,y,x+w,y+70],radius=30,fill=col); d.rectangle([x,y+40,x+w,y+70],fill=col)
    d.text((x+w/2,y+35),label,font=F(POPB,34),fill=(16,12,24),anchor="mm")
    yy=y+100
    for side,wd in lines:
        if side=="l": bub(d,[x+25,yy,x+25+wd,yy+48],(54,48,76))
        else: bub(d,[x+w-25-wd,yy,x+w-25,yy+48],(80,70,130))
        yy+=68
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:(d.ellipse([560,140,1040,700],fill=(80,220,150)),d.ellipse([40,140,520,700],fill=(140,80,255))),130,0.45)
    d=ImageDraw.Draw(im)
    d.text((W/2,105),"73%",font=F(POPB,140),fill=AMB,anchor="mm")
    L=[("l",260),("r",180),("l",300),("r",220)]
    window(d,60,215,440,410,"A",PUR,L)
    window(d,580,215,440,410,"B",GR,[("l",220),("r",250),("l",280),("r",160)])
    d.rounded_rectangle([630,560,970,680],radius=34,fill=GR)
    d.text((800,598),"Judged human",font=F(POPB,34),fill=(10,20,16),anchor="mm")
    d.text((800,645),"It was the AI",font=F(POP,28),fill=(10,40,28),anchor="mm")
    im.save(path,quality=95)
def setup(path):
    W,H=1000,480; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    # interrogator centre
    person(d,500,270,100,(200,190,230))
    d.text((500,400),"Judge",font=F(POPB,34),fill=WHITE,anchor="mm")
    # human left
    person(d,140,220,90,(150,156,170))
    d.text((140,350),"Human",font=F(POPB,30),fill=WHITE,anchor="mm")
    chip(d,860,190,60,GR)
    d.text((860,350),"AI",font=F(POPB,30),fill=WHITE,anchor="mm")
    arrow(d,(400,200),(250,200),PUR); arrow(d,(600,200),(760,200),PUR)
    # clock
    d.ellipse([400,25,490,115],outline=AMB,width=6)
    d.line([(445,70),(445,42)],fill=AMB,width=6); d.line([(445,70),(468,82)],fill=AMB,width=6)
    d.text((510,70),"5 min",font=F(POPB,38),fill=AMB,anchor="lm")
    d.text((500,452),"chats with both at once, then picks one",font=F(POP,26),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def chart(path):
    W,H=1000,560; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    rows=[("GPT-4.5 + persona",73,AMB),("LLaMa-3.1 + persona",56,PUR),("GPT-4.5, no persona",36,(130,120,170)),("ELIZA (1966)",23,(120,126,140)),("GPT-4o, no persona",21,(120,126,140))]
    x0,x1=60,940; y=40
    mx=x0+(x1-x0)*0.5
    for yy in range(70,530,22): d.line([(mx,yy),(mx,yy+12)],fill=(150,150,170),width=3)
    for lab,v,col in rows:
        d.text((x0,y),lab,font=F(POPB,28),fill=WHITE)
        by=y+44; d.rounded_rectangle([x0,by,x1,by+36],radius=18,fill=(40,34,56))
        bw=int((x1-x0)*v/100); d.rounded_rectangle([x0,by,x0+bw,by+36],radius=18,fill=col)
        d.text((x0+bw-14,by+18),f"{v}%",font=F(POPB,26),fill=(14,10,20),anchor="rm")
        y+=100
    d.text((mx+10,530),"50% = coin flip",font=F(POP,24),fill=GREY,anchor="ls")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); setup("d1.png"); chart("d2.png"); print("art ok")
