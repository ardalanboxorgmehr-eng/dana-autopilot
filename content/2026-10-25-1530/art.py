import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(40,80,170)
C1=(14,20,46); C2=(4,5,12)
def arrow(d,p0,p1,col,w=10,hl=34):
    (x0,y0),(x1,y1)=p0,p1; L=math.hypot(x1-x0,y1-y0); ux,uy=(x1-x0)/L,(y1-y0)/L
    bx,by=x1-ux*hl,y1-uy*hl
    d.line([(x0,y0),(bx,by)],fill=col,width=w)
    d.polygon([(x1,y1),(bx-uy*hl*0.6,by+ux*hl*0.6),(bx+uy*hl*0.6,by-ux*hl*0.6)],fill=col)
def sticky(d,x,y,w,h,lines,f):
    d.polygon([(x,y),(x+w,y),(x+w,y+h-40),(x+w-40,y+h),(x,y+h)],fill=(255,222,110))
    d.polygon([(x+w,y+h-40),(x+w-40,y+h),(x+w-40,y+h-40)],fill=(220,180,70))
    for i,t in enumerate(lines): d.text((x+24,y+28+i*f.size*1.5),t,font=f,fill=(60,46,10))
def email(d,x,y,w,h,to,subj,body,f):
    panel(d,[x,y,x+w,y+h],r=24,fill=(240,242,248),outline=(120,140,200),w=4)
    d.rounded_rectangle([x,y,x+w,y+56],radius=24,fill=(60,100,200)); d.rectangle([x,y+30,x+w,y+56],fill=(60,100,200))
    d.text((x+24,y+28),"New message",font=F(POPB,26),fill=WHITE,anchor="lm")
    d.text((x+24,y+84),"To: "+to,font=F(POP,24),fill=(90,96,110),anchor="lm")
    d.line([(x+20,y+108),(x+w-20,y+108)],fill=(200,204,214),width=2)
    d.text((x+24,y+134),"Subject: "+subj,font=F(POPB,24),fill=(30,34,46),anchor="lm")
    d.line([(x+20,y+158),(x+w-20,y+158)],fill=(200,204,214),width=2)
    for i,t in enumerate(body): d.text((x+24,y+178+i*f.size*1.5),t,font=f,fill=(40,44,56))
    d.rounded_rectangle([x+24,y+h-66,x+150,y+h-20],radius=22,fill=(60,100,200))
    d.text((x+87,y+h-43),"Send",font=F(POPB,24),fill=WHITE,anchor="mm")
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:(d.ellipse([80,140,460,560],fill=(255,210,80)),d.ellipse([500,80,1060,700],fill=(80,140,255))),130,0.45)
    d=ImageDraw.Draw(im)
    sticky(d,70,200,340,340,["- meeting moved?","- need report by Fri","- ask nicely!!","- thanks for help"],F(POP,28))
    arrow(d,(430,370),(530,370),WHITE,10)
    email(d,550,120,480,560,"manager@company.com","Report deadline",["Hi Sara,","Could we move our","meeting to Thursday?","I'll send the report","by Friday.","Thanks for your help!"],F(POP,26))
    im.save(path,quality=95)
def notes(path):
    W,H=1000,480; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[40,40,420,H-40],r=26,fill=(30,30,24),outline=(255,222,110))
    d.text((70,70),"YOUR NOTES",font=F(POPB,28),fill=AMB)
    for i,t in enumerate(["late, sorry","price ok?","call next week"]): d.text((70,135+i*60),"- "+t,font=F(POP,32),fill=WHITE)
    arrow(d,(440,240),(560,240),WHITE,10)
    panel(d,[580,40,960,H-40],r=26,fill=(240,242,248),outline=(120,140,200))
    d.text((610,70),"CLEAN EMAIL",font=F(POPB,28),fill=(60,100,200))
    for i,wd in enumerate([300,320,260,310,200,280]): d.rounded_rectangle([610,135+i*44,610+wd,153+i*44],radius=8,fill=(180,188,206))
    im.save(path,quality=95)
def tone(path):
    W,H=1000,440; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    d.text((W/2,60),"TONE",font=F(POPB,34),fill=GREY,anchor="mm")
    d.rounded_rectangle([100,150,900,174],radius=12,fill=(50,56,80))
    d.rounded_rectangle([100,150,560,174],radius=12,fill=BLUE)
    d.ellipse([530,132,590,192],fill=WHITE)
    d.text((100,220),"Formal",font=F(POPB,30),fill=WHITE); d.text((900,220),"Friendly",font=F(POPB,30),fill=WHITE,anchor="ra")
    chips=[("Formal",(60,70,100)),("Firm but polite",BLUE),("Warm",(60,70,100))]
    x=110
    for t,c in chips:
        w=d.textlength(t,font=F(POPB,30))+60
        d.rounded_rectangle([x,310,x+w,370],radius=30,fill=c); d.text((x+w/2,340),t,font=F(POPB,30),fill=WHITE,anchor="mm"); x+=w+30
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); notes("d1.png"); tone("d2.png"); print("art ok")
