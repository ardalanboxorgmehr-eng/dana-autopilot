import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "build"))
from art_kit import *
T=(30,130,120)
def cover(path):
    W,H=1080,900; im=base((W,H),(12,30,32),(4,8,8),T)
    im=addglow(im,lambda d:(d.ellipse([120,120,520,640],fill=(60,220,150)),d.ellipse([560,260,960,760],fill=(255,70,70))),120,0.5)
    d=ImageDraw.Draw(im)
    base_y=450
    d.line([(90,base_y),(990,base_y)],fill=(200,205,215),width=4)
    # practice (right side, RTL first)
    d.rounded_rectangle([640,base_y-340,860,base_y],radius=24,fill=GR)
    d.text((750,base_y-380),"+48%",font=F(POPB,70),fill=GR,anchor="ms")
    fa(d,(750,base_y+70),"سر تمرین",F(VK,54),WHITE,"ms")
    d.text((750,base_y+120),"with AI",font=F(POPB,30),fill=GREY,anchor="ms")
    # exam
    d.rounded_rectangle([220,base_y,440,base_y+120],radius=24,fill=RED)
    d.text((330,base_y-40),"-17%",font=F(POPB,70),fill=RED,anchor="ms")
    fa(d,(330,base_y+200),"سر امتحان",F(VK,54),WHITE,"ms")
    d.text((330,base_y+250),"without AI",font=F(POPB,30),fill=GREY,anchor="ms")
    im.save(path,quality=95)
def practice(path):
    W,H=1000,470; im=base((W,H),(12,30,32),(4,8,8),T); d=ImageDraw.Draw(im)
    bars(d,60,40,W-120,[("فقط کتاب و جزوه",100,(120,126,140),"100%"),("چت‌بات معمولی",148,GR,"148%"),("چت‌بات معلم",227,AMB,"227%")],rowh=140,maxv=227)
    im.save(path,quality=95)
def exam(path):
    W,H=1000,470; im=base((W,H),(30,12,12),(8,4,4),(150,40,40)); d=ImageDraw.Draw(im)
    bars(d,60,40,W-120,[("فقط کتاب و جزوه",100,(120,126,140),"100%"),("چت‌بات معمولی",83,RED,"83%"),("چت‌بات معلم",100,AMB,"~100%")],rowh=140,maxv=100)
    im.save(path,quality=95)
if __name__=="__main__":
    cover("s1.png"); practice("d1.png"); exam("d2.png"); print("art ok")
