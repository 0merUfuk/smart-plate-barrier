# Yeni Başlayanlar İçin Donanım ve Masaüstü Kurulum Kılavuzu

Bu belge, gömülü sistemler ve donanımla ilk kez çalışan bir yazılımcı için adım adım, güvenli bir rehberdir.

---

## 1. Masanızdaki Parçaları Tanıyalım

Kutunuzda veya masanızda bulunan parçalar şunlardır:

1. **ESP32-CAM Kartı**:
   - Üzerinde küçük bir kamera lensi (şerit kabloyla bağlı) ve metal bir çip (ESP32) bulunan küçük dikdörtgen siyah kart.
   - **Görevi**: Kameradan fotoğraf çeker, yerel Wi-Fi ile PC'ye gönderir ve bariyer durumunu yönetir.
2. **USB-Serial Programlayıcı (FTDI / CH340 / CP2102 modülü)**:
   - Bilgisayarınızın USB portuna takılan, diğer ucunda pinler (GND, TX, RX, VCC vb.) bulunan küçük modül.
   - Bazen ESP32-CAM kartının altına doğrudan takılan bir "alt taban / shield" şeklinde micro-USB girişli bir parça da olabilir.
   - **Görevi**: Bilgisayardan yazdığımız yazılımı (firmware) karta yüklemek.
3. **Mavi Mikro Servo Motor (SG90)**:
   - Üzerinde beyaz plastik bir bariyer kolu takılan küçük mavi plastik kutu. Üç kablosu vardır:
     - Kahverengi: Toprak (GND)
     - Kırmızı: Güç (5V)
     - Turuncu / Sarı: Sinyal (PWM kontrolü)
4. **Ultrasonik Mesafe Sensörü (HC-SR04)**:
   - İki tane yuvarlak metal "göz" gibi görünen sensör. 4 pini vardır: VCC, Trig, Echo, GND.
   - **Görevi**: Yaklaşan aracı ve bariyer altındaki engeli algılamak.
5. **Kırmızı ve Yeşil LED'ler**:
   - İki bacaklı küçük ışıklar. Uzun bacak artı (+ / Anot), kısa bacak eksi (- / Katot).
   - **Görevi**: İzin verildi (Yeşil) veya ret (Kırmızı) durumunu göstermek.

---

## 2. Neden "Hard Blocker" (Engel) Dedik?

Elektronikte yazılımdan farklı olarak **yanlış bir voltaj kartı kalıcı olarak yakabilir**:
- **ESP32-CAM pinleri 3.3V ile çalışır.** Eğer 5V'luk bir sinyal doğrudan bir veri pinine girerse çip yanabilir.
- **Motorlar anlık yüksek akım çeker.** Servo motor dönerken fazla akım çekerse, ESP32 voltajı düşer ("brownout") ve kart kendini sürekli yeniden başlatır.

Bu yüzden donanıma enerji vermeden önce parçaların ne olduğunu anlamak projenin güvenlik kuralıdır.

---

## 3. İlk Adım: Güvenli Şekilde Yazılımı Yükleme (Motor Henüz Bağlı Değil)

Motoru veya sensörleri **henüz bağlamayın**. İlk hedefimiz yalnızca kameranın açılıp bilgisayara görüntü gönderebilmesidir.

### Bağlantı (Yalnızca Programlama):
Programlayıcı ile ESP32-CAM arasında yalnızca 5 kablo gerekir:
- `GND` → `GND`
- `5V` (veya VCC) → `5V`
- `TX` (Programlayıcı) → `U0R` (ESP32-CAM RX pini)
- `RX` (Programlayıcı) → `U0T` (ESP32-CAM TX pini)
- `GPIO 0` (ESP32-CAM) → `GND` *(Bu bağlantı kartı "kod yükleme moduna" sokar. Yükleme bittikten sonra çıkarılır).*

### Yükleme Adımları:
1. Bilgisayarınızda **Arduino IDE** açın.
2. `Araçlar` → `Kart` → `ESP32 Arduino` → **`AI Thinker ESP32-CAM`** seçin.
3. `firmware/esp32_cam/esp32_cam.ino` dosyasını açın.
4. Dosyanın başındaki `WIFI_SSID` ve `WIFI_PASSWORD` kısımlarına ev/ofis Wi-Fi bilgilerinizi yazın.
5. `SERVER_HOST` kısmına bilgisayarınızın yerel IP adresini yazın (Terminalde `ifconfig` veya `ipconfig` ile öğrenilebilir, örn: `http://192.168.1.50:8000`).
6. USB kablosunu bilgisayara takın ve `Yükle` (Upload) butonuna basın.
7. Yükleme tamamlandıktan sonra `GPIO 0` ile `GND` arasındaki kabloyu çıkarın ve kart üzerindeki küçük `RST` (Reset) düğmesine basın.
8. Arduino IDE'de `Seri Port Ekranı`nı (Baud rate: **115200**) açın. Kartın Wi-Fi'ye bağlandığını ve sunucuyla konuştuğunu göreceksiniz.

---

## 4. Bilgisayarda Sunucuyu Çalıştırma

Terminalden şu komutla yeni FastAPI adaptörümüzü başlatın:

```bash
cd /Users/omerufuk/Repositories/smart-plate-barrier
.venv-ocr/bin/uvicorn backend.fastapi_app:app --host 0.0.0.0 --port 8000
```

Artık ESP32-CAM her fotoğraf çektiğinde sunucu görüntüyü OCR ile okuyacak, plakayı SQLite veritabanından denetleyecek ve karta sonucu iletecektir.
