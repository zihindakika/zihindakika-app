from pathlib import Path
import os,sys
sys.path.insert(0,os.environ.get('FREYA_DIR','/tmp/FreyaTTS'))
from freyatts import FreyaTTS
text=Path('build/narration.txt').read_text(encoding='utf-8').strip()
if not text:raise SystemExit('empty narration')
model=FreyaTTS.from_pretrained('freyavoice/freya-tts',device='cpu')
wav=model.synthesize(text,steps=32)
model.save_wav(wav,'build/voice_raw.wav')
print('FreyaTTS complete',len(wav))
