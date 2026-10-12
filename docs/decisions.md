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

Kaynak PDF'nin tek kare ve 1/0 yanıt yaklaşımı genişletildi. Tek kare her koşulda
hatasız OCR sağlamaz. API kararları allow/deny/unreadable/error olarak ayrılır.
İzin kararı fiziksel geçiş kanıtı sayılmaz. Gerçek yön/giriş-çıkış takibi bu ilk
sürümün kapsamı dışında, ayrıca sensör tasarımı gerektirir.

Donanım seçimi, bütçe, kesin pinler, görüntü çözünürlüğü, gerçek OCR doğruluğu,
işlem gecikmesi ve güven eşiği ölçümleri henüz karara bağlanmadı.
