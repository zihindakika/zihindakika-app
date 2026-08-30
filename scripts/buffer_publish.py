from pathlib import Path
import os, json, datetime, urllib.request

API = 'https://api.buffer.com'
KEY = os.getenv('BUFFER_API_KEY', '').strip()
STATE = Path('data/latest.json')

def load_state():
    return json.loads(STATE.read_text(encoding='utf-8'))

def save_state(d):
    d['updated_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    STATE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')

def gql(query, variables=None):
    req = urllib.request.Request(
        API,
        data=json.dumps({'query': query, 'variables': variables or {}}).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + KEY},
    )
    with urllib.request.urlopen(req, timeout=90) as r:
        out = json.loads(r.read().decode())
    if out.get('errors'):
        raise RuntimeError(out['errors'])
    return out['data']

def main():
    d = load_state()
    try:
        if not KEY:
            raise RuntimeError('BUFFER_API_KEY tanımlı değil')
        orgs = gql('query { account { organizations { id name } } }')['account']['organizations']
        if not orgs:
            raise RuntimeError('Buffer organizasyonu bulunamadı')
        channels = gql(
            'query($id:OrganizationId!){ channels(input:{organizationId:$id}) { id name service } }',
            {'id': orgs[0]['id']},
        )['channels']
        wanted = [c for c in channels if str(c.get('service', '')).lower() in {'instagram', 'tiktok', 'youtube'}]
        if not wanted:
            raise RuntimeError('Instagram/TikTok/YouTube kanalı bulunamadı')

        video = d['video']
        caption = d.get('caption') or (d.get('title', 'ZihinDakika') + '\n\n#zihindakika')
        slot = d.get('slot')
        now = datetime.datetime.now(datetime.timezone.utc)
        mode, due = 'shareNow', None
        if slot in {'17:30', '20:30'}:
            tr = now + datetime.timedelta(hours=3)
            hh, mm = map(int, slot.split(':'))
            target = tr.replace(hour=hh, minute=mm, second=0, microsecond=0) - datetime.timedelta(hours=3)
            if target > now + datetime.timedelta(seconds=75):
                mode, due = 'customScheduled', target.isoformat().replace('+00:00', 'Z')

        mutation = 'mutation($input:CreatePostInput!){createPost(input:$input){... on PostActionSuccess{post{id status dueAt channelService}} ... on MutationError{message}}}'
        results = []
        for c in wanted:
            service = str(c['service']).lower()
            inp = {
                'text': caption,
                'channelId': c['id'],
                'schedulingType': 'automatic',
                'mode': mode,
                'assets': [{'video': {'url': video, 'metadata': {'thumbnailOffset': 2000, 'title': d.get('title', 'ZihinDakika')}}}],
                'aiAssisted': True,
                'needsApproval': False,
                'source': 'zihindakika-v3',
            }
            if due:
                inp['dueAt'] = due
            if service == 'instagram':
                inp['metadata'] = {'instagram': {'type': 'reel', 'shouldShareToFeed': True, 'isAiGenerated': True}}
            elif service == 'tiktok':
                inp['metadata'] = {'tiktok': {'isAiGenerated': True}}
            elif service == 'youtube':
                inp['metadata'] = {'youtube': {
                    'title': d.get('title', 'ZihinDakika')[:100],
                    'categoryId': '27',
                    'privacy': 'public',
                    'madeForKids': False,
                    'embeddable': True,
                    'notifySubscribers': True,
                    'isAiGenerated': True,
                }}
            try:
                res = gql(mutation, {'input': inp})['createPost']
                typed_error = isinstance(res, dict) and bool(res.get('message')) and not res.get('post')
                results.append({'channel': service, 'name': c.get('name'), 'result': res, 'ok': not typed_error})
            except Exception as e:
                results.append({'channel': service, 'name': c.get('name'), 'error': str(e), 'ok': False})

        d['buffer_results'] = results
        ok = [r for r in results if r.get('ok')]
        if not ok:
            raise RuntimeError('Hiçbir Buffer kanalı başarıyla oluşturulamadı')
        d['status'] = f'Buffer gönderimi oluşturuldu • {len(ok)}/{len(results)} kanal'
        save_state(d)
        print(json.dumps(results, ensure_ascii=False))
        return 0
    except Exception as e:
        d['status'] = 'Onaylandı • Buffer gönderimi başarısız'
        d['buffer_error'] = str(e)[:500]
        save_state(d)
        print('BUFFER_ERROR:', str(e))
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
