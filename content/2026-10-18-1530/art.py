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
T=(170,70,50)
def court(d,cx,base,w):
    d.polygon([(cx-w/2-20,base-w*0.78),(cx,base-w*1.02),(cx+w/2+20,base-w*0.78)],fill=(200,190,170))
    d.rectangle([cx-w/2-10,base-w*0.78,cx+w/2+10,base-w*0.72],fill=(180,170,150))
    for i in range(5):
        x=cx-w/2+10+i*(w-20)/4; d.rectangle([x-12,base-w*0.7,x+12,base-w*0.08],fill=(220,212,196))
    d.rectangle([cx-w/2-20,base-w*0.08,cx+w/2+20,base],fill=(180,170,150))
def casedoc(d,x,y,w,h,n):
    panel(d,[x,y,x+w,y+h],r=14,fill=(236,232,224),outline=(160,150,140),w=3)
    d.text((x+20,y+18),f"CASE {n}",font=F(POPB,24),fill=(60,50,40))
    for i in range(3): d.rounded_rectangle([x+20,y+62+i*26,x+w-20-(i%2)*40,y+74+i*26],radius=5,fill=(190,182,170))
def cover(path):
    W,H=1080,900; im=base((W,H),(44,20,14),(8,4,4),T)
    im=addglow(im,lambda d:(d.ellipse([60,150,520,700],fill=(255,160,80)),d.ellipse([560,150,1040,700],fill=(255,70,60))),120,0.42)
    d=ImageDraw.Draw(im)
    court(d,280,620,360)
    d.text((280,700),"$5,000",font=F(POPB,84),fill=AMB,anchor="mm")
    for k in range(6):
        x=580+(k%2)*220; y=110+(k//2)*190
        casedoc(d,x,y,200,165,k+1)
        stamp(d,x+100,y+120,"FAKE",F(POPB,32),RED,5)
    im.save(path,quality=95)
def six(path):
    W,H=1000,480; im=base((W,H),(44,20,14),(8,4,4),T); d=ImageDraw.Draw(im)
    for k in range(6):
        x=60+(k%3)*300; y=40+(k//3)*215
        casedoc(d,x,y,280,190,k+1); stamp(d,x+140,y+145,"DOES NOT EXIST",F(POPB,26),RED,4)
    im.save(path,quality=95)
def chat(path):
    W,H=1000,500; im=base((W,H),(44,20,14),(8,4,4),T); d=ImageDraw.Draw(im)
    bubble(d,[420,40,940,140],"Is Varghese a real case?",F(POP,34),(60,80,130))
    bubble(d,[60,175,800,455],"Upon double-checking, I found that the case ... does indeed exist and can be found on legal research databases such as Westlaw and LexisNexis.",F(POP,32),(48,40,40))
    stamp(d,860,390,"FALSE",F(POPB,40),RED,6)
    im.save(path,quality=95)
def fine(path):
    W,H=1000,360; im=base((W,H),(44,20,14),(8,4,4),T); d=ImageDraw.Draw(im)
    # gavel: tilted head, diagonal handle, sound block
    cx,cy=230,140; a=math.radians(-28); ca,sa=math.cos(a),math.sin(a)
    def rot(px,py): return (cx+px*ca-py*sa, cy+px*sa+py*ca)
    d.line([rot(0,0),rot(130,170)],fill=(140,96,60),width=24)
    d.polygon([rot(-110,-40),rot(110,-40),rot(110,40),rot(-110,40)],fill=(176,124,82))
    for e in (-110,110): d.polygon([rot(e-14,-50),rot(e+14,-50),rot(e+14,50),rot(e-14,50)],fill=(150,104,66))
    d.rounded_rectangle([70,280,300,320],radius=12,fill=(120,84,56)); d.rounded_rectangle([100,255,270,285],radius=10,fill=(150,104,66))
    d.text((690,140),"$5,000",font=F(POPB,110),fill=AMB,anchor="mm")
    d.text((690,240),"+ letters to the judges",font=F(POP,34),fill=WHITE,anchor="mm")
    d.text((690,290),"named in the fake opinions",font=F(POP,34),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); six("d1.png"); chat("d2.png"); fine("d3.png"); print("art ok")
