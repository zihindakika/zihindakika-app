from pathlib import Path
import json,os,datetime
p=Path('data/latest.json');d=json.loads(p.read_text(encoding='utf-8'))
cmd=os.getenv('ZD_COMMAND','').strip();expected=os.getenv('ZD_EXPECTED_ID','').strip()
if expected and d.get('id')!=expected:
 print('stale');raise SystemExit(0)
if cmd=='APPROVE':d['decision']='approved';d['status']='Onaylandı • yayın hazırlanıyor';result='approved'
elif cmd=='REJECT':d['decision']='rejected';d['status']='Paylaşılmadı';result='rejected'
else:result='ignored'
d['updated_at']=datetime.datetime.now(datetime.timezone.utc).isoformat();p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print(result)
