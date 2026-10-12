# Akıllı Plaka Tanıma ve Bariyer Sistemi

Veri Bilimi dersi için yedi kişilik ekip projesi. İlk sürüm: `0.1.0-demo`.
12 Ekim 2026 sunumu için yerel, donanımsız başlangıç demosu.

**Bu sürüm sentetik plaka metni ve güven skoru kullanır. Gerçek OCR, kamera,
ESP32 bağlantısı veya fiziksel servo kontrolü içermez.** İzin kontrolü, SQLite
kayıtları, tekrar istek yönetimi ve sanal bariyer durumları çalışır.

## Hızlı başlangıç

Python 3.10 veya daha yenisi yeterlidir. Demo ek paket, internet veya model indirmez.

```bash
cd smart-plate-barrier
python3 -m backend.server
```

Windows'ta gerekirse `python3` yerine `py` kullan. Tarayıcıda
http://127.0.0.1:8080 aç. Port doluysa `--port 8081` ekle.
Kapatmak için terminalde Ctrl+C. Kayıtlar `data/demo.sqlite3` içinde kalır.
Temiz prova için mevcut kayıtlarını koruyarak yeni DB seç:
`python3 -m backend.server --db data/rehearsal.sqlite3`.

## Gösterim sırası

1. İzinli `34 DMO 01` ve güven `0.96` gönder. Sanal bariyer açılır.
2. Aynı isteği tekrar gönder. Yeni kayıt ve yeni hareket üretilmez.
3. Alanı boş doğrula. Sanal bariyer kapanır.
4. Aynı eski isteği tekrar gönder. Bariyer yeniden açılmaz.
5. İzinsiz plaka, düşük güven, OCR hatası ve ağ hatası senaryolarını göster.
6. Yeni sentetik izinli plaka ekle, kontrol et, sil ve yeniden kontrol et.

Hata seçenekleri yazılımsal girdidir; gerçek OCR veya ağ arızası oluşturmaz.
Kayıtlar erişim denemesidir. Aracın gerçekleşen giriş/çıkışı kaydedilmiş sayılmaz.
UI alan boşluğunu yalnızca demoda manuel doğrular.

## Doğrulama

```bash
python3 -m unittest discover -s tests -v
python3 -m experiments.evaluate_decisions
python3 -m compileall -q backend experiments tests
```

20 Python testi ve 8 sentetik karar senaryosu bu ortamda geçti.
Bu sayı OCR doğruluğunu veya donanım güvenliğini ölçmez.
Rust çekirdeği için üç test tanımlı; yerelde Rust araç zinciri bulunmadığından
çalıştırılmadı. GitHub Actions yapılandırması hazır, uzak CI henüz çalışmadı.

## Repository düzeni

| Klasör | İçerik |
|---|---|
| backend | Python karar/kayıt çekirdeği ve yerel HTTP demo adaptörü |
| web | Türkçe demo arayüzü, bağımlılıksız HTML/CSS/JS |
| firmware | Rust durum çekirdeği ve ESP32 entegrasyon planı |
| hardware | Elektriksel ve mekanik doğrulama listesi |
| experiments | Sentetik karar deneyleri ve gerçek OCR deney planı |
| docs | Sistem analizi, rapor kaynakları, kararlar ve demo kılavuzu |
| tests | Karar, eşzamanlılık, kalıcılık ve HTTP testleri |

## Mimari kararlar

Hedef mimari: ESP32-CAM, Python FastAPI + OpenCV/EasyOCR, SQLite ve web arayüzü.
Bu demo yalnızca standart Python HTTP adaptörünü çalıştırır. Ağır OCR bağımlılıkları
ve FastAPI yarınki başlangıç demosu için zorunlu değildir. Sonraki adım aynı karar
çekirdeğine FastAPI/görüntü alma adaptörü eklemektir; henüz uygulanmadı.

Rust öncelikli firmware adayı, C++ alternatifidir. Kart üzerinde JPEG, Wi-Fi,
sensör ve servo deneyi yapılmadan dil kararı nihai değildir.
GPIO tablosu ve güç tasarımı onaylanmış sayılmaz. Ayrıntı: `docs/decisions.md`.
İlk OCR eşiği 0.85 öneridir; gerçek veriyle kalibrasyon bekliyor.
Demo plaka deseni yaygın Türkçe plaka biçimlerini yaklaşık doğrular, hukuki
veya kapsamlı plaka standardı doğrulaması değildir.

## Ortak çalışma

Güncel rapor ve analiz belgeleri ortak Drive'da, kod/deney kaynakları bu repository'de.
Bir alandaki değişiklik diğer çıktılara yansıtılmalı. `docs/project-spec.json`
başlangıç kapsamını ve durum ayrımını tutar. `CONTRIBUTING.md` katkı sürecini açıklar.
Ekip bilgileri ortak Drive’daki rapora eklendi. Öğrenci numaraları public repository’ye alınmaz. Görev atamaları, kesin bütçe ve dönem teslim takvimi ekipçe tamamlanacak.
MIT lisansı ilk kod sürümüne uygulanır; ekip ve üçüncü taraf katkıları ayrıca gözden geçirilir.

## Paylaşılan çıktılar

- [Proje Raporu](https://docs.google.com/document/d/1vDKvaRxzL0q3-bQG_iXnJojBNwFH-yydQoRMU0lB3nU/edit)
- [Sistem Analizi](https://docs.google.com/document/d/1-xp9nqTSedWo9novYjrRBgL_kVeg9aOZ7jUhLM4iOPA/edit)
- [12 Ekim demo sunumu](https://drive.google.com/file/d/19Ne6TYf3Gz2fMCGPafVnCDD43lOg3x3b/view)

Belgelerin erişimi ortak Drive paylaşımına bağlıdır. Bu bağlantılar belgeleri public yapmaz.

Yerel HTTP adaptöründe üretim kimlik doğrulaması yoktur. Varsayılan bağlantı yalnızca
127.0.0.1'dir. Bu sunucuyu internete açma veya gerçek bariyere bağlama.
