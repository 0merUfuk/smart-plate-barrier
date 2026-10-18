# Teknik kararlar ve durum

11 Ekim 2026, sürüm 0.1.0-demo. Çalışma kararları ekip incelemesine açıktır.

| Kimlik | Çalışma kararı | Durum ve gerekçe |
|---|---|---|
| ADR-01 | Tek repository | Kullanıcı tercihi; kod, firmware, donanım ve deneyler birlikte |
| ADR-02 | Donanımsız demo | Uygulandı; kart ve montaj doğrulanmadı, yarın için güvenilir prova |
| ADR-03 | Demo HTTP adaptörü Python stdlib | Uygulandı; kurulum bağımlılığı yok. FastAPI hedef adaptör |
| ADR-04 | SQLite | Demoda uygulandı; yerel tek istasyon için basit kalıcı kayıt |
| ADR-05 | Rust öncelikli, C++ alternatif | Aday; kartta bir iş günlük uygulanabilirlik deneyi bekliyor |
| ADR-06 | Tam eşleşme, düşük güvende açmama | Uygulandı; yanlış yetkilendirmeyi azaltmayı amaçlar |
| ADR-07 | Alan boşluğu doğrulamasıyla kapanma | Demoda manuel; fiziksel sensör ve cihaz kontrolü tasarlanacak |
| ADR-08 | request_id ile tekilleştirme | Demo sunucusunda uygulandı; cihaz tarafı henüz yok |
| ADR-09 | web/ içinde Next.js + React + TypeScript + Tailwind CSS | 18 Ekim 2026: hedef frontend yığını ilke olarak onaylandı; mevcut vanilla HTML/CSS/JS demo henüz taşınmadı, geçiş uygulaması ayrıca yetkilendirilecek. Mevcut Python backend ve karar/kayıt çekirdeği korunur; FastAPI planlanan API framework'üdür. Next.js yalnızca frontend katmanıdır; Route Handlers/API Routes ile yinelenen iş API'si, ayrı veritabanı erişimi, OCR veya cihaz/bariyer kontrolü eklenmez. Mevcut genel mimari ve ana dizinler korunur. |

Kaynak PDF'nin tek kare ve 1/0 yanıt yaklaşımı genişletildi. Tek kare her koşulda
hatasız OCR sağlamaz. API kararları allow/deny/unreadable/error olarak ayrılır.
İzin kararı fiziksel geçiş kanıtı sayılmaz. Gerçek yön/giriş-çıkış takibi bu ilk
sürümün kapsamı dışında, ayrıca sensör tasarımı gerektirir.

Donanım seçimi, bütçe, kesin pinler, görüntü çözünürlüğü, gerçek OCR doğruluğu,
işlem gecikmesi ve güven eşiği ölçümleri henüz karara bağlanmadı.
