# Akıllı Plaka Bariyer Sistemi — Donanım ve Yazılım Entegrasyon Rehberi

> **Ekip Handoff Dokümanı**  
> **Tarih:** 2 Kasım 2026  
> **Hedef Kitle:** Donanım montajını yapacak, web dashboard'unu bağlayacak ve projeyi birleştirecek ekip arkadaşları.  
> **Temel İlke:** Donanıma enerji vermeden önce elektriksel sınırları doğrulayın. Fiziksel hareketi ancak güvenlik kontrolleri geçtikten sonra etkinleştirin.

---

## 1. Giriş ve Proje Durumu (Handoff Özeti)

Bu proje; araç plakalarını kamera ile okuyan, sunucu tarafında yapay zeka (OCR) ile doğrulayan ve fiziksel bariyeri otomatik olarak yöneten bir **Akıllı Plaka Tanıma ve Bariyer Sistemi** prototipidir.

### Bugüne Kadar Neler Tamamlandı? (Doğrulanmış Yazılım Tabanı)
- **FastAPI Cihaz Adaptörü (`backend/fastapi_app.py`)**: Gerçek kameradan gelen JPEG görüntülerini (`POST /api/device/v1/observations`) hem ham ikili akış (`image/jpeg`) hem çok parçalı form (`multipart/form-data`) olarak kabul eder. Cihaz durum ve hareket olaylarını (`POST /api/device/v1/events`) telemetri olarak kaydeder. Bearer token yetkilendirmesi devrededir.
- **Karar ve Veritabanı Çekirdeği (`backend/store.py`, `backend/domain.py`)**: SQLite üzerinde atomik işlem yönetimi, `(device_id, session_id, request_id)` bazlı tekilleştirme (`duplicate: true`) ve farklı görüntüde `409 Conflict` koruması sağlar. İzinli plaka listesi (`allowed`) ve deneme kayıtları (`device_observations`, `device_events`) kalıcı olarak saklanır.
- **Yapay Zeka / Çevrimdışı OCR Motoru (`backend/ocr.py`)**: Pretrained `cct-s-v2-global-model` ONNX modeli entegre edilmiştir. CPU üzerinde ~6.5 ms gecikmeyle çalışır; karakter dolgu (padding) alanları güven skorundan ayıklanmıştır. Alternatif EasyOCR adaptörü hazırdır. Bounding-box kırpma aracı (`experiments/crop_plate.py`) ve 10 plakalı uçtan uca simülasyon (`experiments/simulate_device.py`) tamamlanmıştır.
- **Web Dashboard Görsel Kabuğu (`web/`)**: Next.js 16 + React 19 + Tailwind CSS + Vitest araç zinciri kurulmuş; 9 birim testi ve Turbopack derlemesi hatasız geçmektedir.
- **54 Otomatik Test**: Backend, OCR ve API mantığını kapsayan 54 birim testi yerelde ve GitHub Actions CI üzerinde %96 kod kapsamıyla (coverage) geçmektedir.

### Ekip Olarak Şimdi Ne Yapılacak? (Kalan İşler)
1. **Donanım / Masaüstü Sorumlusu**: Parçaları breadboard üzerinde birbirine bağlayacak, seviye dönüştürücü dirençleri kuracak, `firmware/esp32_cam/esp32_cam.ino` kodunu karta yükleyecek ve fiziksel prototipi çalıştıracaktır.
2. **Frontend / Dashboard Sorumlusu**: `web/` dizinindeki Next.js arayüzünün veri çekme fonksiyonlarını çalışan FastAPI backend'inin `http://127.0.0.1:8000/api/state` ucuna bağlayacaktır.
3. **Entegrasyon Testi**: Kart masaya konacak, önüne plaka gösterilecek ve servonun bariyeri açıp kapatması uçtan uca test edilecektir.

---

## 2. Donanım Envanteri ve Parça Listesi (BOM)

Masanızda / proje kutunuzda bulunması gereken parçalar şunlardır:

