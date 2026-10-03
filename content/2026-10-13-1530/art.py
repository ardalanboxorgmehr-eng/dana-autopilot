import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(30,110,160)
CY=(80,200,230)
def bell(d,cx,cy,s,col):
    d.pieslice([cx-s,cy-s,cx+s,cy+s*1.1],180,360,fill=col)
    d.rectangle([cx-s,cy,cx+s,cy+s*0.6],fill=col)
    d.rounded_rectangle([cx-s*1.25,cy+s*0.55,cx+s*1.25,cy+s*0.8],radius=int(s*0.12),fill=col)
    d.ellipse([cx-s*0.25,cy+s*0.8,cx+s*0.25,cy+s*1.2],fill=col)
def eye(d,cx,cy,w,col):
    d.ellipse([cx-w,cy-w*0.5,cx+w,cy+w*0.5],outline=col,width=8)
    d.ellipse([cx-w*0.32,cy-w*0.32,cx+w*0.32,cy+w*0.32],fill=col)
def cover(path):
    W,H=1080,900; im=base((W,H),(10,30,42),(4,8,10),T)
    im=addglow(im,lambda d:(d.ellipse([80,100,560,700],fill=(60,170,230)),d.ellipse([560,200,1040,760],fill=(60,220,160))),120,0.5)
    d=ImageDraw.Draw(im)
    # search bar
    panel(d,[70,90,1010,190],r=50,fill=(240,242,248),outline=(240,242,248),w=2)
    d.ellipse([105,118,150,163],outline=(60,120,220),width=6); d.line([(145,158),(165,178)],fill=(60,120,220),width=6)
    d.text((190,140),"Keep me updated when the price drops",font=F(POP,34),fill=(40,44,56),anchor="lm")
    # sources scanned (left to right flow)
    srcs=[("Shops",GR),("Forums",AMB),("News",BLUE),("Posts",(240,120,170))]
    for i,(t,c) in enumerate(srcs):
        y=260+i*120
        panel(d,[70,y,330,y+90],r=22,fill=(18,26,34),outline=c,w=4)
        d.text((200,y+45),t,font=F(POPB,32),fill=c,anchor="mm")
        d.line([(340,y+45),(470,430)],fill=(90,110,130),width=4)
    eye(d,540,430,90,CY)
    # arrow to phone
    d.polygon([(650,410),(700,410),(700,385),(745,430),(700,475),(700,450),(650,450)],fill=WHITE)
    x0,y0,x1,y1=phone(d,765,220,280,450)
    panel(d,[x0,y0+30,x1,y0+200],r=18,fill=(30,40,56),outline=CY,w=3)
    bell(d,x0+40,y0+80,22,AMB)
    d.text((x0+75,y0+62),"Price drop",font=F(POPB,26),fill=WHITE)
    d.text((x0+75,y0+100),"Now $79",font=F(POP,22),fill=GR)
    d.text((x0+20,y0+150),"AI Mode alert",font=F(POP,22),fill=GREY)
    im.save(path,quality=95)
def howto(path):
    W,H=1000,480; im=base((W,H),(10,30,42),(4,8,10),T); d=ImageDraw.Draw(im)
    panel(d,[50,30,W-50,H-30],r=30,fill=(16,22,30),outline=(70,100,120))
    d.text((90,70),"AI Mode",font=F(POPB,36),fill=CY)
    d.rounded_rectangle([340,130,W-90,250],radius=26,fill=(40,64,110))
    d.text((370,150),"Tell me when applications",font=F(POP,30),fill=WHITE)
    d.text((370,195),"open for this program",font=F(POP,30),fill=WHITE)
    d.rounded_rectangle([90,280,700,410],radius=26,fill=(28,70,52))
    d.text((120,300),"OK. I'll keep checking",font=F(POP,30),fill=WHITE)
    d.text((120,348),"and notify you.",font=F(POP,30),fill=WHITE)
    bell(d,800,320,40,AMB)
    im.save(path,quality=95)
def examples(path):
    W,H=1000,520; im=base((W,H),(10,30,42),(4,8,10),T); d=ImageDraw.Draw(im)
    items=[("Back in stock",GR),("Price drop",AMB),("New place nearby",BLUE),("Holiday activities",(240,120,170))]
    for i,(t,c) in enumerate(items):
        x=60+(i%2)*450; y=50+(i//2)*230
        panel(d,[x,y,x+430,y+200],r=28,fill=(16,22,30),outline=c,w=4)
        bell(d,x+70,y+80,30,c)
        d.text((x+130,y+100),t,font=fiten(d,t,POPB,280,34),fill=WHITE,anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); howto("d1.png"); examples("d2.png"); print("art ok")
