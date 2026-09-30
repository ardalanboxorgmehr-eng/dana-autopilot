import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(120,60,200)
def cover(path):
    W,H=1080,900; im=base((W,H),(26,16,44),(5,4,10),T)
    im=addglow(im,lambda d:d.ellipse([140,200,940,760],fill=(170,90,255)),110,0.55)
    d=ImageDraw.Draw(im)
    # short clip
    panel(d,[70,330,380,570],r=34,fill=(26,22,40),outline=(140,100,220))
    waveform(d,100,380,250,120,(200,160,255),n=14,seed=2)
    d.text((225,540),"0:10",font=F(POPB,40),fill=AMB,anchor="ms")
    # arrow
    d.polygon([(535,450),(475,410),(475,430),(410,430),(410,470),(475,470),(475,490)],fill=WHITE)
    # big voice
    panel(d,[560,170,1010,730],r=40,fill=(22,18,34),outline=(170,110,255),w=4)
    waveform(d,590,230,390,150,(190,140,255),n=26,seed=5)
    langs=["English","Español","Deutsch","Français","Türkçe","Italiano","Polski"]
    x,y=590,420
    for i,l in enumerate(langs):
        f=F(POPB,28); tw=d.textlength(l,font=f)+36
        if x+tw>985: x=590; y+=62
        d.rounded_rectangle([x,y,x+tw,y+48],radius=24,fill=(48,36,80))
        d.text((x+tw/2,y+24),l,font=f,fill=WHITE,anchor="mm")
        x+=tw+12
    d.text((785,700),"90+ languages",font=F(POPB,34),fill=AMB,anchor="ms")
    im.save(path,quality=95)
def clip(path):
    W,H=1000,420; im=base((W,H),(26,16,44),(5,4,10),T); d=ImageDraw.Draw(im)
    panel(d,[40,60,W-40,H-60],r=34,fill=(24,20,36),outline=(120,90,200))
    waveform(d,90,110,W-180,140,(190,140,255),n=40,seed=9)
    d.rounded_rectangle([90,290,W-90,306],radius=8,fill=(50,44,70))
    d.rounded_rectangle([90,290,90+(W-180)*0.35,306],radius=8,fill=AMB)
    d.text((90,340),"0:10",font=F(POPB,30),fill=AMB); d.text((W-90,340),"voice sample",font=F(POP,28),fill=GREY,anchor="ra")
    im.save(path,quality=95)
def tags(path):
    W,H=1000,460; im=base((W,H),(26,16,44),(5,4,10),T); d=ImageDraw.Draw(im)
    panel(d,[40,40,W-40,H-40],r=34,fill=(24,20,36),outline=(120,90,200))
    f=F(POP,36)
    lines=[("Hello! ",None),("[laughs]",AMB)],[("I can't believe it... ",None),("[angrily]",RED)],[("Call me back. ",None),("[whispers]",BLUE)]
    y=90
    for ln in lines:
        x=90
        for t,c in ln:
            d.text((x,y),t,font=f,fill=c or WHITE); x+=d.textlength(t,font=f)
        y+=110
    im.save(path,quality=95)
def call(path):
    W,H=1000,560; im=base((W,H),(40,12,16),(6,4,6),(150,30,40)); d=ImageDraw.Draw(im)
    x0,y0,x1,y1=phone(d,330,20,340,520)
    person(d,500,200,90,(120,110,130),(160,150,170))
    d.text((500,300),"Unknown number",font=F(POPB,28),fill=WHITE,anchor="ms")
    d.text((500,340),"\"It's me... I need money now\"",font=F(POP,20),fill=AMB,anchor="ms")
    d.ellipse([380,410,450,480],fill=RED); d.ellipse([550,410,620,480],fill=GR)
    d.ellipse([730,120,850,240],fill=RED); d.text((790,178),"!",font=F(POPB,84),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); clip("d1.png"); tags("d2.png"); call("d3.png"); print("art ok")
