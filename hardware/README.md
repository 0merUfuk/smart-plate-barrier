# Donanım doğrulama planı

Önerilen bileşenler: ESP32-CAM, HC-SR04, SG90, iki LED ve uygun dirençler,
besleme, programlama adaptörü ve 3D baskı kasa. Satın alma/çalışma durumu bilinmiyor.

Kaynak PDF'deki GPIO12/13/14/16/15 tablosu **onaylanmış bağlantı planı değildir**.
Kartın tam modeli, kamera pinleri, PSRAM, microSD ve açılış pinleri birlikte incelenmeli.
GPIO16 bellekle çakışabilir. GPIO12/15 açılış seviyeleri dikkate alınmalı.
Standart 5 V HC-SR04 Echo çıkışı doğrudan 3.3 V GPIO'ya bağlanmamalı.
Varyant föyünü kontrol et ve uygun seviye düşürme kullan.
Servo beslemesini kaynak kapasitesi, ortak toprak ve gerilim düşmesi için doğrula.

## Montaj öncesi kayıt

| Kontrol | Kanıt | Durum |
|---|---|---|
| Kart modeli ve revizyonu | Fotoğraf + üretici şeması | Bekliyor |
| Kamera ve PSRAM | JPEG örneği + seri çıktı | Bekliyor |
| Güç bütçesi | Ölçülen akım + besleme kapasitesi | Bekliyor |
| HC-SR04 sinyal seviyesi | Varyant föyü + ölçüm | Bekliyor |
| Pin çakışmaları | Kamera/SD/PSRAM/açılış matrisi | Bekliyor |
| Güvenli kapanma | Alan algılama testi | Bekliyor |
| Mekanik sınırlar | Servo açı sınırı ve yük deneyi | Bekliyor |

Bu sürüm gerçek otopark kullanımına uygunluk iddiası taşımaz.
