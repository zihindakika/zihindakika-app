from pathlib import Path
import os,json,datetime,urllib.request
KEY=os.getenv('BUFFER_API_KEY','').strip()
if not KEY: raise SystemExit('BUFFER_API_KEY tanımlı değil; yayın yapılmadı.')
API='https://api.buffer.com'
def gql(q):
    req=urllib.request.Request(API,data=json.dumps({'query':q}).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+KEY})
    with urllib.request.urlopen(req,timeout=90) as r: out=json.loads(r.read().decode())
    if out.get('errors'): raise RuntimeError(out['errors'])
    return out['data']
orgs=gql('query { account { organizations { id name } } }')['account']['organizations']
if not orgs: raise SystemExit('Buffer organizasyonu bulunamadı.')
org=orgs[0]['id']
channels=gql('query { channels(input: { organizationId: "'+org+'" }) { id name service } }')['channels']
wanted=[c for c in channels if str(c.get('service','')).lower() in {'instagram','tiktok','youtube'}]
if not wanted: raise SystemExit('Instagram/TikTok/YouTube kanalı bulunamadı.')
d=json.loads(Path('data/latest.json').read_text(encoding='utf-8'));repo=os.getenv('GITHUB_REPOSITORY','zihindakika/zihindakika-app');owner,name=repo.split('/',1)
video=f'https://{owner}.github.io/{name}/media/latest.mp4?v={d.get("generated_at","")}'
caption=d.get('title','ZihinDakika')+'\n\n'+d.get('narration','')+'\n\n#kişiselgelişim #psikoloji #üretkenlik #zihindakika'
slot=d.get('slot');now=datetime.datetime.now(datetime.timezone.utc);mode='shareNow';due=None
if slot in {'17:30','20:30'}:
    tr=now+datetime.timedelta(hours=3);hh,mm=map(int,slot.split(':'));target=tr.replace(hour=hh,minute=mm,second=0,microsecond=0)-datetime.timedelta(hours=3)
    if target>now+datetime.timedelta(minutes=1):mode='customScheduled';due=target.isoformat().replace('+00:00','Z')
results=[]
for c in wanted:
    esc=lambda s:s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n')
    fields=['text: "'+esc(caption)+'"','channelId: "'+c['id']+'"','schedulingType: automatic','mode: '+mode,'aiAssisted: true','assets: [{ video: { url: "'+esc(video)+'" } }]']
    if due: fields.append('dueAt: "'+due+'"')
    q='mutation { createPost(input: { '+ ' '.join(fields) +' }) { ... on PostActionSuccess { post { id status dueAt } } ... on MutationError { message } } }'
    try:results.append({'channel':c['service'],'result':gql(q)['createPost']})
    except Exception as e:results.append({'channel':c['service'],'error':str(e)})
d['buffer_results']=results;d['status']='Buffer gönderimi tamamlandı';Path('data/latest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
