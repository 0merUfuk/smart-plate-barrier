# Akıllı Plaka Tanıma ve Bariyer Sistemi

Veri Bilimi dersi için yedi kişilik ekip projesi.
Sistem; araç plakalarını kamera ile okuyan, sunucu tarafında yapay zeka (OCR) ile doğrulayan ve fiziksel bariyeri otomatik olarak yöneten prototiptir.

> [!IMPORTANT]
> **Ekip Handoff & Entegrasyon Rehberi:**
> Projenin donanım montajını yapacak, ESP32-CAM'e kod yükleyecek ve Next.js dashboard'u bağlayacak ekip arkadaşlarımız için eksiksiz adım adım rehber hazırlandı:
> 📖 **[Donanım ve Yazılım Entegrasyon Rehberi](docs/donanim-ve-yazilim-entegrasyon-rehberi.md)** (Parça listesi, 3.3V/5V voltaj bölücü devresi, pin matrisi ve test adımları).

---

## Sistem Mimarisi ve İki Çalışma Modu

1. **Tam Entegre Mod (FastAPI + FastPlateOCR ONNX + ESP32-CAM + Web Dashboard)**:
   - Gömülü istemci (ESP32-CAM) OV2640 kamerasından JPEG çeker, HTTP POST ile sunucuya iletir.
   - PC sunucusu (`backend/fastapi_app.py`) `cct-s-v2-global-model` ONNX modelini (~6.5 ms) çalıştırır.
   - İzinli plaka kontrolü (`backend/store.py`) tam eşleşmeyle bariyer açma/kapama ve telemetri olaylarını yönetir.
   - Web arayüzü (`web/`) canlı sistem durumunu ve geçmişi gösterir.
2. **Hızlı Simülasyon / Prova Modu (`backend/server.py`)**:
   - Bağımlılıksız Python standart kütüphanesi ile `http://127.0.0.1:8080` adresinde sentetik arayüz çalışır.

---

## Hızlı Başlangıç

### Mod A: Tam Entegre Cihaz & OCR Sunucusu
```bash
# 1. Sanal ortamı etkinleştirin ve FastAPI sunucusunu başlatın
.venv-ocr/bin/uvicorn backend.fastapi_app:app --host 0.0.0.0 --port 8000

# 2. Ayrı bir terminalde Web Dashboard'u başlatın
cd web && npm run dev
# Tarayıcıda: http://localhost:3000

# 3. 10 Plakalı Uçtan Uca Simülasyonu Çalıştırın
.venv-ocr/bin/python -m experiments.simulate_device
```

### Mod B: Bağımlılıksız Yerel Demo Sunucusu
```bash
python3 -m backend.server
# Tarayıcıda: http://127.0.0.1:8080
```

---

## Doğrulama ve Testler

```bash
# 1. Standart Python birim testleri (54 test)
python3 -m unittest discover -s tests -v

# 2. OCR ve FastAPI testleri (Sanal ortamda tüm testler)
.venv-ocr/bin/coverage run -m unittest discover -s tests && .venv-ocr/bin/coverage report -m

# 3. Web Dashboard testleri ve derlemesi
cd web && npm test && npm run lint && npm run typecheck && npm run build
```

- **54 Python birim testi** (%96 kod kapsamıyla hatasız geçmektedir).
- **9 Vitest arayüz testi** (0 lint uyarısı, 0 tip hatası).
- GitHub Actions CI üzerinde Python 3.10, Python 3.12 ve Rust kontrolleri doğrulanmıştır.

---

## Repository Düzeni

| Klasör | İçerik |
|---|---|
| `backend/` | Karar çekirdeği (`domain.py`), SQLite deposu (`store.py`), FastAPI adaptörü (`fastapi_app.py`) ve OCR arayüzü (`ocr.py`) |
| `firmware/` | ESP32-CAM tam entegre Arduino kodu (`firmware/esp32_cam/esp32_cam.ino`) ve Rust çekirdeği |
| `web/` | Next.js 16 + React 19 + Tailwind CSS Web Dashboard arayüzü |
| `experiments/` | Bounding-box kırpıcı (`crop_plate.py`), örnek üretici ve 10 plakalı simülasyon |
| `hardware/` | Elektriksel doğrulama notları ve güvenlik sınırları |
| `docs/` | Entegrasyon rehberi, API sözleşmesi (`api.md`), masaüstü rehberi (`bench-guide.md`) ve teknik kararlar |
| `tests/` | 54 adet otomatik birim ve entegrasyon testi |

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
