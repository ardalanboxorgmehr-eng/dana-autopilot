# Generic builder for Dana AI carousels. Usage: python3 dana_ai.py spec.json
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD=os.path.join(os.path.dirname(os.path.abspath(__file__)),"fonts")
BLACK=os.path.join(FD,"Vazirmatn-Black.ttf"); BOLD=os.path.join(FD,"Vazirmatn-Bold.ttf"); SEMI=os.path.join(FD,"Vazirmatn-SemiBold.ttf")
POP=os.path.join(FD,"Poppins-Medium.ttf"); POPB=os.path.join(FD,"Poppins-Bold.ttf")
W,H=1080,1350; GREEN=(58,190,72); ACC=(255,206,84)
FA=dict(direction="rtl",language="fa")
def F(p,s): return ImageFont.truetype(p,s)
def fitfa(d,t,p,maxw,start):
    s=start
    while s>18:
        f=F(p,s)
        if d.textlength(t,font=f,**FA)<=maxw: return f
        s-=2
    return F(p,18)
def _greedy(d,words,f,maxw):
    out=[];cur=""
    for w in words:
        tt=(cur+" "+w).strip()
        if d.textlength(tt,font=f,**FA)<=maxw or not cur: cur=tt
        else: out.append(cur); cur=w
    out.append(cur); return out
def wrapfa(d,t,f,maxw):
    out=[]
    for para in t.split("\n"):
        words=para.split(" "); g=_greedy(d,words,f,maxw); n=len(g)
        lo,hi=maxw*0.4,maxw
        while hi-lo>4:  # balance: narrowest width keeping same line count
            mid=(lo+hi)/2
            if len(_greedy(d,words,f,mid))<=n: hi=mid
            else: lo=mid
        out+=_greedy(d,words,f,hi)
    return out
def wrapen(d,t,f,maxw):
    out=[]
    for para in t.split("\n"):
        line=""
        for w in para.split(" "):
            tt=(line+" "+w).strip()
            if d.textlength(tt,font=f)<=maxw: line=tt
            else: out.append(line); line=w
        out.append(line)
    return out
def load(src,crop=None):
    im=Image.open(src).convert("RGB")
    if crop: im=im.crop(tuple(crop))
    return im
def bg(glowcol):
    c=Image.new("RGB",(W,H),(10,10,12))
    g=Image.new("L",(W,H),0); ImageDraw.Draw(g).ellipse([-200,-520,W+200,420],fill=85); g=g.filter(ImageFilter.GaussianBlur(120))
    return Image.composite(Image.new("RGB",(W,H),tuple(glowcol)),c,g)
def photo_top(im,ph):
    s=W/im.width; p=im.resize((W,int(im.height*s)),Image.LANCZOS)
    if p.height<ph:  # scale to fill height
        s=ph/im.height; p=im.resize((int(im.width*s),ph),Image.LANCZOS); x=(p.width-W)//2; p=p.crop((x,0,x+W,ph))
    c=Image.new("RGB",(W,H),(0,0,0)); hh=min(ph,p.height); c.paste(p.crop((0,0,W,hh)),(0,0))
    fade=150; g=Image.new("L",(W,fade))
    for y in range(fade): ImageDraw.Draw(g).line([(0,y),(W,y)],fill=int(255*(y/fade)**1.4))
    c.paste(Image.new("RGB",(W,fade),(0,0,0)),(0,hh-fade),g)
    return c
def cover(s,sp):
    c=photo_top(load(sp["src"],sp.get("crop")),sp.get("ph",830)); d=ImageDraw.Draw(c)
    lines=sp["lines"]; top=sp.get("ph",830)-10
    f=min([fitfa(d,t,BLACK,W-120,sp.get("size",90)) for t in lines],key=lambda x:x.size)
    lh=f.size*1.42; y=top+(H-top-lh*len(lines))/2-f.size*0.1
    for i,t in enumerate(lines):
        d.text((W/2,y),t,font=f,fill=ACC if i==0 else (255,255,255),anchor="ma",**FA); y+=lh
    return c
def card(s,sp):
    c=bg(s.get("glow",(40,90,160)))
    if sp.get("bgsrc") or (not sp.get("src") and s.get("bgsrc")):
        b=load(sp.get("bgsrc",s.get("bgsrc")),sp.get("bgcrop",s.get("bgcrop")))
        sc=max(W/b.width,H/b.height); b=b.resize((int(b.width*sc)+1,int(b.height*sc)+1),Image.LANCZOS)
        x=(b.width-W)//2; y=(b.height-H)//2; b=b.crop((x,y,x+W,y+H)).filter(ImageFilter.GaussianBlur(18))
        c=Image.blend(b,Image.new("RGB",(W,H),(8,8,10)),0.72)
    d=ImageDraw.Draw(c)
    ft=fitfa(d,sp["title"],BLACK,W-120,84)
    img=sp.get("src")
    if not img: ft=fitfa(d,sp["title"],BLACK,W-120,100)
    fsz=46 if img else 60
    fs=F(SEMI,fsz); sl=wrapfa(d,sp.get("sub",""),fs,W-140) if sp.get("sub") else []
    th=ft.size*1.55+len(sl)*fs.size*1.6+(50 if img else 0)
    im=None
    if img:
        im=load(img,sp.get("crop"))
        maxh=H-90-th-140
        sc=min((W-60)/im.width,maxh/im.height); im=im.resize((int(im.width*sc),int(im.height*sc)),Image.LANCZOS)
    total=th+(im.height if im else 0)
    top=max(90,(H-110-total)/2+20)
    d.text((W-60,top),sp["title"],font=ft,fill=ACC if sp.get("acc") else (255,255,255),anchor="ra",**FA)
    yy=top+ft.size*1.55
    for ln in sl:
        d.text((W-60,yy),ln,font=fs,fill=(215,218,225),anchor="ra",**FA); yy+=fs.size*1.6
    if im:
        iy=int(top+th); x=(W-im.width)//2
        m=Image.new("L",im.size,0); ImageDraw.Draw(m).rounded_rectangle([0,0,im.width-1,im.height-1],radius=28,fill=255)
        d.rounded_rectangle([x-3,iy-3,x+im.width+2,iy+im.height+2],radius=30,outline=(70,74,84),width=3)
        c.paste(im,(x,iy),m)
    if s.get("tag"): d.text((W/2,H-80),s["tag"],font=F(POPB,32),fill=(140,145,158),anchor="ma")
    return c
