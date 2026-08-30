from pathlib import Path
import json, os, random, datetime, urllib.request
FALLBACK=[
('Motivasyon Beklemek Neden Hata?','Başlamak için motivasyon beklemek iyi bir plan gibi görünür, ama motivasyon gün boyunca değişir. Daha güvenilir olan şey başlangıcı küçültmektir. Yapacağın işi beş dakikalık bir adıma indir. Masaya otur, dosyayı aç ve yalnızca ilk parçayı yap. Beynin büyük bir göreve değil, küçük bir başlangıca daha az direnç gösterir. Çoğu zaman hareket ettikten sonra devam etmek kolaylaşır. Kısacası hedefin her gün çok istekli olmak değil, başlamak için gereken eşiği düşürmek olsun. Motivasyonu bekleme; başlamayı kolaylaştıran bir sistem kur.'),
('Karar Yorgunluğu Gününü Nasıl Tüketir?','Sabah ne giyeceğinden hangi işe önce başlayacağına kadar onlarca küçük karar verirsin. Tek tek önemsiz görünseler de gün ilerledikçe seçim yapmak zorlaşabilir. Bu yüzden bazı kararları önceden vermek işe yarar. Örneğin çalışma saatini, ilk görevi veya mola düzenini bir gece önce belirleyebilirsin. Böylece önemli konular için daha fazla zihinsel alan bırakırsın. Amaç hayatı tamamen otomatikleştirmek değil; gereksiz seçimleri azaltmaktır. Enerjini küçük kararlara değil, gerçekten düşünmen gereken konulara sakla.'),
('İki Dakikalık Başlangıç Neden İşe Yarar?','Ertelediğin bir iş gözünde büyüdüğünde, beynin tamamını bitirmen gerekiyormuş gibi davranır. Oysa ilk hedef yalnızca iki dakika olabilir. Spor yapacaksan kıyafetini giy. Ders çalışacaksan kitabı aç ve ilk paragrafı oku. Bir proje yapacaksan dosyayı oluştur. Bu küçük hareket işi bitirmez ama başlangıç sürtünmesini azaltır. Başladıktan sonra devam edip etmemeye yeniden karar verebilirsin. Buradaki fikir kendini kandırmak değil; büyük bir görevi, beynin kabul edeceği kadar küçük bir giriş kapısına çevirmektir.')]
def ask(topic):
    prompt=f'Türkçe, 95-120 kelimelik özgün kısa video anlatımı yaz. Konu: {topic}. İlk cümle güçlü merak kancası olsun. Sade, kanıta uygun ve uygulanabilir anlat. Tıbbi teşhis, mucize vaat, finansal vaat kullanma. Tek paragraf; başlık, emoji ve hashtag yok.'
    payload=json.dumps({'model':'qwen2.5:1.5b','prompt':prompt,'stream':False}).encode()
    try:
        req=urllib.request.Request('http://127.0.0.1:11434/api/generate',data=payload,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=90) as r:
            out=json.loads(r.read().decode())['response'].strip()
        if 70 <= len(out.split()) <= 160:return out
    except Exception:pass
    return None
title=random.choice([x[0] for x in FALLBACK]); fallback=dict(FALLBACK)[title]; narration=ask(title) or fallback
now=datetime.datetime.now(datetime.timezone.utc); slot=os.getenv('ZD_SLOT','auto')
if slot=='auto':slot='17:30' if now.hour < 15 else '20:30'
Path('build').mkdir(exist_ok=True);Path('build/narration.txt').write_text(narration,encoding='utf-8')
Path('build/meta.json').write_text(json.dumps({'title':title,'narration':narration,'slot':slot,'generated_at':now.isoformat()},ensure_ascii=False,indent=2),encoding='utf-8')
