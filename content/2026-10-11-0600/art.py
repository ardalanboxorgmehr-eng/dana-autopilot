import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(150,40,60)
def group(d,x,y,w,h,edited):
    d.rounded_rectangle([x,y,x+w,y+h],radius=20,fill=(170,190,210))
    d.rectangle([x,y+h*0.72,x+w,y+h],fill=(120,150,110))
    cols=[(90,70,140),(200,90,60),(60,110,160)]
    for i in range(3):
        cx=x+w*(0.2+0.3*i); s=h*0.28
        if edited and i==1:
            person(d,cx,y+h*0.62,s,(120,124,140),(170,174,188))
            d.text((cx,y+h*0.62-s*0.58),"?",font=F(POPB,int(s*0.5)),fill=(40,44,56),anchor="mm")
            d.rectangle([cx-s*0.75,y+h*0.62-s*1.05,cx+s*0.75,y+h*0.62+s*0.72],outline=AMB,width=5)
        else:
            person(d,cx,y+h*0.62,s,(150,30,40) if edited else cols[i],(170,120,90))
def sparkle(d,cx,cy,r,col):
    d.polygon([(cx,cy-r),(cx+r*0.25,cy-r*0.25),(cx+r,cy),(cx+r*0.25,cy+r*0.25),(cx,cy+r),(cx-r*0.25,cy+r*0.25),(cx-r,cy),(cx-r*0.25,cy-r*0.25)],fill=col)
def heart(d,cx,cy,r,col):
    d.ellipse([cx-r,cy-r*0.8,cx,cy+r*0.2],fill=col); d.ellipse([cx,cy-r*0.8,cx+r,cy+r*0.2],fill=col)
    d.polygon([(cx-r*0.97,cy-r*0.15),(cx+r*0.97,cy-r*0.15),(cx,cy+r*1.1)],fill=col)
def cover(path):
    W,H=1080,900; im=base((W,H),(40,12,18),(6,3,4),T)
    im=addglow(im,lambda d:d.rectangle([160,150,920,700],fill=(255,90,110)),110,0.45)
    d=ImageDraw.Draw(im)
    d.rectangle([150,130,930,720],fill=(30,26,30),outline=(120,110,120),width=6)
    group(d,190,170,700,510,True)
    sparkle(d,540,210,50,AMB); sparkle(d,610,260,26,AMB)
    d.rounded_rectangle([700,640,900,700],radius=20,fill=RED); d.text((800,670),"AI EDIT",font=F(POPB,30),fill=WHITE,anchor="mm")
    im.save(path,quality=95)
def compare(path):
    W,H=1000,460; im=base((W,H),(40,12,18),(6,3,4),T); d=ImageDraw.Draw(im)
    group(d,540,70,400,300,False); group(d,60,70,400,300,True)
    fa(d,(740,420),"عکس اصلی",F(VB,36),WHITE,"ms"); fa(d,(260,420),"بعد از ادیت",F(VB,36),AMB,"ms")
    d.polygon([(480,220),(515,195),(515,245)],fill=WHITE)
    im.save(path,quality=95)
def viral(path):
    W,H=1000,520; im=base((W,H),(40,12,18),(6,3,4),T); d=ImageDraw.Draw(im)
    x0,y0,x1,y1=phone(d,330,10,340,500)
    group(d,x0+10,y0+30,x1-x0-20,200,True)
    for i in range(3): d.rounded_rectangle([x0+10,y0+250+i*34,x1-10-i*50,y0+266+i*34],radius=8,fill=(70,74,90))
    heart(d,x0+26,y0+372,14,RED); d.text((x0+50,y0+372),"12.4k",font=F(POPB,30),fill=RED,anchor="lm")
    for k,(x,y) in enumerate([(160,120),(820,160),(120,340),(860,380)]):
        d.ellipse([x-38,y-38,x+38,y+38],fill=(60,20,30),outline=RED,width=3); heart(d,x,y,18,RED)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); compare("d1.png"); viral("d2.png"); print("art ok")
