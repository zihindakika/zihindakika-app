from pathlib import Path
import json,os,datetime
p=Path('data/latest.json');d=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {};cmd=os.getenv('ZD_COMMAND','')
if cmd=='APPROVE':d['decision']='approved';d['status']='Onaylandı • yayınlanıyor'
elif cmd=='REJECT':d['decision']='rejected';d['status']='Paylaşılmadı'
d['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
