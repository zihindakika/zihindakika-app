# ZihinDakika V3

Telefon odaklı, sıfır maliyetli kısa video üretim ve onay sistemi.

- Arayüz: GitHub Pages PWA
- İçerik: Qwen2.5 3B (yerel GitHub Actions runner üzerinde Ollama), kalite kontrol + güvenli fallback
- Ses: FreyaTTS-small 48 kHz birincil, Piper Türkçe güvenli fallback
- Video: 1080×1920 H.264/AAC, dinamik altyazı ve koyu/neon ZihinDakika görsel dili
- Yayın: yalnızca açık `Paylaş` onayından sonra Buffer API
- Video depolama: `media` dalında yalnız son video tutulur; ana dal ikili video geçmişiyle şişmez
