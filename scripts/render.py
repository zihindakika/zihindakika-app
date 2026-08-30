from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,subprocess,textwrap,re,math
W,H=1080,1920; meta=json.loads(Path('build/meta.json').read_text(encoding='utf-8')); text=meta['narration']; title=meta['title']
FB='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; FR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def probe(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',p],text=True).strip())
duration=probe('build/voice.wav'); sentences=[s.strip() for s in re.split(r'(?<=[.!?])\s+',text) if s.strip()]
if len(sentences)<4:
    w=text.split();step=max(1,math.ceil(len(w)/4));sentences=[' '.join(w[i:i+step]) for i in range(0,len(w),step)]
n=max(1,math.ceil(len(sentences)/4)); groups=[' '.join(sentences[i:i+n]) for i in range(0,len(sentences),n)];groups=(groups+['']*4)[:4]
Path('build/scenes').mkdir(parents=True,exist_ok=True)
for i,body in enumerate(groups):
    img=Image.new('RGB',(W,H),(7,17,31));d=ImageDraw.Draw(img,'RGBA')
    for y in range(H):
        q=y/H;col=(int(7+5*q),int(17+20*q),int(31+35*q));d.line((0,y,W,y),fill=col)
    d.ellipse((650,-80,1150,420),fill=(39,213,255,32));d.ellipse((-250,1250,500,2000),fill=(70,60,150,40));d.rounded_rectangle((70,90,1010,1830),radius=48,outline=(39,213,255,80),width=3)
    d.text((90,135),'ZİHİNDAKİKA',font=ImageFont.truetype(FB,48),fill=(39,213,255,255));y=330;hf=ImageFont.truetype(FB,62 if len(title)<38 else 52)
    for line in textwrap.wrap(title,width=26):d.text((90,y),line,font=hf,fill=(242,250,255,255));y+=78
    y=max(y+90,760);bf=ImageFont.truetype(FR,44)
    for line in textwrap.wrap(body,width=35):
        d.text((90,y),line,font=bf,fill=(218,237,248,235));y+=60
        if y>1570:break
    d.text((90,1710),'Motivasyon değil. Sistem.',font=ImageFont.truetype(FB,38),fill=(39,213,255,235));img.save(f'build/scenes/{i}.jpg',quality=92)
scene_d=max(1,duration/4); lines=[]
for i in range(4):lines += [f"file 'scenes/{i}.jpg'",f'duration {scene_d:.3f}']
lines += ["file 'scenes/3.jpg'"];Path('build/scenes.txt').write_text('\n'.join(lines),encoding='utf-8')
chunks=[]
for s in sentences:chunks.extend(textwrap.wrap(s,width=42))
if not chunks:chunks=[text]
per=duration/len(chunks)
def ts(sec):
    ms=int(round(sec*1000));h=ms//3600000;ms%=3600000;m=ms//60000;ms%=60000;s=ms//1000;ms%=1000;return f'{h:02}:{m:02}:{s:02},{ms:03}'
srt=[]
for i,c in enumerate(chunks,1):srt += [str(i),f'{ts((i-1)*per)} --> {ts(min(duration,i*per))}',c,'']
Path('build/subs.srt').write_text('\n'.join(srt),encoding='utf-8');Path('media').mkdir(exist_ok=True)
vf="scale=1080:1920,fps=30,subtitles=build/subs.srt:force_style='FontName=DejaVu Sans,FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00101010,BorderStyle=1,Outline=2,Shadow=1,Alignment=2,MarginV=110'"
subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i','build/scenes.txt','-i','build/voice.wav','-vf',vf,'-c:v','libx264','-preset','medium','-crf','27','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-shortest','-movflags','+faststart','media/latest.mp4'],check=True)
latest={'title':title,'status':'Video hazır • önizle ve karar ver','video':'./media/latest.mp4','decision':'pending','slot':meta['slot'],'narration':text,'generated_at':meta['generated_at']}
Path('data').mkdir(exist_ok=True);Path('data/latest.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf-8')