| Parça Adı | Model / Kod | Miktar | Görevi ve Açıklaması | Çalışma Voltajı |
|---|---|:---:|---|:---:|
| **ESP32-CAM Geliştirme Kartı** | AI-Thinker ESP32-CAM | 1 | Ana mikrodenetleyici. Wi-Fi üzerinden sunucuyla haberleşir, GPIO'ları yönetir. | 5V (VCC pini) / 3.3V Dahili Mantık |
| **Kamera Modülü** | OV2640 (2 Megapiksel) | 1 | Kartın üzerindeki sokete şerit kabloyla takılan kamera. Plaka fotoğrafı çeker. | ESP32-CAM dahili besleme |
| **Programlayıcı Adaptör** | FTDI FT232RL veya ESP32-CAM-MB | 1 | Bilgisayarın USB portundan karta kod yüklemeyi ve Seri Port haberleşmesini sağlar. | 5V / 3.3V Jumper |
| **Mikro Servo Motor** | TowerPro SG90 (Mavi) | 1 | Bariyer kolunu fiziksel olarak açıp kapatır (0° kapalı, 90° açık). | 4.8V – 6.0V (Önerilen: 5V Harici) |
| **Ultrasonik Mesafe Sensörü** | HC-SR04 | 1 | Önüne araç yaklaştığında mesafeyi ölçer; çekim ve kapanma kontrolünü tetikler. | **5V VCC** (Echo: 5V Seviye) |
| **Durum LED'leri** | 5mm LED (Yeşil ve Kırmızı) | 1'er adet | Yeşil: İzin verildi (açık). Kırmızı: Ret / Hata / Okunamadı (kapalı). | 2.0V – 3.2V (Dirençle) |
| **LED Akım Sınırlama Dirençleri** | 220Ω veya 330Ω | 2 | LED'lerin fazla akım çekip yanmasını ve GPIO'yu bozmasını engeller. | Pasif |
| **Seviye Dönüştürücü Dirençler** | 1kΩ ve 2kΩ (veya 1kΩ + 2x1kΩ) | 1'er adet | **Hayati:** HC-SR04 5V Echo çıkışını ESP32'nin 3.3V girişine güvenle düşürür. | Pasif voltaj bölücü |
| **Devre Tahtası (Breadboard)** | Standart 400 veya 830 delikli | 1 | Kablo ve parçaları lehim yapmadan birbirine bağlamak için kullanılır. | - |
| **Jumper Kablolar** | Erkek-Erkek, Erkek-Dişi | ~15 adet | Parçalar arası elektriksel bağlantılar için. | - |
| **Harici 5V Güç Kaynağı** | 5V 2A USB Adaptör veya Güç Modülü | 1 | Servo ve kart için temiz, kesintisiz güç sağlar (Brownout önleme). | 5V DC |

---

## 3. Kritik Elektriksel Güvenlik ve Uyumluluk Kuralları

> [!CAUTION]
> **Elektronik parçalar yazılım gibi geri alınamaz!** Yanlış bir voltaj kartı veya sensörü kalıcı olarak yakabilir. Lütfen şu 4 kuralı montaj öncesinde mutlaka okuyun:

### Kural 1: HC-SR04 Echo Seviye Düşürme (5V -> 3.3V Şartı)
- **Tehlike:** Standart HC-SR04 sensörü 5V ile beslenir ve `Echo` pininden **5V sinyal** üretir. ESP32'nin GPIO pinleri en fazla **3.3V** tolere edebilir! 5V doğrudan girerse ESP32 pini kalıcı hasar görür.
- **Çözüm (Basit Voltaj Bölücü Devre):**  
  Sensörün Echo çıkışına iki direnç bağlayarak gerilimi 3.33V'a düşürün:
  ```
  HC-SR04 Echo pini ────[ 1kΩ Direnç ]────┬────> ESP32-CAM GPIO 13
                                          │
                                   [ 2kΩ Direnç ]
                                          │
                                         GND (Toprak)
  ```
  *(Matematiksel kanıt: $V_{out} = 5V \times \frac{2k\Omega}{1k\Omega + 2k\Omega} = 3.33V$)*

