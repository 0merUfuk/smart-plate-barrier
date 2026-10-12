# İlk geliştirme işleri

| İş | Kabul ölçütü | Durum |
|---|---|---|
| Ekip bilgisayarında demo provası | Tarayıcıda izin, ret, tekrar ve kapanma akışı | Bekliyor |
| Üye ve görev ataması | Yedi üye, sorumlular ve inceleyenler belli | Bekliyor |
| Kart envanteri | Tam model ve üretici şeması kaydedildi | Bekliyor |
| Güç ve pin doğrulaması | Sensör seviyesi, PSRAM ve güç matrisi | Bekliyor |
| Rust uygulanabilirlik | Kartta JPEG, Wi-Fi, sensör ve PWM | Bekliyor |
| FastAPI görüntü adaptörü | JPEG boyut ve hata kontrolleriyle aynı karar çekirdeği | Bekliyor |
| Gerçek OCR adaptörü | Etiketli görüntülerde metin ve güven çıktısı | Bekliyor |
| Veri kümesi ve bölümler | İzin/lisans, oturumlar, ayrı ayar/test | Bekliyor |
| Alan algılama ve mekanik | Engel varken kapanmama ve servo sınır deneyi | Bekliyor |
| Gerçek cihaz güvenlik sözleşmesi | Kimlik, eski yanıt reddi ve süre sınırı | Bekliyor |
| Yönetici erişimi | Gerçek kullanım için kimlik doğrulama | Bekliyor |
| Dönem ölçümleri | OCR metrikleri, gecikme, güç/enerji | Bekliyor |

Yerel Python testleri geçti. 12 Ekim 2026 tarihinde public repository yayımlandı.
GitHub Actions üzerinde Python 3.10/3.12 kontrolleri ve üç Rust testi geçti.
Kanıt: https://github.com/0merUfuk/smart-plate-barrier/actions/runs/38249748425
Bu sonuçlar gerçek OCR veya fiziksel donanım doğrulaması değildir.
