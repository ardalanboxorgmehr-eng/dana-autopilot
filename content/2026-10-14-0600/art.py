import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(140,90,40)
GOLD=(220,170,90)
def gavel(d,cx,cy,s,col):
    import math
    d.rounded_rectangle([cx-s*0.9,cy+s*0.9,cx+s*0.9,cy+s*1.15],radius=int(s*0.1),fill=(120,84,50))
    head=[(-s*0.55,-s*0.25),(s*0.55,-s*0.25),(s*0.55,s*0.25),(-s*0.55,s*0.25)]
    a=math.radians(-35)
    def rot(p,ox,oy): return (ox+p[0]*math.cos(a)-p[1]*math.sin(a), oy+p[0]*math.sin(a)+p[1]*math.cos(a))
    hx,hy=cx-s*0.15,cy-s*0.2
    d.polygon([rot(p,hx,hy) for p in head],fill=col)
    h1=rot((0,s*0.25),hx,hy); h2=rot((0,s*1.3),hx,hy)
    d.line([h1,h2],fill=col,width=int(s*0.16))
def screen(d,box,label=True):
    x0,y0,x1,y1=box
    panel(d,box,r=24,fill=(16,18,26),outline=(110,116,132),w=6)
    cx=(x0+x1)/2
    person(d,cx,y0+(y1-y0)*0.55,(y1-y0)*0.42,(70,90,130),(110,130,170))
    waveform(d,x0+40,y1-90,x1-x0-80,50,(120,200,255),n=40)
    if label:
        t="AI-GENERATED"; f=F(POPB,28); w=d.textlength(t,font=f)
        d.rounded_rectangle([x0+24,y0+24,x0+24+w+30,y0+70],radius=14,fill=RED)
        d.text((x0+39,y0+47),t,font=f,fill=WHITE,anchor="lm")
def cover(path):
    W,H=1080,900; im=base((W,H),(36,26,16),(8,6,4),T)
    im=addglow(im,lambda d:(d.ellipse([120,60,760,700],fill=(120,170,255)),d.ellipse([640,300,1060,800],fill=(255,170,80))),120,0.45)
    d=ImageDraw.Draw(im)
    screen(d,[90,90,700,620])
    gavel(d,860,440,150,GOLD)
    im.save(path,quality=95)
def video(path):
    W,H=1000,500; im=base((W,H),(36,26,16),(8,6,4),T); d=ImageDraw.Draw(im)
    screen(d,[200,30,800,470])
    im.save(path,quality=95)
def sentence(path):
    W,H=1000,480; im=base((W,H),(36,26,16),(8,6,4),T); d=ImageDraw.Draw(im)
    bars(d,60,30,W-120,[("درخواست وکیل",7,(120,126,140),"7 yrs"),("درخواست دادستان",9,BLUE,"9 yrs"),("حکم قاضی",10.5,RED,"10.5 yrs")],rowh=140,maxv=10.5)
    im.save(path,quality=95)
def vacated(path):
    W,H=1000,400; im=base((W,H),(36,26,16),(8,6,4),T); d=ImageDraw.Draw(im)
    panel(d,[80,40,W-80,H-40],r=26,fill=(236,232,222),outline=(200,190,170),w=3)
    for i in range(6): d.rounded_rectangle([130,90+i*38,W-130-(i%3)*80,104+i*38],radius=6,fill=(190,184,170))
    s=Image.new("RGBA",(560,160),(0,0,0,0)); sd=ImageDraw.Draw(s)
    sd.rounded_rectangle([6,6,554,154],radius=20,outline=(210,40,40),width=10)
    sd.text((280,80),"VACATED",font=F(POPB,84),fill=(210,40,40),anchor="mm")
    s=s.rotate(12,expand=True,resample=Image.BICUBIC)
    im.paste(s,(W//2-s.width//2,H//2-s.height//2),s)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); video("d1.png"); sentence("d2.png"); vacated("d3.png"); print("art ok")
