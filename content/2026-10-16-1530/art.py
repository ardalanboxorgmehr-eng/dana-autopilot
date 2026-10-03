import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(50,80,200)
def menu(d,box,items,hl=0):
    x0,y0,x1,y1=box
    panel(d,box,r=24,fill=(22,26,40),outline=(90,110,170),w=3)
    for i,(n,c) in enumerate(items):
        y=y0+20+i*80
        if i==hl: d.rounded_rectangle([x0+14,y,x1-14,y+66],radius=16,fill=(40,56,100))
        d.rounded_rectangle([x0+30,y+15,x0+66,y+51],radius=10,fill=c)
        d.text((x0+86,y+33),n,font=F(POPB,30),fill=WHITE,anchor="lm")
def cover(path):
    W,H=1080,900; im=base((W,H),(14,20,52),(4,6,14),T)
    im=addglow(im,lambda d:(d.ellipse([140,80,940,760],fill=(90,130,255)),),130,0.45)
    d=ImageDraw.Draw(im)
    menu(d,[200,110,880,450],[("/study-coach",GR),("/email-polish",AMB),("/cv-check",(240,120,170)),("/fact-check",BLUE)],hl=0)
    # prompt bar
    panel(d,[120,500,960,610],r=55,fill=(240,242,248),outline=(240,242,248),w=2)
    d.text((175,555),"/",font=F(POPB,56),fill=(70,100,220),anchor="mm")
    d.text((215,555),"study-coach  + my notes.pdf",font=F(POP,34),fill=(40,44,56),anchor="lm")
    d.ellipse([870,520,940,590],fill=(70,100,220))
    d.polygon([(893,532),(925,555),(893,578)],fill=WHITE)
    im.save(path,quality=95)
def slash(path):
    W,H=1000,460; im=base((W,H),(14,20,52),(4,6,14),T); d=ImageDraw.Draw(im)
    menu(d,[160,30,840,330],[("/study-coach",GR),("/email-polish",AMB),("/cv-check",(240,120,170))],hl=1)
    panel(d,[100,355,900,440],r=42,fill=(240,242,248),outline=(240,242,248),w=2)
    d.text((150,397),"/",font=F(POPB,48),fill=(70,100,220),anchor="mm")
    d.rounded_rectangle([172,375,176,420],radius=2,fill=(40,44,56))
    im.save(path,quality=95)
def steps(path):
    W,H=1000,300; im=base((W,H),(14,20,52),(4,6,14),T); d=ImageDraw.Draw(im)
    st=["Menu","Settings","Skills","Add skill"]
    xs=[115,370,625,875]
    for i,(t,x) in enumerate(zip(st,xs)):
        c=GR if i==3 else (90,110,170)
        panel(d,[x-100,100,x+100,200],r=24,fill=(22,26,40),outline=c,w=4)
        d.text((x,150),t,font=fiten(d,t,POPB,170,32),fill=WHITE,anchor="mm")
        if i<3:
            a=x+108; b=xs[i+1]-108
            d.polygon([(a,141),(b-18,141),(b-18,128),(b,150),(b-18,172),(b-18,159),(a,159)],fill=WHITE)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); slash("d1.png"); steps("d2.png"); print("art ok")