def prompt(s,sp):
    c=bg(s.get("glow",(40,90,160))); d=ImageDraw.Draw(c)
    ft=fitfa(d,sp["title"],BLACK,W-120,76); d.text((W-70,110),sp["title"],font=ft,fill=(255,255,255),anchor="ra",**FA)
    fs=F(SEMI,40); sl=wrapfa(d,sp.get("sub",""),fs,W-150)
    y=110+ft.size*1.5
    for ln in sl: d.text((W-70,y),ln,font=fs,fill=(200,200,205),anchor="ra",**FA); y+=fs.size*1.5
    cy0=y+40
    fp=F(POP,48); txt="“"+sp["prompt"]+"”"; lines=wrapen(d,txt,fp,W-240)
    while len(lines)*fp.size*1.42>H-cy0-300 and fp.size>24:
        fp=F(POP,fp.size-2); lines=wrapen(d,txt,fp,W-240)
    lh=fp.size*1.42; ch=90+len(lines)*lh+50
    cy0=cy0+max(0,(H-200-cy0-ch)/2)
    d.rounded_rectangle([70,cy0,W-70,cy0+ch],radius=34,fill=(28,28,32),outline=(60,60,66),width=2)
    d.text((120,cy0+40),"PROMPT",font=F(POPB,28),fill=tuple(s.get("glow",(40,90,160))) if sum(s.get("glow",(0,0,0)))>300 else ACC)
    yy=cy0+90
    for ln in lines: d.text((120,yy),ln,font=fp,fill=(240,240,242)); yy+=lh
    hint=sp.get("hint","")
    if hint:
        fh=fitfa(d,hint,SEMI,W-160,34); d.text((W/2,H-110),hint,font=fh,fill=(150,150,158),anchor="ma",**FA)
    return c
def endcard(s,sp):
    c=photo_top(load(sp["src"],sp.get("crop")),700); d=ImageDraw.Draw(c)
    f1=fitfa(d,sp["cta1"],BLACK,W-160,72); f2=fitfa(d,sp["cta2"],SEMI,W-180,42)
    y=710; bh=f1.size*1.5+f2.size*1.6+50
    d.rounded_rectangle([70,y,W-70,y+bh],radius=36,fill=(255,255,255))
    d.text((W/2,y+26),sp["cta1"],font=f1,fill=(15,15,18),anchor="ma",**FA)
    d.text((W/2,y+26+f1.size*1.45),sp["cta2"],font=f2,fill=(80,80,86),anchor="ma",**FA)
    y=y+bh+40
    d.text((W/2,y),"دانستنی روز",font=F(BLACK,92),fill=(255,255,255),anchor="ma",**FA)
    cf=F(BLACK,54); cta="فالو کن"
    pw,phh=int(d.textlength(cta,font=cf,**FA)+130),92; px,py=(W-pw)//2,int(y+130)
    d.rounded_rectangle([px,py,px+pw,py+phh],radius=46,fill=GREEN)
    d.text((W/2,py+phh/2-4),cta,font=cf,fill=(0,0,0),anchor="mm",**FA)
    d.text((W/2,py+phh+16),"@danestani.ruzz",font=F(BOLD,40),fill=(170,225,175),anchor="ma")
    return c
KIND=dict(cover=cover,card=card,prompt=prompt,endcard=endcard)
if __name__=="__main__":
    spec=sys.argv[1]; s=json.load(open(spec)); base=os.path.dirname(os.path.abspath(spec)); os.chdir(base)
    os.makedirs("out",exist_ok=True)
    for f in glob.glob("out/*.jpg"): os.remove(f)
    for i,sp in enumerate(s["slides"],1):
        KIND[sp["kind"]](s,sp).save(f"out/slide-{i:02d}.jpg",quality=93)
    fs=sorted(glob.glob("out/*.jpg")); n=len(fs); cols=5
    sheet=Image.new("RGB",(cols*330,((n+cols-1)//cols)*420),"white")
    for k,f in enumerate(fs):
        im=Image.open(f); im.thumbnail((320,410)); sheet.paste(im,(330*(k%cols)+5,420*(k//cols)+5))
    sheet.save("review.png"); print(n,"slides")
