from pathlib import Path
import datetime,json,os,random,re,urllib.request,hashlib
BUILD=Path('build');DATA=Path('data');BUILD.mkdir(exist_ok=True);DATA.mkdir(exist_ok=True)
MODEL=os.getenv('ZD_LLM_MODEL','qwen2.5:3b')
SEEDS={'Davranış Bilimi':['başlangıç sürtünmesi','seçim mimarisi','alışkanlık döngüsü','ortamın davranışa etkisi','küçük taahhütler','dikkat kalıntısı'],'Üretkenlik':['tek görev','zaman bloklama','enerji yönetimi','odak ritüeli','görev küçültme','öncelik filtresi'],'Psikoloji':['karar yorgunluğu','negatiflik yanlılığı','çerçeveleme etkisi','zirve-son kuralı','kayıptan kaçınma','alışkanlık ve kimlik'],'İlginç Bilgiler':['beynin tahmin sistemi','uykunun öğrenmedeki rolü','müziğin zaman algısı','hafıza ve bağlam','mikro molalar','merak boşluğu']}
FALLBACKS=[
('Davranış Bilimi','Başlamayı Kolaylaştıran 20 Saniye Kuralı','Bir işi sürekli erteliyorsan sorun her zaman motivasyon olmayabilir; bazen başlangıç çok fazla sürtünme yaratır. Yapmak istediğin davranışın ilk adımını yaklaşık yirmi saniye kolaylaştırmayı dene. Akşamdan çalışma dosyanı açık bırakmak, spor kıyafetini görünür yere koymak veya okuyacağın kitabı masaya hazırlamak buna örnek. Tersi de işe yarar: azaltmak istediğin davranışı birkaç adım zorlaştır. Telefonu başka odaya bırakmak gibi. Küçük çevre düzenlemeleri iradeyi sihirli biçimde artırmaz; yalnızca doğru davranışa başlamayı daha zahmetsiz hale getirir.'),
('Üretkenlik','Tek Görev Neden Daha Hızlı Hissettirir?','Aynı anda birkaç işi yürütmek hızlı görünür, ama zihnin çoğu zaman görevler arasında geçiş yapar. Her geçişte önceki işten kalan küçük bir dikkat izi yeni göreve taşınabilir. Bu yüzden yirmi dakikalık tek görev bloğu bazen bir saatlik dağınık çalışmadan daha temiz hissettirir. Denemek için tek bir hedef seç, gereksiz sekmeleri kapat ve bitiş noktasını önceden belirle. Süre dolunca kısa bir mola ver. Amaç bütün günü kusursuz odakla geçirmek değil; önemli işleri yaparken geçiş sayısını azaltmaktır.'),
('Psikoloji','Karar Yorgunluğu Gününü Nasıl Tüketir?','Sabah ne giyeceğinden hangi işe önce başlayacağına kadar onlarca küçük karar verirsin. Tek tek önemsiz görünseler de gün ilerledikçe seçim yapmak zorlaşabilir. Bu yüzden bazı kararları önceden vermek işe yarar. Örneğin çalışma saatini, ilk görevi veya mola düzenini bir gece önce belirleyebilirsin. Böylece önemli konular için daha fazla zihinsel alan bırakırsın. Amaç hayatı tamamen otomatikleştirmek değil; gereksiz seçimleri azaltmaktır. Enerjini küçük kararlara değil, gerçekten düşünmen gereken konulara sakla.'),
('Üretkenlik','Motivasyon Beklemek Neden Hata?','Başlamak için motivasyon beklemek iyi bir plan gibi görünür, ama motivasyon gün boyunca değişir. Daha güvenilir olan şey başlangıcı küçültmektir. Yapacağın işi beş dakikalık bir adıma indir. Masaya otur, dosyayı aç ve yalnızca ilk parçayı yap. Büyük bir göreve başlamak zor gelirken küçük bir giriş adımı daha az direnç yaratabilir. Çoğu zaman hareket ettikten sonra devam etmek kolaylaşır. Hedefin her gün çok istekli olmak değil; başlamak için gereken eşiği düşürmek olsun. Motivasyonu beklemek yerine başlamayı kolaylaştıran bir sistem kur.'),
('İlginç Bilgiler','Merak Boşluğu Neden Aklında Kalır?','Bir bilgi eksik bırakıldığında zihnin onu tamamlamak istemesi tesadüf değildir. Bildiğin şeyle bilmek istediğin şey arasında küçük bir boşluk oluştuğunda merak artabilir. Bu yüzden iyi bir anlatım doğrudan cevabı vermek yerine önce doğru soruyu kurar. Ders çalışırken de aynı fikri kullanabilirsin: başlığı okumak yerine kendine önce burada neyi açıklamaya çalışıyor diye sor. Sonra cevabı metinde ara. Bu yöntem her şeyi otomatik olarak öğretmez, ama pasif okumayı aktif aramaya dönüştürür ve dikkatin için net bir hedef oluşturur.'),
('Psikoloji','Negatif Bir Yorum Neden Daha Ağır Gelir?','On iyi yorumun yanında tek bir olumsuz yorum varsa zihnin bazen ona daha fazla takılabilir. İnsanlar olumsuz bilgiyi tehdit açısından daha önemli değerlendirmeye eğilim gösterebilir. Bu, her eleştiriyi görmezden gelmen gerektiği anlamına gelmez. Daha iyi yöntem, yorumu kanıt gibi incelemektir: somut mu, tekrarlanıyor mu, değiştirebileceğin bir davranış söylüyor mu? Cevap evetse kullan; yalnızca kaba veya belirsizse ağırlığını azalt. Bir yorumun güçlü hissettirmesi, onun mutlaka en doğru veri olduğu anlamına gelmez.')]
def history():
 p=DATA/'history.json'
 try:return json.loads(p.read_text(encoding='utf-8')).get('titles',[])[-50:]
 except:return []
