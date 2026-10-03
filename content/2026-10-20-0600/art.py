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
T=(30,140,130)
def cover(path):
    W,H=1080,900; im=base((W,H),(10,36,36),(4,8,8),T)
    im=addglow(im,lambda d:(d.ellipse([520,80,1060,780],fill=(60,220,190)),d.ellipse([40,250,480,700],fill=(255,200,80))),120,0.42)
    d=ImageDraw.Draw(im)
    x0,y0,x1,y1=phone(d,600,80,380,740)
    d.text(((x0+x1)/2,y0+40),"Examiner mode",font=F(POPB,32),fill=WHITE,anchor="mm")
    d.ellipse([(x0+x1)/2-110,y0+110,(x0+x1)/2+110,y0+330],fill=(40,170,150))
    d.ellipse([(x0+x1)/2-80,y0+140,(x0+x1)/2+80,y0+300],fill=(90,220,200))
    waveform(d,x0+20,y0+380,x1-x0-40,110,GR,n=28,seed=5)
    d.rounded_rectangle([x0+20,y0+530,x1-20,y0+610],radius=20,fill=(30,40,40))
    d.text(((x0+x1)/2,y0+570),"Part 2 · prep 1:00",font=F(POPB,30),fill=AMB,anchor="mm")
    # speech bubbles left
    bubble(d,[60,170,520,330],"Describe a place you like to visit.",F(POP,34),(30,70,64))
    bubble(d,[60,380,520,540],"Well, one place I really love is...",F(POP,34),(70,58,30))
    d.ellipse([60,590,150,680],fill=AMB); d.rounded_rectangle([92,605,118,650],radius=13,fill=(20,24,24)); d.line([(105,650),(105,668)],fill=(20,24,24),width=5)
    d.text((175,635),"Speak, don't type",font=F(POPB,36),fill=WHITE,anchor="lm")
    im.save(path,quality=95)
def parts(path):
    W,H=1000,400; im=base((W,H),(10,36,36),(4,8,8),T); d=ImageDraw.Draw(im)
    d.text((60,45),"IELTS Speaking · 11-14 minutes",font=F(POPB,36),fill=WHITE,anchor="lm")
    segs=[("Part 1","Interview","4-5 min",BLUE,4.5),("Part 2","Long turn","3-4 min",AMB,3.5),("Part 3","Discussion","4-5 min",GR,4.5)]
    tot=sum(s[4] for s in segs); x=60; w=W-120
    for i,(a,b,c,col,v) in enumerate(segs):
        sw=w*v/tot-10
        d.rounded_rectangle([x,110,x+sw,330],radius=24,fill=col)
        d.text((x+sw/2,165),a,font=F(POPB,40),fill=(12,12,16),anchor="mm")
        d.text((x+sw/2,225),b,font=F(POP,30),fill=(12,12,16),anchor="mm")
        d.text((x+sw/2,280),c,font=F(POPB,30),fill=(12,12,16),anchor="mm")
        x+=sw+10
    im.save(path,quality=95)
def criteria(path):
    W,H=1000,420; im=base((W,H),(10,36,36),(4,8,8),T); d=ImageDraw.Draw(im)
    items=[("Fluency &","Coherence",BLUE),("Lexical","Resource",GR),("Grammatical","Range & Accuracy",AMB),("Pronun-","ciation",(255,120,90))]
    items=[("Fluency and Coherence",BLUE),("Lexical Resource",GR),("Grammatical Range and Accuracy",AMB),("Pronunciation",(255,120,90))]
    for i,(t,c) in enumerate(items):
        y=40+i*92
        d.rounded_rectangle([60,y,W-60,y+76],radius=20,fill=(20,34,34),outline=c,width=4)
        d.ellipse([84,y+16,128,y+60],fill=c); d.text((106,y+38),str(i+1),font=F(POPB,28),fill=(12,12,16),anchor="mm")
        d.text((150,y+38),t,font=F(POPB,34),fill=WHITE,anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); parts("d1.png"); criteria("d2.png"); print("art ok")
