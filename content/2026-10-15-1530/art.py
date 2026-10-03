import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,70,160)
def robot(d,cx,cy,s,col):
    d.line([(cx,cy-s*0.9),(cx,cy-s*0.65)],fill=col,width=6); d.ellipse([cx-12,cy-s*0.95-12,cx+12,cy-s*0.95+12],fill=col)
    d.rounded_rectangle([cx-s*0.6,cy-s*0.65,cx+s*0.6,cy+s*0.2],radius=int(s*0.2),fill=col)
    d.ellipse([cx-s*0.35,cy-s*0.4,cx-s*0.12,cy-s*0.17],fill=(20,24,34)); d.ellipse([cx+s*0.12,cy-s*0.4,cx+s*0.35,cy-s*0.17],fill=(20,24,34))
    d.rounded_rectangle([cx-s*0.5,cy+s*0.3,cx+s*0.5,cy+s*0.9],radius=int(s*0.2),fill=col)
def headset_person(d,cx,cy,s,col):
    person(d,cx,cy,s,col,(200,170,140))
    d.arc([cx-s*0.42,cy-s*1.0,cx+s*0.42,cy-s*0.2],200,340,fill=(30,30,36),width=10)
    d.rounded_rectangle([cx-s*0.48,cy-s*0.66,cx-s*0.32,cy-s*0.42],radius=6,fill=(30,30,36))
    d.line([(cx-s*0.38,cy-s*0.45),(cx-s*0.1,cy-s*0.3)],fill=(30,30,36),width=6)
def cover(path):
    W,H=1080,900; im=base((W,H),(14,20,46),(4,6,12),T)
    im=addglow(im,lambda d:(d.ellipse([60,120,560,700],fill=(80,140,255)),d.ellipse([560,160,1060,740],fill=(255,150,90))),120,0.45)
    d=ImageDraw.Draw(im)
    # robot mask lifted off a human
    panel(d,[90,120,500,660],r=40,fill=(20,26,44),outline=(110,150,255),w=5)
    robot(d,295,350,190,(130,170,255))
    d.text((295,600),"AI agent",font=F(POPB,40),fill=(150,190,255),anchor="mm")
    d.polygon([(530,370),(600,370),(600,340),(650,390),(600,440),(600,410),(530,410)],fill=WHITE)
    panel(d,[680,120,1000,660],r=40,fill=(44,30,24),outline=(255,170,90),w=5)
    headset_person(d,840,420,200,(230,140,80))
    d.text((840,600),"Human",font=F(POPB,40),fill=(255,190,120),anchor="mm")
    im.save(path,quality=95)
def flow(path):
    W,H=1000,360; im=base((W,H),(14,20,46),(4,6,12),T); d=ImageDraw.Draw(im)
    nodes=[("You",GREY),("Muse",BLUE),("Call center",(255,170,90)),("Business",GR)]
    xs=[100,367,633,900]
    for (t,c),x in zip(nodes,xs):
        panel(d,[x-92,110,x+92,250],r=26,fill=(18,22,34),outline=c,w=4)
        d.text((x,180),t,font=fiten(d,t,POPB,150,34),fill=c,anchor="mm")
    for i in range(3):
        a=xs[i]+100; b=xs[i+1]-100
        d.polygon([(a,170),(b-22,170),(b-22,155),(b,180),(b-22,205),(b-22,190),(a,190)],fill=WHITE)
    d.text((630,300),"human places the call",font=F(POPB,28),fill=(255,190,120),anchor="mm")
    im.save(path,quality=95)
def privacy(path):
    W,H=1000,420; im=base((W,H),(14,20,46),(4,6,12),T); d=ImageDraw.Draw(im)
    d.rounded_rectangle([60,60,600,200],radius=28,fill=(40,64,110))
    d.text((90,95),"Book me a doctor's appointment",font=F(POP,30),fill=WHITE)
    d.text((90,140),"for my test results",font=F(POP,30),fill=WHITE)
    d.polygon([(630,220),(700,220),(700,195),(745,240),(700,285),(700,260),(630,260)],fill=WHITE)
    panel(d,[770,90,950,370],r=26,fill=(44,30,24),outline=(255,170,90),w=4)
    headset_person(d,860,270,120,(230,140,80))
    d.rounded_rectangle([60,240,420,300],radius=20,fill=(60,30,30))
    d.text((90,270),"Who can see this?",font=F(POPB,28),fill=(255,150,150),anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); flow("d1.png"); privacy("d2.png"); print("art ok")
