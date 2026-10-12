# 12 Ekim 2026 demo kılavuzu

## Sunum öncesi

- Python 3.10+ kontrol et. Repository dizininden README komutuyla başlat.
- http://127.0.0.1:8080 aç. İnternet gerekmiyor.
- Yeni prova veritabanı kullan. Sentetik 34 DMO 01 / 06 TST 02 izinlidir.
- Sunum PDF'ini indir ve çevrimdışı açılabildiğini kontrol et.
- Ekranda simulation açıklamasının görüldüğünden emin ol.

## Yaklaşık üç dakikalık akış

1. Başlangıç açıklaması: Bugün karar/kayıt yazılımı ve sanal bariyer gösteriliyor.
2. 34 DMO 01, 0.96 ile izin ver. Bariyer açık ve alan boşluğu bekliyor.
3. Tekrar isteğini göster. Yeni kayıt/hareket yok.
4. Alanı boş doğrula. Kapandıktan sonra tekrar isteği yeniden açmaz.
5. İzinsiz, düşük güven ve iki hata girdisini göster.
6. İzinli listeyi değiştir ve kararın değiştiğini göster.
7. 20 test ve 8 fixture sonucunu terminalde göster. Bunların OCR metriği olmadığını belirt.
8. Kart doğrulaması, gerçek OCR ve mekanik entegrasyonun sonraki hedef olduğunu açıkla.

## Kurtarma

Port doluysa --port 8081. DB kilitliyse aynı dosyayı kullanan ikinci sunucuyu kapat.
Sayfa eski görünüyorsa yenile. Hata/ret açık bariyeri kapatmaz; alanı boş doğrula.
İzinli demo plakasını sildiysen yeniden ekle veya farklı prova DB dosyası seç.
Donanım veya OCR çalışıyor iddiasını bu demodan çıkarma.