### Kural 2: Ortak Toprak (Common Ground) Zorunluluğu
- Eğer servo motor harici bir adaptörden veya pilden besleniyorsa, harici güç kaynağının **GND (eksi)** hattı ile ESP32-CAM'in **GND pini** breadboard üzerinde mutlaka **birbirine bağlanmalıdır**.
- Ortak toprak olmadan sinyal seviyeleri referans alamaz ve servo düzensiz titrer veya hiç çalışmaz.

### Kural 3: Servo Motoru Asla 3.3V Pininden Beslemeyin (Brownout Koruması)
- SG90 servo motor kolu hareket ettirirken anlık olarak 500mA - 1000mA akım çekebilir.
- ESP32-CAM üzerindeki dahili 3.3V regülatör bu akımı taşıyamaz; voltaj anında çöker ve ESP32 `Brownout detector was triggered` hatası vererek kendini sürekli yeniden başlatır.
- Servo motorun kırmızı kablosunu doğrudan **5V güç hattına** bağlayın.

### Kural 4: ESP32-CAM Pin Çakışmalarına Dikkat Edin
- **GPIO 16 ve 17:** Kart üzerindeki 4MB PSRAM (harici bellek) tarafından kullanılır. **Bu pinlere asla kablo bağlamayın!**
- **GPIO 0:** Kart açılırken GND'ye bağlıysa "Kod Yükleme Modu"na girer. Normal çalışmada boş bırakılmalıdır.
- **GPIO 1 ve 3:** Bilgisayarla seri haberleşme (TX/RX) yapar. Başka sensör bağlamayın.

---

## 4. Resmi Pin Bağlantı Matrisi (Pinout)

Tüm donanım bağlantıları aşağıdaki tabloya göre yapılmalıdır:

| ESP32-CAM Pini | Bağlanan Parça / Modül | Parçanın Pini | Sinyal Yönü | Gerilim Seviyesi | Açıklama ve Güvenlik Notu |
|:---:|---|:---:|:---:|:---:|---|
| **5V** | Güç Hattı / Programlayıcı | 5V / VCC | Güç Girişi | 5.0V | Kartın ana güç girişi. |
| **GND** | Tüm Parçalar / Güç Kaynağı | GND | Toprak | 0V | Ortak toprak hattı. |
| **GPIO 14** | SG90 Servo Motor | Sinyal (Turuncu/Sarı) | Çıkış (PWM) | 3.3V | Bariyer kolunu 0°-90° döndürür (50Hz PWM). |
| **GPIO 15** | HC-SR04 Ultrasonik Sensör | Trig | Çıkış | 3.3V | Mesafe ölçümü için 10µs tetikleme darbesi. |
| **GPIO 13** | HC-SR04 Ultrasonik Sensör | Echo (Direnç sonrası) | Giriş | **3.3V (Bölünmüş)** | Echo 5V -> 1kΩ / 2kΩ bölücüden geçip GPIO 13'e girer. |
| **GPIO 12** | Yeşil LED | Anot (+) [Uzun bacak] | Çıkış | 3.3V (220Ω seri) | Plaka izinli (`allow`) olduğunda yanar. |
| **GPIO 2** | Kırmızı LED | Anot (+) [Uzun bacak] | Çıkış | 3.3V (220Ω seri) | Plaka ret (`deny` / `unreadable`) durumunda yanar. |
| **GPIO 33** | Dahili Kart LED'i (Kırmızı) | Dahili | Çıkış | 3.3V | Kart üzerindeki küçük bildirim ışığı (Ters mantık). |
| **GPIO 0** | Programlayıcı / Jumper | GND (Sadece yüklemede) | Giriş | 0V | Kod yüklerken GND'ye takın; çalışma anında sökün. |
| **U0R (GPIO 3)** | Programlayıcı (FTDI) | TXD | Giriş | 3.3V / 5V | Seri yükleme alıcı pini. |
| **U0T (GPIO 1)** | Programlayıcı (FTDI) | RXD | Çıkış | 3.3V | Seri log verici pini. |

