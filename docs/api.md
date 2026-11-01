# API sözleşmesi

Yerel taban adresi `http://127.0.0.1:8080` (FastAPI adaptöründe `http://127.0.0.1:8000`).

Sistem iki uç kümesini destekler:
1. Geriye dönük uyumlu simülasyon ve dashboard demo uçları.
2. Kimlik doğrulamalı gerçek cihaz (ESP32 / gömülü istemci) uçları (`/api/device/v1/`).

---

## 1. Demo uçları (Simülasyon ve tarayıcı)

Maksimum gövde 8192 bayt. Yerel demo tarayıcısı içindir; üretim veya cihaz yetkilendirmesi değildir.

| Yöntem | Yol | İşlev |
|---|---|---|
| GET | `/api/health` | Sürüm ve çalışma modu |
| GET | `/api/state` | İzinli plakalar, sanal durum, son 50 gözlem ve 20 hareket |
| POST | `/api/demo/scan` | Sentetik OCR gözlemi |
| POST | `/api/demo/clear` | Manuel alan boşluğu doğrulaması |
| POST | `/api/plates/add` | Sentetik izinli plaka ekleme |
| POST | `/api/plates/remove` | İzinli plaka silme |

### İstek örneği (POST /api/demo/scan)

```json
{"request_id":"demo-001","plate":"34 DMO 01","confidence":0.96,"fault":"none"}
```

- `request_id`: 1-64 ASCII harf/rakam/alt çizgi/tire.
- `confidence`: sonlu sayı [0,1].
- `fault`: `none` / `ocr_error` / `network_timeout`.
- Yanıt: `decision`, `reason`, `barrier`, `barrier_action`, `duplicate`, `mode`, `created_at`.
- Tekilleştirme: Aynı `request_id` ve normalize edilmiş aynı veri `duplicate=true` döner. Aynı kimlik farklı veriyle 409 Conflict döner.

---

## 2. Kimlik doğrulamalı cihaz adaptörü (v1)

Gerçek kamera ve donanım istemcisi için uygulanmış resmi sözleşmedir.

### Yetkilendirme
Cihaz her istekte `Authorization: Bearer <DEVICE_AUTH_TOKEN>` veya `X-Device-Token: <TOKEN>` başlığı sağlamalıdır. Geçersiz veya eksik belirteç 401 Unauthorized üretir.

### POST /api/device/v1/observations

Gerçek JPEG görüntüsünü ve gözlem üstverisini alır, sunucuda OCR (`fast-plate-ocr` / ONNX) çalıştırır, izinli listeyle tam eşleşmeyi değerlendirir ve sonucu döndürür.

Cihaz belleğini ve akışını kolaylaştırmak için iki taşıma biçimi desteklenir:

#### Biçim A: Ham JPEG akışı (Önerilen gömülü format)
- `Content-Type`: `image/jpeg`
- Başlıklar:
  - `X-Device-Id`: Cihaz kimliği (örn. `esp32-barrier-01`, 1-64 karakter `[A-Za-z0-9_-]`)
  - `X-Session-Id`: Açılış oturum kimliği (her yeniden başlatmada değişir)
  - `X-Request-Id`: Monotonik istek/sıra kimliği
  - `X-Deadline-Ms` (İsteğe bağlı): Cihaz tarafı zaman aşımı süresi
  - `Authorization`: `Bearer <token>`
- Gövde: Ham JPEG ikili verisi (maksimum 512.000 bayt / 500 KB).

#### Biçim B: Çok parçalı form (Multipart Form)
- `Content-Type`: `multipart/form-data`
- Alanlar:
  - `metadata`: JSON dizesi (`{"device_id":"...", "session_id":"...", "request_id":"...", "roi":[xmin,ymin,xmax,ymax]}`)
  - `image`: JPEG dosya verisi

#### Karar mantığı
1. Görüntü boyutu ve kod çözümü denetlenir (bozuk/boş veriye `error`).
2. OCR çalıştırılır; karakter güven ortalaması hesaplanır (dolgu karakterleri güven skoruna dahil edilmez).
3. Biçim denetimi (`PLATE` regex) ve güven eşiği (`CONFIDENCE_THRESHOLD = 0.85`) uygulanır.
4. Geçerli biçim ve yüksek güvende SQLite `allowed` tablosunda tam eşleşme aranır.
5. Sonuç: `allow` (`exact_match`), `deny` (`not_in_allowlist`), `unreadable` veya `error`.
   Sunucu asla motor eylem komutu (`barrier_action`) dayatmaz; kararı ve sebebi döner.

#### Tekilleştirme ve çakışma (Idempotency)
- Aynı `(device_id, session_id, request_id)` ve aynı görüntü hash'i (`image_sha256`) yeniden gelirse mevcut karar `duplicate: true` olarak döner.
- Aynı kimlik üçlüsüyle farklı bir görüntü hash'i gelirse sunucu **409 Conflict** yanıtı verir.

#### Yanıt şeması (200 OK)
```json
{
  "protocol_version": "1.0",
  "device_id": "esp32-barrier-01",
  "session_id": "boot-20261101-01",
  "request_id": "req-00042",
  "decision": "allow",
  "reason": "exact_match",
  "plate": "34DMO01",
  "confidence": 0.942,
  "duplicate": false,
  "server_time": "2026-11-01T15:30:00.123Z",
  "ocr": {
    "engine": "fast-plate-ocr",
    "model": "cct-s-v2-global-model",
    "latency_ms": 7.4,
    "raw_text": "34DMO01",
    "country_hint": null
  }
}
```

---

### POST /api/device/v1/events

Bariyer donanımının hareket tamamlama, alan algılama veya arıza telemetrisini kaydeder.

- `Content-Type`: `application/json`
- `Authorization`: `Bearer <token>`

#### İstek gövdesi
```json
{
  "device_id": "esp32-barrier-01",
  "session_id": "boot-20261101-01",
  "event_id": "evt-00109",
  "event_type": "motion_completed",
  "barrier_state": "open_waiting_clear",
  "details": {
    "movement": "open",
    "duration_ms": 1150
  }
}
```

- `event_id` tekilleştirilir; aynı `event_id` tekrar gelirse `duplicate: true` döner ve mükerrer kayıt engellenir.

---

## 3. Durum kodları

- `200 OK`: İşlem başarılı veya tekil tekrar yanıtı.
- `400 Bad Request`: Eksik başlık, geçersiz kimlik biçimi veya bozuk görüntü/üstveri.
- `401 Unauthorized`: Eksik veya geçersiz cihaz belirteci.
- `403 Forbidden`: Demo uçlarında yabancı tarayıcı `Origin` erişimi.
- `404 Not Found`: Tanımsız uç.
- `409 Conflict`: Aynı işlem kimliğinin farklı veri/görüntüyle kullanımı.
- `413 Payload Too Large`: İzin verilen boyuttan büyük gövde (demo için >8 KB, JPEG için >500 KB).
- `415 Unsupported Media Type`: Desteklenmeyen `Content-Type`.
