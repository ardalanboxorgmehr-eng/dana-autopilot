import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,90,150)
BL=(70,130,230); RD=(220,70,70)
def board(d,x0,y0,cell,n,reveal_mine=True):
    for r in range(n):
        for c in range(n):
            col=(54,92,60) if (r+c)%2==0 else (64,104,70)
            d.rectangle([x0+c*cell,y0+r*cell,x0+(c+1)*cell,y0+(r+1)*cell],fill=col)
    # lakes
    for c in (2,3,6,7):
        if c<n: d.rectangle([x0+c*cell,y0+4*cell,x0+(c+1)*cell,y0+6*cell],fill=(60,120,190)) if n>=10 else None
def piece(d,x,y,s,col,label=None,hidden=False):
    d.rounded_rectangle([x+s*0.12,y+s*0.12,x+s*0.88,y+s*0.88],radius=int(s*0.12),fill=col,outline=(20,20,26),width=2)
    if hidden:
        d.text((x+s/2,y+s/2),"?",font=F(POPB,int(s*0.5)),fill=(255,230,230),anchor="mm")
    elif label:
        d.text((x+s/2,y+s/2),label,font=F(POPB,int(s*0.38)),fill=WHITE,anchor="mm")
def cover(path):
    W,H=1080,900; im=base((W,H),(12,22,40),(4,6,10),T)
    im=addglow(im,lambda d:(d.ellipse([140,80,940,760],fill=(70,120,220)),),130,0.45)
    d=ImageDraw.Draw(im)
    n=10; cell=62; x0=(W-n*cell)//2; y0=70
    board(d,x0,y0,cell,n)
    import random; r=random.Random(4)
    labels=["10","9","8","7","6","5","4","3","2","S","B","F"]
    for row in range(0,4):
        for c in range(n):
            if r.random()<0.75: piece(d,x0+c*cell,y0+row*cell,cell,RD,hidden=True)
    for row in range(6,10):
        for c in range(n):
            if r.random()<0.75: piece(d,x0+c*cell,y0+row*cell,cell,BL,label=r.choice(labels))
    # score badge
    d.rounded_rectangle([W/2-190,y0+n*cell+20,W/2+190,y0+n*cell+110],radius=44,fill=(16,20,30),outline=AMB,width=4)
    d.text((W/2,y0+n*cell+65),"15 - 1 - 4",font=F(POPB,50),fill=AMB,anchor="mm")
    im.save(path,quality=95)
def hidden(path):
    W,H=1000,420; im=base((W,H),(12,22,40),(4,6,10),T); d=ImageDraw.Draw(im)
    # chess: all visible vs stratego hidden
    panel(d,[50,40,470,380],r=26,fill=(18,22,32),outline=GR,w=4)
    d.text((260,80),"Chess",font=F(POPB,36),fill=GR,anchor="mm")
    for i,t in enumerate(["K","Q","R","B","N","P"]):
        piece(d,80+i*64,150,64,(90,96,112),label=t)
    for i,t in enumerate(["K","Q","R","B","N","P"]):
        piece(d,80+i*64,240,64,BL,label=t)
    d.text((260,345),"everything visible",font=F(POP,26),fill=GREY,anchor="mm")
    panel(d,[530,40,950,380],r=26,fill=(18,22,32),outline=RD,w=4)
    d.text((740,80),"Stratego",font=F(POPB,36),fill=RD,anchor="mm")
    for i in range(6): piece(d,560+i*64,150,64,RD,hidden=True)
    for i,t in enumerate(["10","S","B","F","3","2"]): piece(d,560+i*64,240,64,BL,label=t)
    d.text((740,345),"opponent pieces hidden",font=F(POP,26),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def score(path):
    W,H=1000,440; im=base((W,H),(12,22,40),(4,6,10),T); d=ImageDraw.Draw(im)
    fa(d,(W-60,40),"در برابر قوی‌ترین بازیکن دنیا، ۲۰ بازی",F(VB,36),(225,228,236))
    items=[("AI",15,GR),("Draw",4,GREY),("Human",1,RD)]
    for i,(t,v,c) in enumerate(items):
        y=130+i*95
        d.text((60,y+30),t,font=F(POPB,34),fill=WHITE,anchor="lm")
        d.rounded_rectangle([230,y,940,y+60],radius=30,fill=(38,42,54))
        bw=max(70,int(710*v/15))
        d.rounded_rectangle([230,y,230+bw,y+60],radius=30,fill=c)
        d.text((230+bw-24,y+30),str(v),font=F(POPB,34),fill=(12,12,16),anchor="rm")
    im.save(path,quality=95)
def compute(path):
    W,H=1000,400; im=base((W,H),(12,22,40),(4,6,10),T); d=ImageDraw.Draw(im)
    d.text((60,40),"Training examples needed",font=F(POPB,36),fill=WHITE)
    d.text((60,130),"DeepNash",font=F(POPB,32),fill=GREY)
    d.rounded_rectangle([60,180,940,236],radius=28,fill=(110,116,132))
    d.text((60,270),"Ataraxos",font=F(POPB,32),fill=GR)
    d.rounded_rectangle([60,320,60+70,376],radius=28,fill=GR)
    d.text((150,348),"< 1/100",font=F(POPB,34),fill=GR,anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); hidden("d1.png"); score("d2.png"); compute("d3.png"); print("art ok")
