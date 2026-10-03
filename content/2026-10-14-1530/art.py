import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(120,50,150)
PINK=(235,110,160); BLU=(70,150,255)
def heart(d,cx,cy,s,col):
    r=s*0.3
    d.ellipse([cx-s*0.5,cy-s*0.35,cx-s*0.5+2*r*1.1,cy-s*0.35+2*r*1.1],fill=col)
    d.ellipse([cx+s*0.5-2*r*1.1,cy-s*0.35,cx+s*0.5,cy-s*0.35+2*r*1.1],fill=col)
    d.polygon([(cx-s*0.5+2,cy-s*0.05),(cx+s*0.5-2,cy-s*0.05),(cx,cy+s*0.5)],fill=col)
def octo(d,cx,cy,s,col):
    for i in range(8):
        a=math.radians(25+i*(130/7))
        pts=[]
        for k in range(16):
            t=k/15; rr=s*(0.3+1.5*t)
            ang=a+0.45*math.sin(t*4.5+i*0.9)*t
            pts.append((cx+math.cos(ang)*rr*1.15, cy+s*0.25+math.sin(ang)*rr))
        w=int(s*0.24)
        for k in range(len(pts)-1):
            ww=max(6,int(w*(1-k/17)))
            d.line([pts[k],pts[k+1]],fill=col,width=ww)
            d.ellipse([pts[k+1][0]-ww/2,pts[k+1][1]-ww/2,pts[k+1][0]+ww/2,pts[k+1][1]+ww/2],fill=col)
    d.ellipse([cx-s*0.7,cy-s*0.95,cx+s*0.7,cy+s*0.6],fill=col)
    for ex in (-0.3,0.3):
        d.ellipse([cx+ex*s-s*0.13,cy+s*0.05,cx+ex*s+s*0.13,cy+s*0.31],fill=WHITE)
        d.ellipse([cx+ex*s-s*0.06,cy+s*0.12,cx+ex*s+s*0.06,cy+s*0.27],fill=(20,10,30))
def drop(d,cx,cy,s,col):
    d.ellipse([cx-s*0.5,cy-s*0.1,cx+s*0.5,cy+s*0.9],fill=col)
    d.polygon([(cx-s*0.45,cy+s*0.2),(cx+s*0.45,cy+s*0.2),(cx,cy-s*0.75)],fill=col)
def cover(path):
    W,H=1080,900; im=base((W,H),(30,14,44),(5,4,10),T)
    im=addglow(im,lambda d:(d.ellipse([260,80,820,640],fill=(200,80,200)),d.ellipse([700,450,1050,850],fill=(40,120,255))),120,0.5)
    d=ImageDraw.Draw(im)
    octo(d,540,250,170,(196,72,120))
    # three hearts on the body
    heart(d,475,155,56,PINK); heart(d,605,155,56,PINK); heart(d,540,95,74,(255,150,190))
    d.text((150,150),"3 hearts",font=F(POPB,52),fill=PINK,anchor="mm")
    drop(d,940,110,90,BLU); d.text((940,245),"blue blood",font=F(POPB,40),fill=BLU,anchor="mm")
    d.text((540,660),"2/3 of neurons in the arms",font=F(POPB,40),fill=AMB,anchor="ms")
    im.save(path,quality=95)
def hearts(path):
    W,H=1000,460; im=base((W,H),(30,14,44),(5,4,10),T); d=ImageDraw.Draw(im)
    for x,lab in ((200,"قلب آبشش"),(800,"قلب آبشش")):
        heart(d,x,170,140,PINK); fa(d,(x,300),lab,F(VB,38),WHITE,"ma")
    heart(d,500,160,200,(255,150,190)); fa(d,(500,300),"قلب اصلی",F(VB,44),AMB,"ma")
    d.text((500,410),"systemic heart pauses while swimming",font=F(POP,28),fill=GREY,anchor="ma")
    im.save(path,quality=95)
def blood(path):
    W,H=1000,460; im=base((W,H),(14,20,44),(4,5,10),(40,70,160)); d=ImageDraw.Draw(im)
    drop(d,730,110,180,(220,50,60)); d.text((730,182),"Fe",font=F(POPB,60),fill=WHITE,anchor="mm")
    fa(d,(730,330),"آدم: آهن",F(VB,42),WHITE,"ma")
    drop(d,270,110,180,BLU); d.text((270,182),"Cu",font=F(POPB,60),fill=WHITE,anchor="mm")
    fa(d,(270,330),"اختاپوس: مس",F(VB,42),WHITE,"ma")
    d.text((270,400),"haemocyanin",font=F(POP,28),fill=GREY,anchor="ma")
    d.text((730,400),"haemoglobin",font=F(POP,28),fill=GREY,anchor="ma")
    im.save(path,quality=95)
def neurons(path):
    W,H=1000,480; im=base((W,H),(30,14,44),(5,4,10),T); d=ImageDraw.Draw(im)
    cx,cy,r=300,240,180
    d.pieslice([cx-r,cy-r,cx+r,cy+r],-90,150,fill=AMB)
    d.pieslice([cx-r,cy-r,cx+r,cy+r],150,270,fill=(110,90,150))
    d.text((cx+40,cy+20),"2/3",font=F(POPB,64),fill=(30,20,10),anchor="mm")
    d.rounded_rectangle([560,130,600,170],radius=10,fill=AMB); fa(d,(920,125),"تو بازوها",F(VB,44),WHITE)
    d.rounded_rectangle([560,250,600,290],radius=10,fill=(110,90,150)); fa(d,(920,245),"مغز مرکزی و بقیه",F(VB,44),WHITE)
    d.text((560,390),"~500 million neurons",font=F(POPB,34),fill=GREY)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); hearts("d1.png"); blood("d2.png"); neurons("d3.png"); print("art ok")
