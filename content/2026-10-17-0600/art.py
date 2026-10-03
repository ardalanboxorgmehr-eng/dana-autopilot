import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(170,100,40)
VEN=(232,170,90); SUN=(255,200,80); EARTH=(70,140,230)
def planet(d,cx,cy,r,col,bands=True):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
    if bands:
        for k,dy in enumerate((-0.45,-0.1,0.3)):
            y=cy+dy*r; hw=math.sqrt(max(0,r*r-(y-cy)**2))*0.92
            d.rounded_rectangle([cx-hw,y-r*0.05,cx+hw,y+r*0.05],radius=int(r*0.05),fill=tuple(max(0,c-18) for c in col))
def arc_arrow(d,cx,cy,r,start,end,col,w=8,cw=True):
    """Draw an arc from start to end degrees (PIL angles, clockwise positive) with arrowhead at the end of travel."""
    if cw:
        d.arc([cx-r,cy-r,cx+r,cy+r],start,end,fill=col,width=w); tip=end; tang=1
    else:
        d.arc([cx-r,cy-r,cx+r,cy+r],end,start,fill=col,width=w); tip=end; tang=-1
    a=math.radians(tip); px,py=cx+r*math.cos(a),cy+r*math.sin(a)
    # tangent direction of travel
    tx,ty=-math.sin(a)*tang,math.cos(a)*tang
    nx,ny=math.cos(a),math.sin(a); s=w*2.6
    d.polygon([(px+tx*s,py+ty*s),(px-tx*s*0.3+nx*s*0.9,py-ty*s*0.3+ny*s*0.9),(px-tx*s*0.3-nx*s*0.9,py-ty*s*0.3-ny*s*0.9)],fill=col)
def cover(path):
    W,H=1080,900; im=base((W,H),(44,26,10),(8,5,3),T)
    im=addglow(im,lambda d:(d.ellipse([-120,120,360,600],fill=(255,170,40)),d.ellipse([480,140,980,640],fill=(230,140,60))),110,0.55)
    d=ImageDraw.Draw(im)
    d.ellipse([-80,200,240,520],fill=SUN)
    # orbit arc
    d.arc([0,60,1360,700],195,250,fill=(200,170,120),width=4)
    planet(d,720,380,190,VEN)
    arc_arrow(d,720,380,240,-150,-60,WHITE,w=8,cw=True)
    d.text((720,632),"1 day  =  243 Earth days",font=F(POPB,44),fill=AMB,anchor="ms")
    d.text((720,686),"1 year  =  225 Earth days",font=F(POPB,40),fill=WHITE,anchor="ms")
    im.save(path,quality=95)
def compare(path):
    W,H=1000,400; im=base((W,H),(44,26,10),(8,5,3),T); d=ImageDraw.Draw(im)
    bars(d,60,40,W-120,[("یه دور دور خودش",243,AMB,"243 days"),("یه دور دور خورشید",225,(170,176,190),"225 days")],rowh=150,maxv=243)
    im.save(path,quality=95)
def spin(path):
    W,H=1000,480; im=base((W,H),(20,24,44),(4,5,10),(60,80,150)); d=ImageDraw.Draw(im)
    planet(d,750,220,120,EARTH,bands=False)
    arc_arrow(d,750,220,160,-40,-140,WHITE,w=7,cw=False)
    d.text((750,440),"Earth",font=F(POPB,34),fill=WHITE,anchor="ms")
    planet(d,250,220,120,VEN)
    arc_arrow(d,250,220,160,-140,-40,AMB,w=7,cw=True)
    d.text((250,440),"Venus",font=F(POPB,34),fill=AMB,anchor="ms")
    im.save(path,quality=95)
def heat(path):
    W,H=1000,420; im=base((W,H),(50,20,10),(8,4,3),(180,70,30)); d=ImageDraw.Draw(im)
    # thermometer
    d.rounded_rectangle([140,40,200,300],radius=30,fill=(60,40,40)); d.ellipse([115,280,225,390],fill=RED)
    d.rounded_rectangle([155,70,185,320],radius=15,fill=RED)
    d.text((280,180),"464°C",font=F(POPB,110),fill=AMB,anchor="lm")
    fa(d,(930,320),"سرب اینجا ذوب می‌شه",F(VB,40),WHITE)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); compare("d1.png"); spin("d2.png"); heat("d3.png"); print("art ok")
