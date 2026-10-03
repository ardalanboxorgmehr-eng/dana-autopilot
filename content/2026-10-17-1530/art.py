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
T=(110,60,190)
def doc(d,x,y,w,h):
    panel(d,[x,y,x+w,y+h],r=20,fill=(236,236,244),outline=(180,180,200),w=3)
    for i in range(7): d.rounded_rectangle([x+30,y+50+i*42,x+w-30-(i%3)*50,y+66+i*42],radius=7,fill=(190,192,206))
def cover(path):
    W,H=1080,900; im=base((W,H),(30,16,50),(6,4,10),T)
    im=addglow(im,lambda d:(d.ellipse([60,120,520,700],fill=(140,90,255)),d.ellipse([600,200,1040,700],fill=(255,80,80))),120,0.45)
    d=ImageDraw.Draw(im)
    doc(d,90,150,360,420)
    # magnifier
    d.ellipse([260,330,470,540],outline=WHITE,width=14); d.line([(445,515),(540,610)],fill=WHITE,width=26)
    d.text((365,435),"?",font=F(POPB,110),fill=AMB,anchor="mm")
    d.text((90,80),"AI CLASSIFIER",font=F(POPB,40),fill=WHITE)
    stamp(d,300,680,"WITHDRAWN · JUL 2023",F(POPB,40),RED,6)
    # stats
    panel(d,[600,140,1000,370],r=30,fill=(26,22,40),outline=(120,100,200))
    d.text((800,250),"26%",font=F(POPB,110),fill=AMB,anchor="mm")
    d.text((800,335),"of AI text caught",font=F(POP,32),fill=GREY,anchor="mm")
    panel(d,[600,410,1000,640],r=30,fill=(26,22,40),outline=(200,80,80))
    d.text((800,520),"9%",font=F(POPB,110),fill=RED,anchor="mm")
    d.text((800,605),"human text called AI",font=F(POP,32),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def rates(path):
    W,H=1000,330; im=base((W,H),(30,16,50),(6,4,10),T); d=ImageDraw.Draw(im)
    bars(d,60,30,W-120,[("متن AI که درست تشخیص داد",26,AMB,"26%"),("متن آدم که اشتباهی AI دونست",9,RED,"9%")],rowh=140,maxv=100)
    im.save(path,quality=95)
def toefl(path):
    W,H=1000,520; im=base((W,H),(40,14,20),(8,4,6),(150,40,60)); d=ImageDraw.Draw(im)
    d.text((W/2,50),"91 TOEFL essays by non-native writers",font=F(POPB,34),fill=WHITE,anchor="mm")
    cols=13; r=19; gx=58; gy=50; x0=W/2-(cols-1)*gx/2; y0=110
    for i in range(91):
        cx=x0+(i%cols)*gx; cy=y0+(i//cols)*gy
        d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=RED if i<89 else GR)
    y=y0+7*gy+10
    d.ellipse([170,y-14,198,y+14],fill=RED); d.text((212,y),"89 flagged as AI by at least 1 of 7 detectors",font=F(POP,28),fill=WHITE,anchor="lm")
    y+=0
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); rates("d1.png"); toefl("d2.png"); print("art ok")
