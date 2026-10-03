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
T=(40,120,210)
PARTS=[("ROLE",(120,110,255),"You are an IELTS tutor."),("TASK",GR,"Make a 4-week reading plan."),("CONTEXT",AMB,"I'm band 6 and have 1 hour a day."),("FORMAT",(255,120,90),"A table: week, task, minutes.")]
def cover(path):
    W,H=1080,900; im=base((W,H),(12,26,50),(4,6,12),T)
    im=addglow(im,lambda d:d.ellipse([560,160,1060,760],fill=(80,150,255)),120,0.5)
    d=ImageDraw.Draw(im)
    for i,(lab,col,_) in enumerate(PARTS):
        y=110+i*160
        d.rounded_rectangle([70,y,470,y+130],radius=30,fill=(20,26,40),outline=col,width=5)
        d.ellipse([95,y+35,155,y+95],fill=col); d.text((125,y+65),str(i+1),font=F(POPB,36),fill=(12,12,16),anchor="mm")
        d.text((180,y+65),lab,font=F(POPB,48),fill=WHITE,anchor="lm")
    # bracket arrows to output
    for i in range(4): d.line([(470,175+i*160),(530,175+i*160)],fill=GREY,width=6)
    d.line([(530,175),(530,655)],fill=GREY,width=6)
    arrow(d,(530,415),(620,415),WHITE,8,28)
    panel(d,[630,200,1020,630],r=30,fill=(20,26,40),outline=BLUE,w=5)
    d.text((660,230),"Better answer",font=F(POPB,34),fill=WHITE)
    for r in range(4):
        y=300+r*75
        for c in range(3):
            x=660+c*118; d.rounded_rectangle([x,y,x+104,y+56],radius=10,fill=(40,60,100) if r==0 else (34,40,56))
    im.save(path,quality=95)
def assembled(path):
    W,H=1000,560; im=base((W,H),(12,26,50),(4,6,12),T); d=ImageDraw.Draw(im)
    d.text((60,40),"The table you get",font=F(POPB,34),fill=WHITE)
    hdr=["Week","Task","Minutes"]; rows=[["1","Skimming drills","60"],["2","Matching headings","60"],["3","True/False/Not Given","60"],["4","Full timed tests","60"]]
    xs=[60,250,780,940]; y=110
    d.rounded_rectangle([60,y,940,y+70],radius=14,fill=(255,120,90))
    for k,h in enumerate(hdr): d.text((xs[k]+24,y+35),h,font=F(POPB,30),fill=(12,12,16),anchor="lm")
    for r,row in enumerate(rows):
        yy=y+85+r*88; d.rounded_rectangle([60,yy,940,yy+76],radius=14,fill=(30,36,52))
        for k,v in enumerate(row): d.text((xs[k]+24,yy+38),v,font=F(POP,30),fill=WHITE,anchor="lm")
    im.save(path,quality=95)
def beforeafter(path):
    W,H=1000,600; im=base((W,H),(12,26,50),(4,6,12),T); d=ImageDraw.Draw(im)
    panel(d,[60,30,W-60,140],r=24,fill=(40,20,24),outline=RED,w=4)
    d.text((90,85),"BEFORE",font=F(POPB,28),fill=RED,anchor="lm")
    d.text((260,85),"“Write a study plan.”",font=F(POP,34),fill=WHITE,anchor="lm")
    arrow(d,(W/2,150),(W/2,215),WHITE,8,26)
    panel(d,[60,225,W-60,H-30],r=24,fill=(16,36,30),outline=GR,w=4)
    d.text((90,262),"AFTER",font=F(POPB,28),fill=GR,anchor="lm")
    y=305; f=F(POP,30)
    for lab,col,t in PARTS:
        d.rounded_rectangle([90,y+4,250,y+46],radius=12,fill=col)
        d.text((170,y+25),lab,font=F(POPB,22),fill=(12,12,16),anchor="mm")
        d.text((272,y+25),t,font=f,fill=WHITE,anchor="lm"); y+=62
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); assembled("d1.png"); beforeafter("d2.png"); print("art ok")
