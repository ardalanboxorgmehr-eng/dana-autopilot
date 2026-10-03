import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
def arrow(d,p0,p1,col=WHITE,w=8,hs=26):
    x0,y0=p0; x1,y1=p1; L=math.hypot(x1-x0,y1-y0); ux,uy=(x1-x0)/L,(y1-y0)/L
    bx,by=x1-ux*hs,y1-uy*hs; d.line([(x0,y0),(bx,by)],fill=col,width=w)
    px,py=-uy,ux; d.polygon([(x1,y1),(bx+px*hs*0.6,by+py*hs*0.6),(bx-px*hs*0.6,by-py*hs*0.6)],fill=col)
def check(d,cx,cy,s,col=GR,w=8):
    d.line([(cx-s*0.5,cy),(cx-s*0.15,cy+s*0.38),(cx+s*0.55,cy-s*0.42)],fill=col,width=w,joint="curve")
def cross(d,cx,cy,s,col=RED,w=8):
    d.line([(cx-s/2,cy-s/2),(cx+s/2,cy+s/2)],fill=col,width=w); d.line([(cx-s/2,cy+s/2),(cx+s/2,cy-s/2)],fill=col,width=w)
def wrap_en(d,t,f,maxw):
    out=[]
    for para in t.split("\n"):
        cur=""
        for w in para.split(" "):
            tt=(cur+" "+w).strip()
            if d.textlength(tt,font=f)<=maxw or not cur: cur=tt
            else: out.append(cur); cur=w
        out.append(cur)
    return out
def text_en(d,x,y,t,f,fill,maxw,lh=1.35):
    for i,l in enumerate(wrap_en(d,t,f,maxw)): d.text((x,y+i*f.size*lh),l,font=f,fill=fill)
    return y+len(wrap_en(d,t,f,maxw))*f.size*lh
def bubble(d,box,t,f,col=(38,44,58),fill=WHITE):
    d.rounded_rectangle(box,radius=26,fill=col)
    text_en(d,box[0]+26,box[1]+20,t,f,fill,box[2]-box[0]-52)
def stamp(d,cx,cy,t,f,col=RED,w=5):
    tw=d.textlength(t,font=f); d.rounded_rectangle([cx-tw/2-18,cy-f.size*0.75,cx+tw/2+18,cy+f.size*0.75],radius=10,outline=col,width=w)
    d.text((cx,cy),t,font=f,fill=col,anchor="mm")
T=(40,110,190)
def tile(d,x,y,w,h,label,fake,col):
    d.rounded_rectangle([x,y,x+w,y+h],radius=20,fill=(28,34,50),outline=RED if fake else GR,width=5)
    person(d,x+w/2,y+h*0.52,h*0.36,col,tuple(min(255,c+30) for c in col))
    d.rounded_rectangle([x+12,y+h-50,x+12+d.textlength(label,font=F(POPB,24))+24,y+h-14],radius=10,fill=(10,12,18))
    d.text((x+24,y+h-32),label,font=F(POPB,24),fill=WHITE,anchor="lm")
    if fake:
        f=F(POPB,22); t="DEEPFAKE"; tw=d.textlength(t,font=f)
        d.rounded_rectangle([x+w-tw-38,y+12,x+w-12,y+46],radius=10,fill=RED); d.text((x+w-25-tw/2,y+29),t,font=f,fill=WHITE,anchor="mm")
def grid(d,x0,y0,w,h):
    tw,th=(w-20)/2,(h-20)/2
    tile(d,x0,y0,tw,th,"CFO",True,(90,110,160))
    tile(d,x0+tw+20,y0,tw,th,"Colleague",True,(120,96,140))
    tile(d,x0,y0+th+20,tw,th,"Colleague",True,(80,130,120))
    tile(d,x0+tw+20,y0+th+20,tw,th,"You",False,(140,120,90))
def cover(path):
    W,H=1080,900; im=base((W,H),(12,24,48),(4,6,12),T)
    im=addglow(im,lambda d:(d.ellipse([60,100,760,760],fill=(70,140,255)),d.ellipse([700,300,1060,760],fill=(255,190,60))),120,0.42)
    d=ImageDraw.Draw(im)
    panel(d,[50,70,720,770],r=34,fill=(16,20,32),outline=(80,100,140),w=4)
    grid(d,80,100,610,560)
    for i,c in enumerate([RED,(70,76,92),(70,76,92)]):
        d.ellipse([260+i*80,690,320+i*80,750],fill=c)
    d.rounded_rectangle([279,712,301,728],radius=4,fill=WHITE)
    d.text((900,330),"US$25m",font=F(POPB,68),fill=AMB,anchor="mm")
    d.text((900,410),"HK$200m",font=F(POPB,44),fill=WHITE,anchor="mm")
    d.text((900,470),"one video call",font=F(POP,34),fill=GREY,anchor="mm")
    d.text((900,515),"15 transfers",font=F(POP,34),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def call(path):
    W,H=1000,560; im=base((W,H),(12,24,48),(4,6,12),T); d=ImageDraw.Draw(im)
    grid(d,140,30,720,500)
    im.save(path,quality=95)
def money(path):
    W,H=1000,520; im=base((W,H),(12,24,48),(4,6,12),T); d=ImageDraw.Draw(im)
    panel(d,[50,170,300,350],r=26,fill=(24,30,46),outline=BLUE,w=4)
    d.text((175,235),"HK office",font=F(POPB,34),fill=WHITE,anchor="mm"); d.text((175,290),"account",font=F(POP,30),fill=GREY,anchor="mm")
    for i in range(5):
        y=40+i*92
        panel(d,[640,y,950,y+76],r=18,fill=(40,26,30),outline=RED,w=3)
        d.text((795,y+38),f"Account {i+1}",font=F(POPB,30),fill=WHITE,anchor="mm")
        arrow(d,(305,260),(632,y+38),AMB,5,20)
    d.text((175,410),"15 transfers",font=F(POPB,36),fill=AMB,anchor="mm")
    d.text((175,460),"HK$200m",font=F(POPB,36),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); call("d1.png"); money("d2.png"); print("art ok")
