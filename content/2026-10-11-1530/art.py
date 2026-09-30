import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(180,110,30)
def cover(path):
    W,H=1080,900; im=base((W,H),(40,28,10),(6,5,3),T)
    im=addglow(im,lambda d:d.ellipse([300,120,900,760],fill=(255,170,60)),120,0.5)
    d=ImageDraw.Draw(im)
    d.rectangle([80,640,1000,670],fill=(90,70,50))
    # laptop
    d.rounded_rectangle([140,440,480,640],radius=14,fill=(30,32,40),outline=(110,116,130),width=4)
    d.text((310,540),"AI",font=F(POPB,70),fill=(150,190,255),anchor="mm")
    d.polygon([(100,640),(520,640),(540,660),(80,660)],fill=(80,84,96))
    # task pile
    cols=[(240,120,90),(90,170,240),(80,200,140),(250,200,80),(200,120,220)]
    for i in range(9):
        y=600-i*58; x=620+(i%2)*14-(i%3)*8
        d.rounded_rectangle([x,y,x+300,y+50],radius=10,fill=cols[i%5])
        d.rounded_rectangle([x+20,y+18,x+200,y+30],radius=6,fill=(255,255,255))
    d.text((770,70),"52%",font=F(POPB,64),fill=RED,anchor="mm")
    d.text((770,120),"expected to do more",font=F(POPB,28),fill=GREY,anchor="mm")
    d.text((310,380),"63%",font=F(POPB,56),fill=GR,anchor="mm")
    d.text((310,418),"say AI made them faster",font=F(POPB,24),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def good(path):
    W,H=1000,300; im=base((W,H),(12,34,24),(4,8,6),(40,140,90)); d=ImageDraw.Draw(im)
    bars(d,60,50,W-120,[("هوش مصنوعی کارم رو سریع‌تر کرده",63,GR,"63%")],rowh=140,maxv=100)
    im.save(path,quality=95)
def bad(path):
    W,H=1000,440; im=base((W,H),(40,12,12),(8,4,4),(150,40,40)); d=ImageDraw.Draw(im)
    bars(d,60,40,W-120,[("حالا ازم کار بیشتری می‌خوان",52,RED,"52%"),("حجم کارم خیلی زیاد شده",62,AMB,"62%")],rowh=150,maxv=100)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); good("d1.png"); bad("d2.png"); print("art ok")
