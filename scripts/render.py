from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import json,subprocess,textwrap,re,math,random,datetime
W,H=1080,1920;BUILD=Path('build');DATA=Path('data');meta=json.loads((BUILD/'meta.json').read_text(encoding='utf-8'));text=meta['narration'];title=meta['title'];hook=meta.get('hook','')
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf';FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def probe(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(p)],text=True).strip())
def wrap(draw,s,font,maxw):
 words=s.split();lines=[];cur=''
 for w in words:
  test=(cur+' '+w).strip()
  if draw.textbbox((0,0),test,font=font)[2]<=maxw:cur=test
  else:
   if cur:lines.append(cur)
   cur=w
 if cur:lines.append(cur)
 return lines
def scene(i,body):
 img=Image.new('RGB',(W,H),(7,9,13));px=img.load()
 top=(8,17,27);bot=(5,9,14)
 for y in range(H):
  q=y/(H-1);c=tuple(int(top[k]*(1-q)+bot[k]*q) for k in range(3));ImageDraw.Draw(img).line((0,y,W,y),fill=c)
 glow=Image.new('RGBA',(W,H),(0,0,0,0));gd=ImageDraw.Draw(glow);gd.ellipse((610,-130,1180,440),fill=(84,227,255,42));gd.ellipse((-330,1250,500,2080),fill=(50,94,255,28));glow=glow.filter(ImageFilter.GaussianBlur(80));img=Image.alpha_composite(img.convert('RGBA'),glow).convert('RGB');d=ImageDraw.Draw(img,'RGBA')
 d.rounded_rectangle((56,60,1024,1860),radius=54,outline=(84,227,255,55),width=3);d.text((82,104),'ZİHİNDAKİKA',font=ImageFont.truetype(FB,42),fill=(84,227,255,255));d.text((82,160),meta.get('category','Zihin'),font=ImageFont.truetype(FR,25),fill=(142,160,181,230))
 tf=ImageFont.truetype(FB,60 if len(title)<48 else 50);y=330
 for line in wrap(d,title,tf,900):d.text((82,y),line,font=tf,fill=(246,249,253,255));y+=74
 d.rounded_rectangle((82,y+34,262,y+39),radius=2,fill=(84,227,255,220));bf=ImageFont.truetype(FB,42 if i==0 else 47);y=max(y+125,760)
 copy=hook if i==0 else (' '.join(body.split()[:18]) + ('…' if len(body.split())>18 else ''))
 for line in wrap(d,copy,bf if i else ImageFont.truetype(FR,42),900):
  d.text((82,y),line,font=bf if i else ImageFont.truetype(FR,42),fill=(220,230,239,245));y+=62
  if y>1420:break
 d.text((82,1700),f'{i+1:02}/05',font=ImageFont.truetype(FB,27),fill=(84,227,255,210));d.line((160,1718,960,1718),fill=(45,62,80,210),width=4);d.line((160,1718,160+int(800*(i+1)/5),1718),fill=(84,227,255,230),width=4)
 # deterministic subtle particles
 random.seed(i+91)
 for _ in range(28):
  x=random.randint(70,1010);yy=random.randint(210,1640);r=random.randint(1,3);d.ellipse((x-r,yy-r,x+r,yy+r),fill=(84,227,255,random.randint(20,65)))
 return img

duration=probe(BUILD/'voice_mastered.wav');sent=[s.strip() for s in re.split(r'(?<=[.!?])\s+',text) if s.strip()]
if len(sent)<5:
 words=text.split();step=max(1,math.ceil(len(words)/5));sent=[' '.join(words[i:i+step]) for i in range(0,len(words),step)]
groups=[];n=max(1,math.ceil(len(sent)/4));groups=[hook]+[' '.join(sent[i:i+n]) for i in range(0,len(sent),n)];groups=(groups+['']*5)[:5]
sc=BUILD/'scenes';sc.mkdir(parents=True,exist_ok=True)
for i,b in enumerate(groups):scene(i,b).save(sc/f'{i}.png',optimize=True)
per_scene=duration/5;lines=[]
for i in range(5):lines += [f"file 'scenes/{i}.png'",f'duration {per_scene:.3f}']
lines += ["file 'scenes/4.png'"];(BUILD/'scenes.txt').write_text('\n'.join(lines),encoding='utf-8')
# subtitle chunks 4-7 words, duration proportional to chunk length
words=text.split();chunks=[];i=0
while i<len(words):
 size=5 if len(words)-i>10 else min(7,len(words)-i);chunks.append(' '.join(words[i:i+size]));i+=size
weights=[max(1,len(c.split())) for c in chunks];total=sum(weights);starts=[];cur=0.0
for w in weights:starts.append((cur,cur+duration*w/total));cur+=duration*w/total
def ats(s):
 cs=int(round(s*100));h=cs//360000;cs%=360000;m=cs//6000;cs%=6000;sec=cs//100;cc=cs%100;return f'{h}:{m:02}:{sec:02}.{cc:02}'
def assesc(s):return s.replace('\\','\\\\').replace('{','\\{').replace('}','\\}')
ass="""[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\nScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: Sub,DejaVu Sans,68,&H00FFFFFF,&H00FFFFFF,&H00070B12,&H90070B12,-1,0,0,0,100,100,0,0,3,2,0,2,80,80,300,1\n\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"""
for c,(a,b) in zip(chunks,starts):ass+=f'Dialogue: 0,{ats(a)},{ats(b)},Sub,,0,0,0,,{assesc(c)}\n'
(BUILD/'subs.ass').write_text(ass,encoding='utf-8')
Path('media').mkdir(exist_ok=True)
vf="scale=1120:1992,crop=1080:1920:x='20+12*sin(t*0.33)':y='36+10*cos(t*0.27)',fps=30,ass=build/subs.ass"
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(BUILD/'scenes.txt'),'-i',str(BUILD/'voice_mastered.wav'),'-vf',vf,'-c:v','libx264','-preset','medium','-crf','21','-profile:v','high','-level','4.1','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-shortest','-movflags','+faststart','media/latest.mp4'],check=True)
final_dur=probe('media/latest.mp4');now=datetime.datetime.now(datetime.timezone.utc).isoformat();video='https://raw.githubusercontent.com/zihindakika/zihindakika-app/media/latest.mp4'
latest={**meta,'status':'Video hazır • önizle ve karar ver','video':video,'decision':'pending','duration_seconds':round(final_dur,2),'voice_engine':Path(BUILD/'voice_engine.txt').read_text(encoding='utf-8').strip(),'render_version':'V3.0','updated_at':now}
DATA.mkdir(exist_ok=True);(DATA/'latest.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'duration':final_dur,'video':video,'voice':latest['voice_engine']},ensure_ascii=False))
