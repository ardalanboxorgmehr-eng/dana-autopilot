import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(150,60,90)
PK=(240,110,150)
def form(d,x,y,w,h,col):
    panel(d,[x,y,x+w,y+h],r=20,fill=(236,238,244),outline=col,w=4)
    for i in range(4):
        yy=y+40+i*(h-60)/4
        d.ellipse([x+24,yy,x+50,yy+26],outline=(120,126,140),width=3)
        if i in (1,3): d.ellipse([x+30,yy+6,x+44,yy+20],fill=col)
        d.rounded_rectangle([x+66,yy+6,x+w-30-(i%2)*50,yy+20],radius=6,fill=(190,196,210))
def cover(path):
    W,H=1080,900; im=base((W,H),(40,14,26),(8,4,6),T)
    im=addglow(im,lambda d:(d.ellipse([60,120,540,720],fill=(120,170,255)),d.ellipse([560,160,1040,720],fill=(255,110,150))),120,0.45)
    d=ImageDraw.Draw(im)
    # left: humans
    panel(d,[70,110,500,640],r=36,fill=(18,22,34),outline=BLUE,w=4)
    d.text((285,160),"Real people",font=F(POPB,38),fill=BLUE,anchor="mm")
    for i in range(3):
        for j in range(3):
            person(d,150+j*135,275+i*135,58,(90,130,200),(200,170,140))
    # right: AI personas
    panel(d,[580,110,1010,640],r=36,fill=(30,16,24),outline=PK,w=4)
    d.text((795,160),"AI personas",font=F(POPB,38),fill=PK,anchor="mm")
    for i in range(3):
        for j in range(3):
            cx=660+j*135; cy=275+i*135
            d.rounded_rectangle([cx-40,cy-55,cx+40,cy+5],radius=14,fill=(200,110,150))
            d.ellipse([cx-24,cy-38,cx-10,cy-24],fill=(30,16,24)); d.ellipse([cx+10,cy-38,cx+24,cy-24],fill=(30,16,24))
            d.rounded_rectangle([cx-44,cy+12,cx+44,cy+62],radius=18,fill=(200,110,150))
    d.rounded_rectangle([512,350,568,362],radius=6,fill=WHITE); d.rounded_rectangle([512,384,568,396],radius=6,fill=WHITE)
    d.line([(555,330),(525,416)],fill=WHITE,width=10)
    im.save(path,quality=95)
def error(path):
    W,H=1000,420; im=base((W,H),(40,14,26),(8,4,6),T); d=ImageDraw.Draw(im)
    items=[("12","avg. points off"),("~300","questions"),("28%","questions off by 15+")]
    for i,(n,t) in enumerate(items):
        x=40+i*315
        panel(d,[x,60,x+290,360],r=26,fill=(24,16,22),outline=PK if i!=1 else GREY,w=4)
        d.text((x+145,180),n,font=F(POPB,80),fill=WHITE,anchor="mm")
        d.text((x+145,290),t,font=fiten(d,t,POPB,250,28),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def knowledge(path):
    W,H=1000,400; im=base((W,H),(40,14,26),(8,4,6),T); d=ImageDraw.Draw(im)
    bars(d,60,30,W-120,[("آدم‌های واقعی",52,BLUE,"52%"),("پرسوناهای هوش مصنوعی",98,PK,"98%")],rowh=150,maxv=100)
    fa(d,(W-60,340),"جواب درست به سؤال متمم اول قانون اساسی آمریکا",F(VS,28),GREY)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); error("d1.png"); knowledge("d2.png"); print("art ok")