---

## 5. Gömülü Yazılım (Firmware) Kurulum ve Yükleme Kılavuzu

Firmware kaynak kodu: [`firmware/esp32_cam/esp32_cam.ino`](file:///Users/omerufuk/Repositories/smart-plate-barrier/firmware/esp32_cam/esp32_cam.ino)

### A. Arduino IDE Ortamının Hazırlanması
1. Bilgisayarınıza [Arduino IDE](https://www.arduino.cc/en/software) (2.x önerilir) kurun.
2. `Dosya` (File) → `Tercihler` (Preferences) açın.
3. `Ek Devre Kartları Yöneticisi URL'leri` alanına şu adresi ekleyin:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. `Araçlar` (Tools) → `Kart` → `Kart Yöneticisi` menüsünden **esp32** araması yapın ve **esp32 by Espressif Systems** paketini kurun.
5. `Araçlar` menüsünden aşağıdaki ayarları seçin:
   - **Kart (Board):** `AI Thinker ESP32-CAM`
   - **CPU Frequency:** `240MHz (WiFi/BT)`
   - **Flash Frequency:** `80MHz`
   - **Flash Mode:** `QIO`
   - **Partition Scheme:** `Huge APP (3MB No OTA/1MB SPIFFS)`
   - **Port:** Programlayıcının bağlı olduğu COM portu (Windows: `COMx`, Mac: `/dev/cu.usbserial-...`)

### B. Kod İçindeki Ayarların Güncellenmesi
[`firmware/esp32_cam/esp32_cam.ino`](file:///Users/omerufuk/Repositories/smart-plate-barrier/firmware/esp32_cam/esp32_cam.ino) dosyasını açın ve en baştaki satırları kendi ortamınıza göre düzenleyin:
```cpp
const char* WIFI_SSID     = "EV_VEYA_OFIS_WIFI_ADINIZ";
const char* WIFI_PASSWORD = "WIFI_PAROLANIZ";

// PC'nizin yerel IP adresi (terminalde 'ifconfig' veya 'ipconfig' ile öğrenin)
const char* SERVER_HOST   = "http://192.168.1.50:8000";
const char* AUTH_TOKEN    = "smart-barrier-device-key-2026";
```

### C. Karta Kod Yükleme Adımları (Flash İşlemi)
1. **ESP32-CAM üzerindeki `GPIO 0` pinini `GND` pinine bir jumper kablo ile bağlayın.** (Bu, kartı Bootloader moduna sokar).
2. FTDI programlayıcıyı bilgisayarın USB portuna takın.
3. Arduino IDE'de **Yükle (Upload)** butonuna basın.
4. Alt panelde `Connecting........_____.....` yazısını gördüğünüzde, ESP32-CAM kartının arkasındaki küçük **RST (Reset)** butonuna 1 saniye basıp bırakın.
5. Yükleme `%100 (Done uploading)` olduğunda:
   - **GPIO 0 ile GND arasındaki kabloyu kesinlikle sökün!**
   - Kart üzerindeki **RST (Reset)** butonuna tekrar basın.
6. Arduino IDE'de `Seri Port Ekranı`nı (Serial Monitor) açın ve baud hızını **115200** yapın.
7. Ekranda Wi-Fi bağlantısının kurulduğunu, kameranın başladığını ve IP adresinin alındığını göreceksiniz.

---

## 6. Web Dashboard Entegrasyonu (Frontend Ekip Arkadaşı İçin)

Dashboard kodu: [`web/`](file:///Users/omerufuk/Repositories/smart-plate-barrier/web)

Arayüzü geliştiren ekip arkadaşımızın dikkat etmesi gereken noktalar:
- **Backend Adresi:** FastAPI sunucumuz yerel ağda varsayılan olarak `http://127.0.0.1:8000` portunda çalışır.
- **CORS Yapılandırması:** Backend, `http://localhost:3000` ve `http://127.0.0.1:3000` adreslerinden gelen tüm isteklere izin verecek şekilde ayarlanmıştır.

### Önemli API Uçları:
1. **Canlı Durumu Okuma (`GET /api/state`)**:
   - Dönen veri:
     ```json
     {
       "mode": "simulation",
       "barrier": "closed", // "closed" veya "open_waiting_clear"
       "allowed_plates": ["06TST02", "34DMO01"],
       "events": [ /* son 50 gözlem ve OCR detayı */ ],
       "actions": [ /* son 20 bariyer eylemi */ ]
     }
     ```
   - Dashboard bileşeni bu endpoint'i düzenli aralıklarla (örneğin her 1 saniyede bir `setInterval` veya SWR/React Query ile) sorgulayarak bariyer animasyonunu ve plaka geçmişini güncelleyebilir.
2. **Manuel Alan Temizleme (`POST /api/demo/clear`)**:
   - Operatör arayüzden "Bariyeri Kapat / Alanı Temizle" butonuna bastığında bu endpoint çağrılır. Bariyer durumu `closed` durumuna geçer.
3. **İzinli Plaka Ekleme/Silme**:
   - Ekleme: `POST /api/plates/add` gövde: `{"plate": "34 ABC 123"}`
   - Silme: `POST /api/plates/remove` gövde: `{"plate": "34 ABC 123"}`

---

## 7. Adım Adım Masaüstü Montaj ve Doğrulama Protokolü

Ekip olarak masaya oturduğunuzda sırasıyla şu 5 adımı uygulayın:

### Adım 1: PC Sunucusunu Başlatın
Terminal açın ve sanal ortamla FastAPI sunucusunu ayağa kaldırın:
```bash
cd /Users/omerufuk/Repositories/smart-plate-barrier
.venv-ocr/bin/uvicorn backend.fastapi_app:app --host 0.0.0.0 --port 8000
```
*(Not: `--host 0.0.0.0`, ESP32'nin yerel ağdan bu sunucuya erişebilmesini sağlar).*

İkinci bir terminalde web arayüzünü başlatın:
```bash
cd /Users/omerufuk/Repositories/smart-plate-barrier/web
npm run dev
```
Tarayıcıda `http://localhost:3000` adresini açın.

### Adım 2: Seri Porttan Kamera Testi Yapın
- Kartı programlayıcı ile takın (GPIO 0 sökülü).
- Arduino Serial Monitor'ü açın (115200 baud).
- Klavyeden `c` harfi yazıp `Enter` tuşuna basın.
- Kartın anında bir kare yakalayıp sunucuya gönderdiğini ve sunucudan gelen JSON yanıtını ekrana bastığını gözlemleyin.

### Adım 3: Mesafe Sensörü ve LED Testi
- Elinizi HC-SR04 sensörünün önüne ~15 cm mesafeye getirin.
- Sensörün araç gelişini algıladığını ve kamerayı otomatik tetiklediğini Serial Monitor'den izleyin.
- Beyaz bir kağıda tükenmez kalemle büyük harflerle **`34 DMO 01`** yazıp kameranın 15 cm önüne tutun:
  - **Beklenen Sonuç:** Yeşil LED yanmalı, Serial Monitor'de `IZIN VERILDI (ALLOW)` yazmalı.
- İzinli olmayan bir yazı gösterin (örn. **`34 XYZ 99`**):
  - **Beklenen Sonuç:** Kırmızı LED yanmalı, Serial Monitor'de `RET (DENY)` yazmalı, bariyer açılmamalıdır.

### Adım 4: Servo Motor Bariyer Testi
- Servo motor sinyal kablosunu GPIO 14'e bağlayın.
- İzinli plaka gösterildiğinde servonun 90 derece kalkarak bariyeri açtığını doğrulayın.
- Elinizi sensörün önünden çekip alanın boşaldığını simüle edin (~30 cm üzeri mesafe).
- 2 saniye sonra servonun tekrar 0 dereceye inerek bariyeri kapattığını doğrulayın.

### Adım 5: Uçtan Uca Doğrulama
- Web Dashboard'u (`http://localhost:3000`) kontrol edin:
  - Okunan plakanın log listesine düştüğünü,
  - Bariyer durumunun "AÇIK" ve ardından "KAPALI" olarak güncellendiğini teyit edin.

---

## 8. Sık Karşılaşılan Sorunlar ve Çözümleri (Troubleshooting)

1. **`Brownout detector was triggered` ve Kartın Sürekli Reset Atması**:
   - **Sebep:** Kart veya servo motor anlık olarak yetersiz voltaj/akım alıyordur.
   - **Çözüm:** Bilgisayarın zayıf bir USB portu yerine güçlü bir USB portu veya harici 5V 2A adaptör kullanın. Programlayıcı üzerindeki 3.3V/5V jumper'ının 5V konumunda olduğundan emin olun.

2. **`Camera init failed with error 0x20001` veya `0x105`**:
   - **Sebep:** Kamera şerit kablosu soketine tam oturmamış veya ters takılmıştır.
   - **Çözüm:** Kartın gücünü kesin. Soketin siyah mandalını nazikçe yukarı kaldırın, altın sarısı pinler karta bakacak şekilde şerit kabloyu dibe kadar itin ve mandalı kapatın.

3. **`HTTP baglanti hatasi: connection refused` (-1)**:
   - **Sebep:** ESP32, PC'deki sunucuya ulaşamıyordur.
   - **Çözüm:** PC ve ESP32'nin aynı Wi-Fi ağına (örneğin aynı modem veya aynı telefon ortak erişim noktasına) bağlı olduğundan emin olun. PC'deki güvenlik duvarının (Firewall) 8000 portunu engellemediğini kontrol edin.

4. **Servo Motor Düzensiz Titriyor ve Isınıyor**:
   - **Sebep:** Ortak toprak (GND) bağlı değildir ya da mekanik sınır (0° veya 90°) zorlanıyordur.
   - **Çözüm:** Harici güç kaynağının GND'sini ESP32 GND'sine bağlayın. Plastik kolu servo kapalı konumdayken takın.

5. **`HTTP 413 Payload Too Large`**:
   - **Sebep:** Yakalanan JPEG fotoğrafı sunucu limiti olan 500 KB'ı aşıyordur.
   - **Çözüm:** `esp32_cam.ino` içinde çözünürlüğü `FRAMESIZE_VGA` veya `FRAMESIZE_CIF` yapın, `jpeg_quality` değerini 12-15 aralığında tutun.

---

## 9. Ekip Dağılımı ve Görev Kontrol Listesi

| Görev Alanı | Yapılacak İş | İlgili Dosyalar | Durum |
|---|---|---|:---:|
| **Donanım & Bench** | Breadboard bağlantılarının şemaya göre kurulması | `docs/donanim-ve-yazilim-entegrasyon-rehberi.md` | Bekliyor |
| **Gömülü Yazılım** | ESP32-CAM'e Wi-Fi ve IP girilerek flash edilmesi | `firmware/esp32_cam/esp32_cam.ino` | Hazır (Flaş bekliyor) |
| **Backend & OCR** | FastAPI ve ONNX model servisinin yerel ağda çalıştırılması | `backend/fastapi_app.py`, `backend/ocr.py` | **Tamamlandı ve Test Edildi** |
| **Web Dashboard** | Next.js arayüzünün `/api/state` endpoint'ine bağlanması | `web/src/` | Hazır (Veri bağlantısı bekliyor) |
| **Fiziksel Kasa / Maket** | Koli/karton veya 3D baskı ile maket bariyer standı | Maket ölçeği | İsteğe bağlı / Planlandı |
