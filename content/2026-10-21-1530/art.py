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
T=(120,70,180)
def cv(d,x,y,w,h):
    panel(d,[x,y,x+w,y+h],r=20,fill=(240,240,246),outline=(170,170,190),w=3)
    d.ellipse([x+30,y+30,x+120,y+120],fill=(190,192,210))
    d.rounded_rectangle([x+140,y+45,x+w-40,y+70],radius=8,fill=(120,124,150)); d.rounded_rectangle([x+140,y+85,x+w-120,y+102],radius=8,fill=(190,192,210))
    for i in range(7):
        yy=y+160+i*52; d.rounded_rectangle([x+30,yy,x+w-30-(i%3)*60,yy+18],radius=8,fill=(195,197,212))
        if i in (1,4): d.line([(x+40,yy+30),(x+w-140,yy+30)],fill=RED,width=5)
        if i in (2,5): d.line([(x+40,yy+30),(x+w-160,yy+30)],fill=GR,width=5)
def cover(path):
    W,H=1080,900; im=base((W,H),(30,18,50),(6,4,10),T)
    im=addglow(im,lambda d:(d.ellipse([60,100,560,760],fill=(170,120,255)),d.ellipse([600,200,1040,700],fill=(255,200,80))),120,0.42)
    d=ImageDraw.Draw(im)
    cv(d,90,90,440,560)
    d.text((310,700),"Fewer errors",font=F(POPB,40),fill=WHITE,anchor="mm")
    arrow(d,(560,400),(660,400),WHITE,10,30)
    panel(d,[680,190,1010,560],r=32,fill=(26,22,40),outline=AMB,w=5)
    d.text((845,320),"+8%",font=F(POPB,120),fill=AMB,anchor="mm")
    d.text((845,430),"more likely",font=F(POP,34),fill=WHITE,anchor="mm")
    d.text((845,475),"to be hired",font=F(POP,34),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def result(path):
    W,H=1000,340; im=base((W,H),(30,18,50),(6,4,10),T); d=ImageDraw.Draw(im)
    bars(d,60,30,W-120,[("بدون ابزار ویرایش",100,(120,126,140),"Baseline"),("با ابزار ویرایش",108,AMB,"+8%")],rowh=140,maxv=110)
    im.save(path,quality=95)
def rewrite(path):
    W,H=1000,480; im=base((W,H),(30,18,50),(6,4,10),T); d=ImageDraw.Draw(im)
    panel(d,[60,30,W-60,150],r=24,fill=(40,20,24),outline=RED,w=4)
    d.text((90,62),"BEFORE",font=F(POPB,26),fill=RED,anchor="lm")
    d.text((90,110),"Responsible for social media.",font=F(POP,34),fill=WHITE,anchor="lm")
    arrow(d,(W/2,160),(W/2,225),WHITE,8,26)
    panel(d,[60,235,W-60,450],r=24,fill=(16,36,30),outline=GR,w=4)
    d.text((90,268),"AFTER",font=F(POPB,26),fill=GR,anchor="lm")
    text_en(d,90,300,"Grew a small shop's Instagram from [X] to [Y] followers in 6 months by posting 3 short videos a week.",F(POP,32),WHITE,W-180)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); result("d1.png"); rewrite("d2.png"); print("art ok")
