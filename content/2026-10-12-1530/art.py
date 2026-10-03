import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(120,60,170)
PUR=(170,120,255)
def figure(d,cx,top,h,body,skin=(205,170,140)):
    s=h/10
    d.ellipse([cx-s*0.9,top,cx+s*0.9,top+s*1.9],fill=skin)
    d.rounded_rectangle([cx-s*0.45,top+s*1.8,cx+s*0.45,top+s*2.3],radius=6,fill=skin)
    d.rounded_rectangle([cx-s*1.9,top+s*2.2,cx+s*1.9,top+s*6.0],radius=int(s*0.8),fill=body)
    d.rounded_rectangle([cx-s*2.5,top+s*2.4,cx-s*1.75,top+s*5.6],radius=int(s*0.35),fill=body)
    d.rounded_rectangle([cx+s*1.75,top+s*2.4,cx+s*2.5,top+s*5.6],radius=int(s*0.35),fill=body)
    d.rounded_rectangle([cx-s*1.5,top+s*5.9,cx-s*0.15,top+s*9.8],radius=int(s*0.3),fill=(50,58,80))
    d.rounded_rectangle([cx+s*0.15,top+s*5.9,cx+s*1.5,top+s*9.8],radius=int(s*0.3),fill=(50,58,80))
def jacket(d,cx,cy,w,col):
    h=w*1.05
    d.polygon([(cx-w*0.3,cy-h/2),(cx+w*0.3,cy-h/2),(cx+w/2,cy-h*0.3),(cx+w/2,cy+h/2),(cx-w/2,cy+h/2),(cx-w/2,cy-h*0.3)],fill=col)
    d.polygon([(cx-w*0.15,cy-h/2),(cx,cy-h*0.2),(cx+w*0.15,cy-h/2)],fill=(30,30,40))
    d.line([(cx,cy-h*0.2),(cx,cy+h/2)],fill=(30,30,40),width=4)
def cover(path):
    W,H=1080,900; im=base((W,H),(30,16,46),(6,4,10),T)
    im=addglow(im,lambda d:(d.ellipse([60,120,520,700],fill=(140,90,255)),d.ellipse([560,160,1040,720],fill=(255,120,170))),120,0.5)
    d=ImageDraw.Draw(im)
    # left: product card with Try on button
    panel(d,[70,110,440,640],r=30,fill=(22,20,34),outline=PUR,w=4)
    d.rounded_rectangle([100,140,410,440],radius=20,fill=(44,40,66))
    jacket(d,255,290,170,(230,90,120))
    d.text((100,465),"Wool jacket",font=F(POPB,32),fill=WHITE)
    d.text((100,510),"$89",font=F(POP,28),fill=GREY)
    d.rounded_rectangle([100,560,410,615],radius=28,fill=WHITE)
    d.text((255,588),"Try on",font=F(POPB,30),fill=(20,20,28),anchor="mm")
    # arrow left -> right
    d.polygon([(470,380),(560,380),(560,350),(615,400),(560,450),(560,420),(470,420)],fill=WHITE)
    # right: phone with figure wearing jacket
    x0,y0,x1,y1=phone(d,650,90,360,640)
    figure(d,830,170,480,(230,90,120))
    d.rounded_rectangle([690,640,970,690],radius=16,fill=(40,30,70))
    d.text((830,665),"Images 2.5",font=F(POPB,26),fill=PUR,anchor="mm")
    im.save(path,quality=95)
def screenshot(path):
    W,H=1000,460; im=base((W,H),(30,16,46),(6,4,10),T); d=ImageDraw.Draw(im)
    # screenshot of item
    panel(d,[50,60,300,400],r=24,fill=(236,236,244),outline=(200,200,210),w=3)
    d.rounded_rectangle([70,80,280,110],radius=10,fill=(200,204,216))
    jacket(d,175,250,150,(60,140,220))
    d.text((175,385),"screenshot",font=F(POPB,22),fill=(90,90,100),anchor="ms")
    d.text((345,230),"+",font=F(POPB,70),fill=WHITE,anchor="mm")
    # selfie
    panel(d,[390,60,590,400],r=24,fill=(40,36,60),outline=PUR,w=3)
    figure(d,490,100,280,(120,124,140))
    d.text((490,385),"your photo",font=F(POPB,22),fill=GREY,anchor="ms")
    d.polygon([(620,215),(700,215),(700,190),(745,230),(700,270),(700,245),(620,245)],fill=WHITE)
    panel(d,[770,60,960,400],r=24,fill=(40,36,60),outline=GR,w=4)
    figure(d,865,100,280,(60,140,220))
    d.text((865,385),"result",font=F(POPB,22),fill=GR,anchor="ms")
    im.save(path,quality=95)
def settings(path):
    W,H=1000,480; im=base((W,H),(30,16,46),(6,4,10),T); d=ImageDraw.Draw(im)
    panel(d,[60,30,W-60,H-30],r=30,fill=(20,20,28),outline=(90,90,110))
    rows=["Settings","Personalization","Reference photos"]
    for i,t in enumerate(rows):
        y=60+i*95
        d.rounded_rectangle([100,y,W-100,y+75],radius=18,fill=(34,34,46) if i<2 else (60,40,90))
        d.text((130,y+37),t,font=F(POPB,32),fill=WHITE,anchor="lm")
        d.text((W-130,y+37),">",font=F(POPB,34),fill=GREY,anchor="rm")
    y=360
    d.rounded_rectangle([100,y,520,y+75],radius=18,fill=(34,34,46))
    d.ellipse([125,y+12,175,y+62],fill=(120,124,140))
    d.text((195,y+37),"photo_01.jpg",font=F(POP,28),fill=GREY,anchor="lm")
    d.rounded_rectangle([560,y,W-100,y+75],radius=18,fill=RED)
    d.text(((560+W-100)/2,y+37),"Delete",font=F(POPB,32),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); screenshot("d1.png"); settings("d2.png"); print("art ok")
