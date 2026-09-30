import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,110,210)
def doc(d,x,y,w,h,lab,col):
    panel(d,[x,y,x+w,y+h],r=18,fill=(236,238,244),outline=col,w=4)
    for i in range(5): d.rounded_rectangle([x+24,y+60+i*34,x+w-24-(i%2)*60,y+74+i*34],radius=6,fill=(190,196,210))
    d.rounded_rectangle([x+16,y+14,x+16+d.textlength(lab,font=F(POPB,24))+24,y+48],radius=12,fill=col)
    d.text((x+28,y+31),lab,font=F(POPB,24),fill=WHITE,anchor="lm")
def cover(path):
    W,H=1080,900; im=base((W,H),(12,26,50),(4,6,12),T)
    im=addglow(im,lambda d:d.ellipse([500,150,1040,760],fill=(80,150,255)),120,0.5)
    d=ImageDraw.Draw(im)
    doc(d,70,170,300,300,"PDF",(220,70,70)); doc(d,120,440,300,300,"NOTES",(60,160,110))
    d.polygon([(595,450),(535,410),(535,430),(470,430),(470,470),(535,470),(535,490)],fill=WHITE)
    # outputs column
    panel(d,[630,120,1010,340],r=26,fill=(20,26,40),outline=BLUE,w=4)
    d.rounded_rectangle([660,150,980,290],radius=16,fill=(34,60,110))
    d.polygon([(800,185),(800,255),(860,220)],fill=WHITE)
    d.text((820,322),"Video overview · 1:00",font=F(POPB,24),fill=AMB,anchor="ms")
    panel(d,[630,370,1010,560],r=26,fill=(20,26,40),outline=GR,w=4)
    d.text((660,395),"Quiz",font=F(POPB,30),fill=GR)
    for i,t in enumerate(["A","B","C"]):
        y=440+i*38; d.ellipse([662,y,688,y+26],outline=WHITE,width=3); d.rounded_rectangle([704,y+6,960-i*50,y+20],radius=6,fill=(80,90,110))
    panel(d,[630,590,1010,760],r=26,fill=(20,26,40),outline=AMB,w=4)
    d.text((660,615),"Flashcards",font=F(POPB,30),fill=AMB)
    for i in range(3): d.rounded_rectangle([660+i*110,665,750+i*110,740],radius=12,fill=(60,66,84),outline=(120,126,140),width=2)
    im.save(path,quality=95)
def video(path):
    W,H=1000,460; im=base((W,H),(12,26,50),(4,6,12),T); d=ImageDraw.Draw(im)
    panel(d,[60,40,W-60,H-40],r=30,fill=(18,24,38),outline=BLUE,w=4)
    d.rounded_rectangle([100,80,W-100,330],radius=20,fill=(30,54,100))
    d.ellipse([W/2-60,145,W/2+60,265],fill=(255,255,255)); d.polygon([(W/2-20,175),(W/2-20,235),(W/2+34,205)],fill=(30,54,100))
    d.rounded_rectangle([100,360,W-100,372],radius=6,fill=(60,70,90)); d.rounded_rectangle([100,360,400,372],radius=6,fill=AMB)
    d.text((100,395),"0:18",font=F(POPB,26),fill=GREY); d.text((W-100,395),"1:00",font=F(POPB,26),fill=GREY,anchor="ra")
    im.save(path,quality=95)
def quiz(path):
    W,H=1000,520; im=base((W,H),(12,26,50),(4,6,12),T); d=ImageDraw.Draw(im)
    items=[("Short answer",GR),("Multiple select",BLUE),("Fill in the blank",AMB)]
    for i,(t,c) in enumerate(items):
        y=40+i*155; panel(d,[60,y,W-60,y+130],r=26,fill=(18,24,38),outline=c,w=4)
        d.text((100,y+45),t,font=F(POPB,38),fill=WHITE,anchor="lm")
        if i==0: d.rounded_rectangle([100,y+78,700,y+112],radius=10,fill=(40,48,66))
        if i==1:
            for k in range(3): d.rounded_rectangle([100+k*70,y+78,140+k*70,y+112],radius=8,fill=c if k!=1 else (40,48,66))
        if i==2: d.text((100,y+95),"The heart has ____ chambers.",font=F(POP,28),fill=GREY,anchor="lm")
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); video("d1.png"); quiz("d2.png"); print("art ok")
