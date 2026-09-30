import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(190,60,40)
def burger(d,cx,cy,s):
    d.chord([cx-s,cy-s*0.9,cx+s,cy+s*0.5],180,360,fill=(226,150,60))
    for i in range(7):
        x=cx-s*0.6+i*s*0.2; d.ellipse([x-5,cy-s*0.55+(i%2)*14,x+5,cy-s*0.55+(i%2)*14+8],fill=(250,230,180))
    d.rounded_rectangle([cx-s*1.02,cy-s*0.22,cx+s*1.02,cy-s*0.02],radius=10,fill=(90,190,70))
    d.rounded_rectangle([cx-s*0.98,cy-s*0.02,cx+s*0.98,cy+s*0.22],radius=14,fill=(110,58,40))
    d.rounded_rectangle([cx-s*1.0,cy+s*0.22,cx+s*1.0,cy+s*0.34],radius=6,fill=(250,200,60))
    d.rounded_rectangle([cx-s*0.98,cy+s*0.34,cx+s*0.98,cy+s*0.62],radius=20,fill=(220,140,60))
def store(d,x,y,w,h,col):
    d.rectangle([x,y+60,x+w,y+h],fill=(34,30,34),outline=(90,80,86),width=4)
    d.polygon([(x-20,y+70),(x+w/2,y),(x+w+20,y+70)],fill=col)
    d.rectangle([x+w*0.35,y+h-120,x+w*0.65,y+h],fill=(70,60,60))
    for k in range(2): d.rectangle([x+30+k*(w-150),y+110,x+120+k*(w-150),y+190],fill=(255,220,140))
def tag(d,cx,cy,t,col):
    f=F(POPB,58); tw=d.textlength(t,font=f)+60
    d.rounded_rectangle([cx-tw/2,cy-50,cx+tw/2,cy+50],radius=26,fill=col)
    d.text((cx,cy),t,font=f,fill=(12,12,14),anchor="mm")
def cover(path):
    W,H=1080,900; im=base((W,H),(40,16,12),(6,4,4),T)
    im=addglow(im,lambda d:(d.ellipse([60,160,480,640],fill=(80,200,120)),d.ellipse([600,160,1020,640],fill=(255,80,60))),110,0.5)
    d=ImageDraw.Draw(im)
    store(d,110,250,300,360,(80,90,100)); store(d,670,250,300,360,(80,90,100))
    burger(d,260,690,90); burger(d,820,690,90)
    tag(d,260,170,"$5.69",GR); tag(d,820,170,"$6.89",RED)
    d.line([(430,520),(650,520)],fill=WHITE,width=5)
    for x in (430,650): d.line([(x,500),(x,540)],fill=WHITE,width=5)
    d.text((540,480),"2 miles",font=F(POPB,38),fill=AMB,anchor="ms")
    d.text((540,580),"+21%",font=F(POPB,56),fill=RED,anchor="mm")
    im.save(path,quality=95)
def flow(path):
    W,H=1000,480; im=base((W,H),(40,16,12),(6,4,4),T); d=ImageDraw.Draw(im)
    ins=["Sales data","Competitor prices","Willingness to pay"]
    for i,t in enumerate(ins):
        y=50+i*140; panel(d,[40,y,420,y+100],r=24,fill=(30,26,30),outline=(120,100,100))
        d.text((230,y+50),t,font=fiten(d,t,POPB,340,34),fill=WHITE,anchor="mm")
        d.line([(420,y+50),(560,240)],fill=(150,140,140),width=4)
    d.rounded_rectangle([560,160,720,320],radius=30,fill=(60,40,110),outline=(170,120,255),width=4)
    d.text((640,240),"AI",font=F(POPB,64),fill=WHITE,anchor="mm")
    d.line([(720,240),(790,240)],fill=WHITE,width=5); d.polygon([(810,240),(785,225),(785,255)],fill=WHITE)
    panel(d,[820,170,970,310],r=24,fill=(40,30,24),outline=AMB)
    d.text((895,240),"$ ?",font=F(POPB,50),fill=AMB,anchor="mm")
    im.save(path,quality=95)
def compare(path):
    W,H=1000,420; im=base((W,H),(40,16,12),(6,4,4),T); d=ImageDraw.Draw(im)
    fa(d,(W-60,60),"فروشگاه اول",F(VB,36),WHITE); fa(d,(W-60,220),"فروشگاه دوم",F(VB,36),WHITE)
    for i,(v,t,c) in enumerate([(5.69,"$5.69",GR),(6.89,"$6.89",RED)]):
        y=120+i*160; w=int(820*v/6.89)
        d.rounded_rectangle([60,y,60+820,y+60],radius=30,fill=(40,36,40))
        d.rounded_rectangle([60+820-w,y,60+820,y+60],radius=30,fill=c)
        d.text((60+820-w+24,y+30),t,font=F(POPB,36),fill=(12,12,14),anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); flow("d1.png"); compare("d2.png"); print("art ok")
