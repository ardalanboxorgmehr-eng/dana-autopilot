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
T=(80,80,210)
def cover(path):
    W,H=1080,900; im=base((W,H),(20,20,54),(4,4,12),T)
    im=addglow(im,lambda d:d.ellipse([200,250,900,800],fill=(120,110,255)),130,0.45)
    d=ImageDraw.Draw(im)
    panel(d,[70,90,1010,220],r=30,fill=(22,24,44),outline=(120,120,220),w=4)
    d.text((110,155),"I drink my coffee with",font=F(POP,52),fill=WHITE,anchor="lm")
    tw=110+d.textlength("I drink my coffee with",font=F(POP,52))+22
    d.rounded_rectangle([tw,120,tw+150,190],radius=14,outline=AMB,width=4)
    d.text((tw+75,155),"?",font=F(POPB,52),fill=AMB,anchor="mm")
    d.text((90,275),"Next-word odds (illustration)",font=F(POPB,32),fill=GREY)
    items=[("milk",41,GR),("sugar",33,BLUE),("cream",18,(170,130,255)),("salt",1,RED)]
    for i,(w,p,c) in enumerate(items):
        y=330+i*110
        d.text((90,y+40),w,font=F(POPB,44),fill=WHITE,anchor="lm")
        d.rounded_rectangle([290,y+15,990,y+65],radius=25,fill=(36,38,62))
        bw=max(50,int(700*p/45)); d.rounded_rectangle([290,y+15,290+bw,y+65],radius=25,fill=c)
        d.text((300+bw+16 if bw<620 else 290+bw-16,y+40),f"{p}%",font=F(POPB,32),fill=WHITE if bw<620 else (12,12,16),anchor="lm" if bw<620 else "rm")
    im.save(path,quality=95)
def pipeline(path):
    W,H=1000,400; im=base((W,H),(20,20,54),(4,4,12),T); d=ImageDraw.Draw(im)
    boxes=[("Your text",BLUE),("Tokens",(170,130,255)),("Model",AMB),("Odds",GR),("1 word",WHITE)]
    bw=150; gap=(W-80-bw*5)/4; y=110
    for i,(t,c) in enumerate(boxes):
        x=40+i*(bw+gap); panel(d,[x,y,x+bw,y+110],r=22,fill=(24,26,48),outline=c,w=4)
        d.text((x+bw/2,y+55),t,font=F(POPB,28),fill=WHITE,anchor="mm")
        if i<4: arrow(d,(x+bw+6,y+55),(x+bw+gap-6,y+55),WHITE,6,18)
    # loop back from last box to first
    xl=40+4*(bw+gap)+bw/2; xf=40+bw/2
    d.line([(xl,y+110),(xl,y+200)],fill=GREY,width=6); d.line([(xl,y+200),(xf,y+200)],fill=GREY,width=6)
    arrow(d,(xf,y+200),(xf,y+118),GREY,6,20)
    d.text((W/2,y+235),"add the word, repeat",font=F(POP,28),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def tokens(path):
    W,H=1000,330; im=base((W,H),(20,20,54),(4,4,12),T); d=ImageDraw.Draw(im)
    parts=["Chat","bots"," are"," surpris","ingly"," useful"]; cols=[BLUE,(170,130,255),GR,AMB,(255,120,90),(90,200,220)]
    sz=48
    while sum(d.textlength(p.strip(),font=F(POPB,sz))+36+12 for p in parts)>W-120: sz-=2
    f=F(POPB,sz); x=60; y=70
    for p,c in zip(parts,cols):
        w=d.textlength(p.strip(),font=f)+36
        d.rounded_rectangle([x,y,x+w,y+84],radius=16,fill=c); d.text((x+w/2,y+42),p.strip(),font=f,fill=(12,12,16),anchor="mm"); x+=w+12
    d.text((60,200),"Illustration: real splits vary by model",font=F(POP,28),fill=GREY)
    d.text((60,250),"English: 1 token ≈ 4 characters ≈ 3/4 of a word",font=F(POPB,30),fill=WHITE)
    im.save(path,quality=95)
def exam(path):
    W,H=1000,420; im=base((W,H),(20,20,54),(4,4,12),T); d=ImageDraw.Draw(im)
    d.text((W/2,50),"Q: When is this person's birthday?",font=F(POPB,34),fill=WHITE,anchor="mm")
    panel(d,[60,100,480,370],r=26,fill=(30,40,30),outline=GR,w=4)
    d.text((270,160),"GUESS",font=F(POPB,40),fill=GR,anchor="mm")
    d.text((270,230),"1 in 365 chance",font=F(POP,32),fill=WHITE,anchor="mm")
    d.text((270,290),"of a point",font=F(POP,32),fill=WHITE,anchor="mm")
    panel(d,[520,100,940,370],r=26,fill=(40,26,30),outline=RED,w=4)
    d.text((730,160),"“I DON'T KNOW”",font=F(POPB,36),fill=RED,anchor="mm")
    d.text((730,240),"0 points",font=F(POPB,48),fill=WHITE,anchor="mm")
    d.text((730,305),"every time",font=F(POP,30),fill=GREY,anchor="mm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); pipeline("d1.png"); tokens("d2.png"); exam("d3.png"); print("art ok")
