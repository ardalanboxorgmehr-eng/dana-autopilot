import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,140,90)
def passport(d,x,y,s):
    d.rounded_rectangle([x,y,x+s,y+s*1.35],radius=10,fill=(30,60,120),outline=(200,180,90),width=3)
    d.ellipse([x+s*0.3,y+s*0.4,x+s*0.7,y+s*0.8],outline=(220,190,90),width=4)
    d.rounded_rectangle([x+s*0.2,y+s*1.0,x+s*0.8,y+s*1.08],radius=4,fill=(220,190,90))
def drawer(d,x,y,w,h):
    d.rectangle([x,y,x+w,y+h],fill=(110,80,56),outline=(70,50,34),width=5)
    d.rectangle([x+20,y+20,x+w-20,y+h/2-8],fill=(130,96,66),outline=(80,58,40),width=4)
    d.rectangle([x+20,y+h/2+8,x+w-20,y+h-20],fill=(130,96,66),outline=(80,58,40),width=4)
    for yy in (y+h/4+6,y+3*h/4-6): d.rounded_rectangle([x+w/2-40,yy-8,x+w/2+40,yy+8],radius=8,fill=(210,200,180))
def bubble(d,box,t,f,col=(38,44,58)):
    d.rounded_rectangle(box,radius=26,fill=col)
    x0,y0,x1,y1=box; lines=[]; cur=""
    for w in t.split(" "):
        tt=(cur+" "+w).strip()
        if d.textlength(tt,font=f)<=x1-x0-50: cur=tt
        else: lines.append(cur); cur=w
    lines.append(cur)
    for i,l in enumerate(lines): d.text((x0+25,y0+22+i*f.size*1.35),l,font=f,fill=WHITE)
def cover(path):
    W,H=1080,900; im=base((W,H),(12,34,24),(4,8,6),T)
    im=addglow(im,lambda d:d.ellipse([520,120,1040,760],fill=(80,220,150)),120,0.5)
    d=ImageDraw.Draw(im)
    drawer(d,80,380,380,330); passport(d,200,300,120)
    d.ellipse([230,250,290,290],fill=AMB); d.polygon([(245,285),(275,285),(260,330)],fill=AMB)
    x0,y0,x1,y1=phone(d,600,110,380,720)
    d.text((630,180),"Gemini",font=F(POPB,34),fill=(150,190,255))
    bubble(d,[630,240,960,470],"Remember in Find Hub that my passport is in the top bedroom drawer.",F(POP,28),(40,64,110))
    bubble(d,[630,500,960,640],"Saved to Find Hub · Remembered",F(POPB,26),(28,70,52))
    d.ellipse([760,700,830,770],fill=(150,190,255)); d.rounded_rectangle([783,715,807,750],radius=12,fill=(20,24,32))
    im.save(path,quality=95)
def listui(path):
    W,H=1000,520; im=base((W,H),(12,34,24),(4,8,6),T); d=ImageDraw.Draw(im)
    panel(d,[60,30,W-60,H-30],r=30,fill=(18,24,22),outline=(80,160,120))
    d.text((100,60),"Remembered",font=F(POPB,40),fill=WHITE)
    rows=[("Passport","Top bedroom drawer"),("Spare key","Kitchen drawer"),("Laptop charger","Blue backpack")]
    for i,(a,b) in enumerate(rows):
        y=140+i*115; d.rounded_rectangle([100,y,W-100,y+95],radius=20,fill=(30,40,36))
        d.ellipse([120,y+22,170,y+72],fill=GR)
        d.text((190,y+28),a,font=F(POPB,30),fill=WHITE); d.text((190,y+64),b,font=F(POP,24),fill=GREY)
    im.save(path,quality=95)
def ask(path):
    W,H=1000,400; im=base((W,H),(12,34,24),(4,8,6),T); d=ImageDraw.Draw(im)
    bubble(d,[380,40,940,150],"Where is my passport?",F(POP,34),(40,64,110))
    bubble(d,[60,190,760,350],"Your passport is in the top bedroom drawer.",F(POP,34),(28,70,52))
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); listui("d1.png"); ask("d2.png"); print("art ok")
