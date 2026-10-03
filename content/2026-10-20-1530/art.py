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
T=(170,120,30)
def eye(d,cx,cy,s,col=WHITE):
    d.chord([cx-s,cy-s*0.62,cx+s,cy+s*0.62],0,360,fill=col)
    d.ellipse([cx-s*0.36,cy-s*0.36,cx+s*0.36,cy+s*0.36],fill=(30,40,70)); d.ellipse([cx-s*0.14,cy-s*0.14,cx+s*0.14,cy+s*0.14],fill=(10,10,14))
def cover(path):
    W,H=1080,900; im=base((W,H),(44,32,10),(8,6,4),T)
    im=addglow(im,lambda d:(d.ellipse([80,120,700,760],fill=(255,190,80)),d.ellipse([700,120,1060,500],fill=(255,80,80))),120,0.42)
    d=ImageDraw.Draw(im)
    panel(d,[70,90,700,760],r=34,fill=(22,22,28),outline=(110,100,80),w=4)
    d.text((110,150),"New chat",font=F(POPB,36),fill=WHITE,anchor="lm")
    rows=[("Password:","••••••••"),("Card no.:","**** **** **** ****"),("Passport:","X•••••••"),("Home address:","•••••• •••")]
    for i,(a,b) in enumerate(rows):
        y=220+i*120
        d.rounded_rectangle([110,y,660,y+92],radius=22,fill=(60,40,30))
        d.text((140,y+46),a,font=F(POPB,32),fill=WHITE,anchor="lm"); d.text((640,y+46),b,font=F(POPB,32),fill=AMB,anchor="rm")
    # no sign over the list
    d.ellipse([560,610,700,750],outline=RED,width=14); d.line([(585,725),(675,635)],fill=RED,width=14)
    # reviewer eye
    panel(d,[760,160,1010,400],r=30,fill=(30,24,28),outline=RED,w=4)
    eye(d,885,250,90)
    d.text((885,355),"Human review",font=F(POPB,28),fill=WHITE,anchor="mm")
    d.text((885,470),"up to",font=F(POP,32),fill=GREY,anchor="mm")
    d.text((885,540),"3 years",font=F(POPB,64),fill=AMB,anchor="mm")
    d.text((885,600),"for reviewed chats",font=F(POP,28),fill=GREY,anchor="mm")
    d.text((885,645),"(Gemini)",font=F(POP,28),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def retention(path):
    W,H=1000,470; im=base((W,H),(44,32,10),(8,6,4),T); d=ImageDraw.Draw(im)
    rows=[("Gemini · Keep Activity off","kept 72 hours",GR),("ChatGPT · Temporary Chat","kept up to 30 days",AMB),("Gemini · chats seen by reviewers","kept up to 3 years",RED)]
    for i,(a,b,c) in enumerate(rows):
        y=40+i*140
        panel(d,[60,y,W-60,y+118],r=24,fill=(26,22,20),outline=c,w=4)
        d.text((95,y+40),a,font=F(POPB,32),fill=WHITE,anchor="lm"); d.text((95,y+84),b,font=F(POP,30),fill=c,anchor="lm")
    im.save(path,quality=95)
def toggle(path):
    W,H=1000,380; im=base((W,H),(44,32,10),(8,6,4),T); d=ImageDraw.Draw(im)
    panel(d,[60,30,W-60,H-30],r=28,fill=(24,24,30),outline=(90,90,100))
    d.text((100,80),"Settings  ›  Data controls",font=F(POPB,32),fill=GREY,anchor="lm")
    d.line([(100,125),(W-100,125)],fill=(60,60,70),width=2)
    d.text((100,190),"Improve the model",font=F(POPB,38),fill=WHITE,anchor="lm")
    d.text((100,240),"for everyone",font=F(POPB,38),fill=WHITE,anchor="lm")
    # toggle off
    d.rounded_rectangle([720,180,860,250],radius=35,fill=(70,70,80)); d.ellipse([726,186,784,244],fill=WHITE)
    d.text((790,290),"OFF",font=F(POPB,30),fill=GR,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); retention("d1.png"); toggle("d2.png"); print("art ok")