def clean(s):return re.sub(r'\s+',' ',str(s)).strip().replace('“','').replace('”','')
def ask(category,seed,recent):
 prompt=f"""ZihinDakika adlı yüz göstermeyen kısa video hesabı için Türkçe içerik üret.\nKategori: {category}. Çekirdek fikir: {seed}.\nSon başlıklar (tekrar etme): {', '.join(recent[-20:]) or 'yok'}.\nSadece geçerli JSON döndür: {{"title":"...","narration":"...","caption":"..."}}\nKurallar: title 4-9 kelime. narration 90-112 Türkçe kelime ve 35-50 saniyelik doğal ritim; ilk cümle merak kancası, ortada tek ana fikir, sonda uygulanabilir tek küçük çıkarım. Sade, özgün ve temkinli dil. Uydurma araştırma veya sayı verme. Tıbbi teşhis/tedavi, finansal vaat, mucize, manipülatif korku veya kesin sonuç kullanma. Emoji ve hashtag narration içinde olmasın. caption 260 karakteri geçmesin ve 3-5 alakalı hashtag ile bitsin."""
 payload=json.dumps({'model':MODEL,'prompt':prompt,'stream':False,'format':'json','options':{'temperature':0.72,'top_p':0.9,'repeat_penalty':1.08}}).encode()
 req=urllib.request.Request('http://127.0.0.1:11434/api/generate',data=payload,headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=180) as r:return json.loads(json.loads(r.read().decode())['response'])
def validate(o,recent):
 try:title,narr,cap=clean(o['title']),clean(o['narration']),clean(o.get('caption',''))
 except:return None
 if not 84<=len(narr.split())<=122:return None
 if not 10<=len(title)<=78:return None
 if title.casefold() in {x.casefold() for x in recent[-35:]}:return None
 bad=['garanti','mucize','tedavi eder','teşhis koy','kesin çözüm','zengin ol','%100']
 if any(x in narr.casefold() for x in bad):return None
 if not cap:cap=f'{title} — Bugün deneyebileceğin küçük bir fikir. #zihindakika #üretkenlik #psikoloji'
 return title,narr,cap
def fallback(recent):
 pool=[x for x in FALLBACKS if x[1].casefold() not in {r.casefold() for r in recent[-30:]}] or FALLBACKS
 cat,title,narr=random.choice(pool)
 if len(narr.split())<88:
  narr += ' Bunu denemek için bugün yalnızca tek bir küçük değişiklik seç ve günün sonunda işe yarayıp yaramadığını gözlemle. Sonucu değil, başlangıcı kolaylaştırmaya odaklan.'
 tags={'Davranış Bilimi':'#davranışbilimi','Üretkenlik':'#üretkenlik','Psikoloji':'#psikoloji','İlginç Bilgiler':'#bilgi'}
 return cat,title,narr,f'{title} — Bugün deneyebileceğin küçük bir zihinsel araç. #zihindakika {tags[cat]} #kişiselgelişim','fallback'
def main():
 recent=history();cat=random.choice(list(SEEDS));seed=random.choice(SEEDS[cat]);src='ollama'
 try:
  parsed=validate(ask(cat,seed,recent),recent)
  if not parsed:raise ValueError('quality')
  title,narr,cap=parsed
 except Exception as e:cat,title,narr,cap,src=fallback(recent);print('fallback',type(e).__name__)
 now=datetime.datetime.now(datetime.timezone.utc);slot=os.getenv('ZD_SLOT','extra');hook=re.split(r'(?<=[.!?])\s+',narr)[0].strip();cid=hashlib.sha256((title+now.isoformat()).encode()).hexdigest()[:12]
 meta={'id':cid,'title':title,'hook':hook,'narration':narr,'caption':cap,'category':cat,'slot':slot,'generated_at':now.isoformat(),'source':src,'model':MODEL}
 (BUILD/'narration.txt').write_text(narr,encoding='utf-8');(BUILD/'meta.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
 (DATA/'history.json').write_text(json.dumps({'titles':(recent+[title])[-50:],'updated_at':now.isoformat()},ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'id':cid,'title':title,'words':len(narr.split()),'slot':slot,'source':src},ensure_ascii=False))
if __name__=='__main__':main()
