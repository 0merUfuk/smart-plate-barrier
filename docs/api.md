# Demo API sözleşmesi

Yerel taban adresi http://127.0.0.1:8080. Mutasyonlar application/json ister.
Maksimum gövde 8192 bayt. Üretim/cihaz API'si değildir; kimlik doğrulama henüz yok.

| Yöntem | Yol | İşlev |
|---|---|---|
| GET | /api/health | Sürüm ve simulation modu |
| GET | /api/state | İzinli plakalar, sanal durum, son 50 gözlem ve 20 hareket |
| POST | /api/demo/scan | Sentetik OCR gözlemi |
| POST | /api/demo/clear | Manuel alan boşluğu doğrulaması |
| POST | /api/plates/add | Sentetik izinli plaka ekleme |
| POST | /api/plates/remove | İzinli plaka silme |

```json
{"request_id":"demo-001","plate":"34 DMO 01","confidence":0.96,"fault":"none"}
```

request_id: 1-64 ASCII harf/rakam/alt çizgi/tire. confidence: sonlu sayı [0,1].
fault: none / ocr_error / network_timeout. Yanıt decision, reason, barrier,
barrier_action, duplicate, mode ve UTC created_at alanlarını taşır.
barrier: closed / open_waiting_clear. barrier_action: open / close / none.

Aynı request_id ve normalize edilmiş aynı veri yeniden gelirse duplicate=true,
barrier_action=none döner ve kayıt eklenmez. Aynı kimlik farklı veriyle kullanılırsa
409 döner. Yanıt geçmiş karar ve güncel sanal durumu içerir; yeni donanım komutu değildir.

400: bozuk veri. 403: yabancı tarayıcı Origin. 404: yol yok. 409: kimlik çakışması.
413: boyut sınırı. 415: içerik türü. Tarihler UTC, arayüz tarayıcının saat dilimidir.

Gelecek görüntü endpoint'i: gerçek JPEG ve cihaz kimliği alacak; boyut sınırı,
kimlik doğrulama, süre sınırı ve OCR hata ayrımı gerekecek. Bu endpoint uygulanmadı.
