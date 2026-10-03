import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(190,130,30)
HON=(240,170,40); HON2=(255,205,90); CLAY=(170,110,70)
def jar(d,cx,base,w,h,col=HON):
    d.rounded_rectangle([cx-w/2,base-h,cx+w/2,base],radius=int(w*0.18),fill=(220,230,240),outline=(200,210,220),width=4)
    d.rounded_rectangle([cx-w/2+12,base-h*0.8,cx+w/2-12,base-12],radius=int(w*0.14),fill=col)
    d.rounded_rectangle([cx-w*0.42,base-h-34,cx+w*0.42,base-h+6],radius=10,fill=(150,100,50))
    d.rounded_rectangle([cx-w*0.3,base-h*0.55,cx+w*0.3,base-h*0.3],radius=10,fill=(250,240,220))
def pot(d,cx,base,s,col=CLAY):
    d.ellipse([cx-s*0.6,base-s*1.1,cx+s*0.6,base],fill=col)
    d.rectangle([cx-s*0.22,base-s*1.35,cx+s*0.22,base-s*0.95],fill=col)
    d.rounded_rectangle([cx-s*0.32,base-s*1.45,cx+s*0.32,base-s*1.3],radius=8,fill=tuple(c-30 for c in col))
    d.line([(cx-s*0.5,base-s*0.6),(cx+s*0.5,base-s*0.6)],fill=tuple(c-40 for c in col),width=5)
def hexgrid(d,x0,y0,cols,rows,r,col):
    for j in range(rows):
        for i in range(cols):
            cx=x0+i*r*1.75+(r*0.875 if j%2 else 0); cy=y0+j*r*1.5
            pts=[(cx+r*math.cos(math.radians(60*k+30)),cy+r*math.sin(math.radians(60*k+30))) for k in range(6)]
            d.polygon(pts,outline=col,width=4)
def cover(path):
    W,H=1080,900; im=base((W,H),(44,30,8),(8,6,3),T)
    im=addglow(im,lambda d:(d.ellipse([140,140,620,640],fill=(255,180,50)),d.ellipse([620,200,1000,640],fill=(200,120,60))),120,0.5)
    d=ImageDraw.Draw(im)
    hexgrid(d,60,60,11,3,52,(120,90,30))
    jar(d,350,640,300,360)
    # drip
    d.rounded_rectangle([330,236,370,300],radius=20,fill=HON); d.ellipse([326,288,374,336],fill=HON)
    pot(d,800,640,250)
    d.text((800,320),"?",font=F(POPB,120),fill=AMB,anchor="ms")
    d.text((800,690),"~3,000 years",font=F(POPB,40),fill=WHITE,anchor="ms")
    im.save(path,quality=95)
def water(path):
    W,H=1000,400; im=base((W,H),(44,30,8),(8,6,3),T); d=ImageDraw.Draw(im)
    bars(d,60,40,W-120,[("آب شهد گل",80,(120,180,240),"60-80%"),("آب عسل آماده",18,HON2,"15-18%")],rowh=150,maxv=100)
    im.save(path,quality=95)
def enzyme(path):
    W,H=1000,480; im=base((W,H),(44,30,8),(8,6,3),T); d=ImageDraw.Draw(im)
    def box(x,y,w,t,col):
        panel(d,[x,y,x+w,y+90],r=24,fill=(30,26,20),outline=col,w=4)
        d.text((x+w/2,y+45),t,font=F(POPB,30),fill=WHITE,anchor="mm")
    box(60,80,250,"nectar sugar",HON2)
    box(60,250,250,"bee enzyme",GR)
    d.text((185,215),"+",font=F(POPB,50),fill=WHITE,anchor="mm")
    # arrow pointing right (flow direction)
    d.rectangle([350,215,520,235],fill=WHITE); d.polygon([(520,195),(570,225),(520,255)],fill=WHITE)
    d.text((460,190),"glucose oxidase",font=F(POP,22),fill=GREY,anchor="ms")
    box(610,80,330,"gluconic acid",AMB)
    box(610,250,330,"hydrogen peroxide",BLUE)
    d.text((500,430),"= acidic + antibacterial",font=F(POPB,30),fill=AMB,anchor="ms")
    im.save(path,quality=95)
def ages(path):
    W,H=1000,460; im=base((W,H),(44,30,8),(8,6,3),T); d=ImageDraw.Draw(im)
    rows=[("Georgia tomb, oldest known honey",5500,AMB,"~4,700-5,500 yrs"),("Egyptian tombs, honey pots",3300,CLAY,"3,000+ yrs")]
    for i,(lab,v,col,vt) in enumerate(rows):
        y=40+i*170
        d.text((60,y),lab,font=F(POPB,32),fill=WHITE)
        by=y+55; d.rounded_rectangle([60,by,940,by+50],radius=25,fill=(38,42,54))
        bw=int(880*v/5500); d.rounded_rectangle([60,by,60+bw,by+50],radius=25,fill=col)
        d.text((80,by+25),vt,font=F(POPB,28),fill=(20,16,10),anchor="lm")
    d.text((60,410),"edible after 3,000 years? not documented",font=F(POPB,30),fill=RED)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); water("d1.png"); enzyme("d2.png"); ages("d3.png"); print("art ok")
