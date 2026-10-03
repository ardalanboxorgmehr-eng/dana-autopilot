import os, sys, random
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(150,110,40)
C1=(36,28,14); C2=(8,6,4)
WOOD=(214,170,96); LINE=(70,48,20)
def board(d,x,y,size,n=19,stones=(),hi=None,label=None):
    d.rounded_rectangle([x-20,y-20,x+size+20,y+size+20],radius=18,fill=WOOD)
    st=size/(n-1)
    for i in range(n):
        d.line([(x,y+i*st),(x+size,y+i*st)],fill=LINE,width=2)
        d.line([(x+i*st,y),(x+i*st,y+size)],fill=LINE,width=2)
    if n==19:
        for a in (3,9,15):
            for b in (3,9,15): d.ellipse([x+a*st-5,y+b*st-5,x+a*st+5,y+b*st+5],fill=LINE)
    r=st*0.47
    for (cx,cy,c) in stones:
        px,py=x+cx*st,y+cy*st
        d.ellipse([px-r,py-r,px+r,py+r],fill=(20,20,22) if c=="b" else (245,245,240),outline=(10,10,10),width=1)
    if hi:
        px,py=x+hi[0]*st,y+hi[1]*st
        d.ellipse([px-r*2.6,py-r*2.6,px+r*2.6,py+r*2.6],outline=AMB,width=7)
        d.ellipse([px-r*1.7,py-r*1.7,px+r*1.7,py+r*1.7],fill=(255,214,110))
        d.ellipse([px-r,py-r,px+r,py+r],fill=(20,20,22))
        if label: d.text((px,py),label,font=F(POPB,int(r*1.05)),fill=AMB,anchor="mm")
    return st
STONES=[(3,3,"b"),(15,3,"w"),(3,15,"w"),(15,15,"b"),(2,5,"w"),(5,2,"b"),(16,5,"w"),(13,2,"b"),(4,13,"b"),(2,13,"w"),(16,12,"w"),(14,16,"b"),(12,15,"w"),(9,3,"b"),(10,2,"w"),(15,9,"b"),(16,9,"w"),(3,9,"w"),(2,10,"b"),(13,4,"w"),(12,3,"b"),(17,14,"b"),(14,10,"w")]
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:d.ellipse([160,40,920,760],fill=(255,190,80)),130,0.45)
    d=ImageDraw.Draw(im)
    board(d,230,70,620,stones=STONES,hi=(4,10),label="37")
    d.rounded_rectangle([60,600,360,720],radius=30,fill=(20,16,10),outline=AMB,width=4)
    d.text((210,640),"1 in 10,000",font=F(POPB,40),fill=AMB,anchor="mm")
    d.text((210,690),"Move 37, Game 2",font=F(POP,26),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def zoom(path):
    W,H=1000,520; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    sub=[(1,3,"w"),(2,1,"b"),(3,4,"w"),(5,2,"b"),(6,5,"w"),(4,1,"b"),(8,4,"b"),(7,2,"w")]
    board(d,80,80,360,n=10,stones=sub,hi=(4,5),label="37")
    d.text((520,110),"\"Almost no human",font=F(POPB,40),fill=WHITE)
    d.text((520,165),"pro would've",font=F(POPB,40),fill=WHITE)
    d.text((520,220),"thought of it\"",font=F(POPB,40),fill=WHITE)
    d.text((520,285),"commentator, after the game",font=F(POP,26),fill=GREY)
    d.text((520,370),"Lee left the room",font=F(POPB,32),fill=AMB)
    d.text((520,412),"before answering",font=F(POPB,32),fill=AMB)
    im.save(path,quality=95)
def score(path):
    W,H=1000,460; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    d.text((W/2,70),"AlphaGo  4 - 1  Lee Sedol",font=F(POPB,54),fill=WHITE,anchor="mm")
    res=["AI","AI","AI","LEE","AI"]
    for i,r in enumerate(res):
        x=120+i*180; win=r=="LEE"
        d.ellipse([x,150,x+130,280],fill=AMB if win else (60,62,72),outline=(255,240,200) if win else (110,112,124),width=4)
        d.text((x+65,215),r,font=F(POPB,36 if win else 40),fill=(30,20,6) if win else WHITE,anchor="mm")
        d.text((x+65,320),f"Game {i+1}",font=F(POP,28),fill=GREY,anchor="mm")
    d.text((120+3*180+65,385),"Move 78",font=F(POPB,32),fill=AMB,anchor="mm")
    d.text((W/2,430),"Seoul, 9-15 March 2016",font=F(POP,26),fill=GREY,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); zoom("d1.png"); score("d2.png"); print("art ok")
