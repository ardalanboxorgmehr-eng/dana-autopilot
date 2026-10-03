import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
from PIL import ImageFilter
T=(160,60,120)
C1=(40,14,34); C2=(8,4,8)
PINK=(255,110,170)
PARTS=[("SUBJECT",(255,206,84)),("STYLE",(255,110,170)),("LIGHT",(255,160,70)),("CAMERA",(90,160,240)),("MOOD",(60,200,150))]
def arrow(d,p0,p1,col,w=10,hl=34):
    (x0,y0),(x1,y1)=p0,p1; L=math.hypot(x1-x0,y1-y0); ux,uy=(x1-x0)/L,(y1-y0)/L
    bx,by=x1-ux*hl,y1-uy*hl
    d.line([(x0,y0),(bx,by)],fill=col,width=w)
    d.polygon([(x1,y1),(bx-uy*hl*0.6,by+ux*hl*0.6),(bx+uy*hl*0.6,by-ux*hl*0.6)],fill=col)
def scene(w,h,sky1,sky2,sun,mount,ground,blur=0,flat=False):
    im=Image.new("RGB",(w,h)); d=ImageDraw.Draw(im)
    for y in range(h):
        t=y/h; d.line([(0,y),(w,y)],fill=tuple(int(sky1[i]*(1-t)+sky2[i]*t) for i in range(3)))
    if sun: d.ellipse([w*0.62,h*0.16,w*0.62+h*0.26,h*0.42],fill=sun)
    d.polygon([(-10,h*0.8),(w*0.3,h*0.36),(w*0.55,h*0.8)],fill=mount[0])
    d.polygon([(w*0.3,h*0.8),(w*0.65,h*0.46),(w+10,h*0.8)],fill=mount[1])
    if not flat:
        d.polygon([(w*0.3,h*0.36),(w*0.24,h*0.47),(w*0.36,h*0.47)],fill=(240,240,245))
    d.rectangle([0,h*0.8,w,h],fill=ground)
    # small house
    hx,hy=w*0.18,h*0.8
    d.rectangle([hx,hy-h*0.12,hx+w*0.14,hy],fill=(200,90,70)); d.polygon([(hx-8,hy-h*0.12),(hx+w*0.07,hy-h*0.22),(hx+w*0.14+8,hy-h*0.12)],fill=(90,50,40))
    d.rectangle([hx+w*0.05,hy-h*0.07,hx+w*0.09,hy],fill=(255,220,120))
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    return im
def paste_round(im,tile,x,y,r=22):
    m=Image.new("L",tile.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,tile.width-1,tile.height-1],radius=r,fill=255)
    im.paste(tile,(x,y),m)
def cover(path):
    W,H=1080,900; im=base((W,H),C1,C2,T)
    im=addglow(im,lambda d:d.ellipse([520,100,1060,700],fill=(255,120,180)),130,0.45)
    d=ImageDraw.Draw(im)
    for i,(t,c) in enumerate(PARTS):
        y=110+i*112
        d.rounded_rectangle([60,y,390,y+84],radius=42,fill=c)
        d.text((225,y+42),t,font=F(POPB,38),fill=(20,10,16),anchor="mm")
        if i<4: d.text((225,y+98),"+",font=F(POPB,34),fill=WHITE,anchor="mm")
    arrow(d,(420,360),(540,360),WHITE,10)
    tile=scene(460,520,(255,170,90),(140,70,120),(255,230,150),[(90,60,110),(70,50,90)],(60,40,60))
    d.rounded_rectangle([565,95,1035,625],radius=28,fill=WHITE)
    paste_round(im,tile,570,100,24)
    im.save(path,quality=95)
def styles(path):
    W,H=1000,480; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    tw,th=210,300
    tiles=[("Photo",scene(tw,th,(120,170,230),(220,230,240),(255,250,220),[(90,100,110),(70,80,90)],(80,110,60))),
           ("Watercolor",scene(tw,th,(170,210,240),(250,240,230),(255,220,170),[(150,170,200),(130,160,190)],(170,200,150),blur=5)),
           ("Flat vector",scene(tw,th,(80,200,220),(80,200,220),(255,210,60),[(40,90,140),(30,70,120)],(60,170,100),flat=True)),
           ("Neon art",scene(tw,th,(40,10,80),(200,40,140),(255,90,200),[(60,20,110),(90,30,140)],(30,10,50)))]
    for i,(lab,t) in enumerate(tiles):
        x=40+i*(tw+30); paste_round(im,t,x,50)
        d.text((x+tw/2,400),lab,font=F(POPB,30),fill=WHITE,anchor="mm")
    d.text((W/2,450),"same subject, different style",font=F(POP,24),fill=GREY,anchor="mm")
    im.save(path,quality=95)
def lights(path):
    W,H=1000,460; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    tw,th=290,300
    tiles=[("golden hour",scene(tw,th,(255,180,90),(255,120,80),(255,230,150),[(140,80,70),(110,60,60)],(90,60,40))),
           ("overcast",scene(tw,th,(170,175,185),(200,204,210),None,[(110,116,126),(95,100,110)],(100,110,100))),
           ("neon at night",scene(tw,th,(20,10,50),(90,20,100),(255,80,200),[(40,20,80),(60,30,110)],(20,10,40)))]
    for i,(lab,t) in enumerate(tiles):
        x=40+i*(tw+25); paste_round(im,t,x,40)
        d.text((x+tw/2,395),lab,font=F(POPB,30),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def formula(path):
    W,H=1000,520; im=base((W,H),C1,C2,T); d=ImageDraw.Draw(im)
    panel(d,[40,30,W-40,H-30],r=30,fill=(26,18,26),outline=(110,70,100))
    segs=[("an old orange cat asleep on books,",0),("watercolor illustration,",1),("soft window light,",2),("close-up, shallow depth of field,",3),("cozy mood",4)]
    y=75; f=F(POPB,34)
    for t,k in segs:
        c=PARTS[k][1]
        d.text((90,y),t,font=f,fill=WHITE)
        tw=d.textlength(t,font=f); d.rounded_rectangle([90,y+48,90+tw,y+56],radius=4,fill=c)
        d.text((W-90,y+20),PARTS[k][0],font=F(POPB,24),fill=c,anchor="ra")
        y+=82
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); styles("d1.png"); lights("d2.png"); formula("d3.png"); print("art ok")
