# Sistem Analizi

Akıllı Plaka Tanıma ve Bariyer Sistemi

Sürüm 0.1.0-demo / 11 Ekim 2026

## Amaç kapsam ve mevcut durum

Sistem Analizi, Akıllı Plaka Tanıma ve Bariyer Sistemi için başlangıç gereksinimlerini, bileşen sınırlarını ve kabul ölçütlerini tanımlar. 11 Ekim 2026 sürümü ekip incelemesine açık bir analiz temelidir. Dönem raporundan ayrı tutulur.

Sistem yaklaşan aracı algılamayı, plaka görüntüsünü PC’de işlemeyi, izinli listeyle eşleşmeye göre erişim kararını vermeyi ve uygun fiziksel koşullarda bariyeri yönetmeyi hedefler. Yedi kişilik ekip yazılım ve donanım bileşenlerini birlikte geliştirecek.

### 12 Ekim demo kapsamı

Sentetik OCR gözlemi, gerçek izin kontrolü ve SQLite kayıtları, sanal bariyer, manuel alan boşluğu doğrulaması ve izinli liste yönetimi uygulanmıştır. Yerel Python HTTP adaptörü çalışır. Gerçek OCR ve FastAPI görüntü adaptörü henüz yoktur.

### Varsayımlar ve kapsam sınırları

- Başlangıç için tek erişim noktası ve kontrollü masaüstü prototipi varsayılıyor. Maket ölçeği ekipçe teyit edilecek.
- PC ve cihazın aynı yerel ağda olması hedefleniyor.
- Gerçek otopark işletimi, çoklu şerit ve endüstriyel uygunluk kapsam dışında.
- Gerçek geçiş yönü ve giriş/çıkış sayımı ilk sürüm dışında.
- Kesin kart, bütçe, ders takvimi ve görev atamaları bekliyor.

Doğrulanan ilerleme: 20 Python testi ve 8 sentetik karar senaryosu geçti. Donanım, gerçek OCR, yerel Rust testleri ve uzak CI doğrulanmadı.

## Paydaşlar ve kullanım senaryoları

| Aktör | Gereksinim veya rol |
| --- | --- |
| Sürücü veya maket araç | Yaklaşma, erişim kararı ve geçiş alanı |
| Yönetici | İzinli plaka listesi ve deneme kayıtları |
| Yedi kişilik ekip | Geliştirme, veri toplama, montaj ve doğrulama |
| Öğretim elemanı | Ders kapsamı ve değerlendirme ölçütleri |
| ESP32 ve PC | Görüntü, karar ve durum iletişimi |

### UC01 İzinli erişim

Ön koşul izinli listede plaka bulunması ve görüntünün yeterli güvenle okunmasıdır. Cihaz gözlem üretir, sunucu tam eşleşmeyi değerlendirir. Yeni izin kararı yalnızca kapalı bariyerde açma isteği oluşturur. Bariyer alan boşluğu doğrulanana kadar açık bekler. Demoda cihaz ve görüntü yerine sentetik giriş kullanılır.

### UC02 Ret veya okunamama

Plaka listede değilse ret, güven düşük veya biçim uygun değilse okunamadı sonucu döner. Yeni açma üretilmez. Önceki araç nedeniyle açık olan bariyer bu kararla kapanmaz.

### UC03 Hata veya tekrar yanıt

OCR veya iletişim hatası yeni açma üretmez. Demoda hata yalnızca seçilebilir girdidir. Aynı request_id ile aynı veri yeniden gelirse kayıt ve hareket tekrar edilmez. Farklı verinin aynı kimliği kullanması 409 hatasıdır. Gerçek cihazda eski/tekrar yanıtın reddi ayrıca uygulanacaktır.

### UC04 Liste ve kayıt yönetimi

Yönetici sentetik izinli plaka ekleyip silebilir ve son erişim denemelerini görebilir. Üretim kimlik doğrulaması demo adaptöründe bulunmaz. Gerçek araç geçişiyle ilgili kayıt için ayrıca algılama ve veri modeli gerekecektir.

## Bileşenler ve mimari

Gömülü katman algılama, JPEG çekme, iletişim ve fiziksel durum kontrolünden sorumlu olacak. PC katmanı OCR ve erişim kararını yürütecek. Web arayüzü izinli liste ve kayıt yönetimini sağlayacak. Donanım kontrolü ile OCR kararı ayrı sorumluluklardır.

| Katman | Hedef bileşen | Başlangıç durumu |
| --- | --- | --- |
| Gömülü | ESP32-CAM, sensör ve servo sürücüleri | Rust durum çekirdeği adayı; sürücüler yok |
| Görüntü işleme | OpenCV ve EasyOCR | Planlandı |
| Sunucu | FastAPI ve karar/kayıt çekirdeği | Karar/kayıt mevcut; FastAPI adaptörü planlandı |
| Veritabanı | SQLite | Demoda mevcut |
| Arayüz | HTML CSS JavaScript | Demo kaynakları mevcut |
| Mekanik | 3D baskı kasa ve bariyer | Planlandı |

### Demo veri akışı

Tarayıcı sentetik gözlemi POST /api/demo/scan ile gönderir. Sunucu biçim ve güven kontrolünü yapar, izinli listeyi sorgular, tek işlem içinde gözlem ve sanal durum güncellemesini kaydeder. Arayüz /api/state üzerinden kayıt ve durumu gösterir.

### Hedef donanım veri akışı

Yaklaşma sensörü cihazı tetikler. Cihaz JPEG ve işlem kimliğini PC’ye gönderir. Sunucu görüntüyü okuyup karar döndürür. Cihaz kimlik, geçerlilik süresi ve yerel durum koşullarını denetleyerek hareketi uygular. Alan boşluğu ayrı algılanır. Bu zincir henüz uygulanıp doğrulanmadı.

### Dil ve araç seçimi

Rust öncelikli adaydır. Kartta kamera, Wi-Fi, sensör ve servo birlikte en fazla bir iş günlük denemede doğrulanır. Çözülmemiş sürücü/araç zinciri engeli kalırsa C++ alternatifi kullanılır. Bu karar değişse de API ve durum modeli korunur. Kamera sürücüsü C bileşenidir [S3, S5].

## İşlevsel gereksinimler

Durum alanı tam sistem tamamlanmasını değil, bu sürümdeki kapsamı belirtir. Uygulanan kararlar sentetik gözlemler üzerindedir.

| Kimlik | Gereksinim | Durum |
| --- | --- | --- |
| FR01 | Yaklaşan aracı algılama | Donanımda planlandı |
| FR02 | JPEG çekme ve sunucuya gönderme | Planlandı |
| FR03 | Görüntüden plaka çıkarma | Planlandı |
| FR04 | Biçim ve güven kontrolü | Sentetik girdide uygulandı |
| FR05 | İzinli listeyle tam eşleşme | Uygulandı |
| FR06 | Tekrar istekleri tekilleştirme | Demo sunucusunda uygulandı |
| FR07 | Bariyer ve durum göstergesi | Sanal olarak uygulandı |
| FR08 | İzinli plaka ekleme ve silme | Uygulandı |
| FR09 | Zaman damgalı erişim denemesi kaydı | Uygulandı |
| FR10 | Ret ve hata halinde yeni açma üretmeme | Hata girdileriyle uygulandı |
| FR11 | Alan boşluğunu doğrulayarak kapanma | Demoda manuel |
| FR12 | Gerçek yön ve geçiş tespiti | İlk sürüm dışında |

### Karar kuralları

- Sıra: hata kontrolü, biçim kontrolü, güven kontrolü, tam eşleşme.
- Dört sonuç: allow, deny, unreadable ve error.
- Güven eşiği 0.85 öneridir ve henüz kalibre edilmedi.
- Normalizasyon boşluk ve harf büyüklüğüyle sınırlı. Yaklaşık eşleşme yok.
- Aynı gözlem kimliği farklı veriyle yeniden kullanılamaz.

Plaka biçim deseni demo için yaygın biçimleri yaklaşık kapsar. Eksiksiz ülke standardı doğrulaması değildir. Gerçek veri kapsamı belirlendikten sonra kurallar gözden geçirilecek.

## İşlevsel olmayan gereksinimler ve veri

| Kimlik | Gereksinim | Kabul veya durum |
| --- | --- | --- |
| NFR01 | Hata halinde yeni açma yok | Sentetik hata testleri geçti; gerçek cihaz deneyi bekliyor |
| NFR02 | Tekilleştirme ve kalıcılık | SQLite işlem ve yeniden açma testleri geçti |
| NFR03 | Uçtan uca gecikme | İlk öneri p95 en fazla 5 sn; PC ve koşullar belli olunca teyit edilecek |
| NFR04 | Tekrar üretilebilir deney | Veri bölümü, sürüm, koşul ve örnek sayısı kaydı |
| NFR05 | Veri mahremiyeti | Public örnekler sentetik; gerçek veri izin ve saklama planı bekliyor |
| NFR06 | Kimlik doğrulama | Yerel demo sınırlı; gerçek cihaz/yönetici erişimi için planlandı |
| NFR07 | Bakım ve ekip katkısı | Tek repository, testler, PR incelemesi ve haftalık belge güncellemesi |

### Başlangıç veri modeli

allowed tablosu normalize plaka anahtarını tutar. events tablosu request_id, normalize gözlem yükü, karar yanıtı ve UTC zaman damgasını saklar. settings sanal bariyer durumunu ve ilk kurulum işaretini, actions ise sanal açma/kapatma kaydını tutar.

Demo arayüzü en son 50 gözlem ve 20 sanal hareketi gösterir. Bu ekran sınırı bir saklama politikası değildir. Fiziksel geçiş kaydı, cihaz kimliği, görüntü referansı ve saklama süresi sonraki veri modeli kararlarıdır.

### Ölçüm tanımları

Tam plaka doğruluğu, karakter hata oranı, yanlış kabul ve yanlış ret ayrı raporlanır. İzinli gözlemin okunamadı sonucu yanlış ret hesabında ayrıca açıklanır. Uçtan uca süre gerçek sensör tetiklemesinden karar ve hareket uygulamasına kadar ölçülmelidir. Demo fixture süresi bu ölçümün yerine geçmez.

## Durum modeli ve arayüz sözleşmesi

Başlangıç sanal durumları closed ve open_waiting_clear’dır. Tam cihaz yaşam döngüsü için algılama, görüntü alma, karar bekleme, fiziksel açılma/kapanma ve arıza durumları sonraki firmware tasarımında eklenecek.

| Mevcut durum | Olay | Yeni durum | Sanal hareket |
| --- | --- | --- | --- |
| closed | Yeni allow | open_waiting_clear | open |
| closed | Ret, okunamadı veya hata | closed | none |
| open_waiting_clear | Alan boş doğrulaması | closed | close |
| open_waiting_clear | Ret, hata veya yeni allow | open_waiting_clear | none |
| Her durum | Aynı gözlemin tekrarı | Değişmez | none |

Zamanlayıcıyla kör kapanma uygulanmadı. Alan boşluğu demoda kullanıcı düğmesiyle doğrulanır. Gerçek kapanma için sensör güvenilirliği, mekanik sınırlar ve iletişim hatasında davranış ayrıca test edilecektir.

### Demo HTTP sözleşmesi

- GET /api/health ve /api/state sağlık, kayıt ve durum okur.
- POST /api/demo/scan gözlem alır. request_id, plate, confidence ve isteğe bağlı fault kullanır.
- POST /api/demo/clear manuel alan boşluğu alır.
- POST /api/plates/add ve /api/plates/remove listeyi yönetir.

Yanıt decision, reason, duplicate, barrier, barrier_action, mode ve created_at alanlarını içerir. Mutasyon gövdeleri JSON ve en fazla 8192 bayttır. Aynı kimlikle farklı gözlem 409 üretir. Demo sunucusu yalnızca 127.0.0.1 üzerinde dinler.

Hedef JPEG endpoint’i, cihaz/yönetici kimlik doğrulaması, yanıt geçerlilik süresi ve gerçek zaman aşımı politikası planlandı. Bunlar mevcut demo API’sinin doğrulanmış işlevleri değildir.

## Riskler ve açık kararlar

| Risk | Etki | Önlem veya sonraki adım |
| --- | --- | --- |
| GPIO ve PSRAM çakışması | Kamera veya açılış çalışmayabilir | Kart şemasıyla pin matrisi [S4] |
| 5 V Echo ve güç dalgalanması | Kart hasarı veya yeniden başlama | Seviye uyumu, güç bütçesi ve ölçüm [S8] |
| Tek kare düşük kalite | Yanlış okuma veya okunamama | Kalite kontrolü, koşullu yeniden çekim deneyi |
| Güvensiz kapanma | Araç veya maket engeline çarpma | Alan algılama ve yerel kontrol |
| Eski veya tekrar yanıt | Yanlış fiziksel hareket | Cihaz kimliği, süre sınırı, cihazda tekilleştirme |
| Rust entegrasyon engeli | Takvim kayması | Kısa deneme ve C++ alternatifi |
| Sentetik sonucun yanlış sunumu | Geçersiz başarı iddiası | Tüm çıktılarda demo ve gerçek deney ayrımı |

### Ekipten netleşmesi gereken bilgiler

- Kartın tam modeli ve parça envanteri
- Maket ölçeği, kamera açısı ve gösterim ortamı
- Alan boşluğunu hangi sensör düzeninin doğrulayacağı
- Bütçe, güç kaynağı ve satın alma durumu
- Üye adları, görev sahipleri ve inceleyenler
- Hocanın resmi şablonu, rubriği ve kesin teslim takvimi

Alternatif proje belgesi ortak klasörde erişilebilir değil. Bu analiz yalnızca ana projeyi kapsar. Açık kararlar gereksinim ve test planını değiştirdikçe sürüm notuyla güncellenecek.

## Doğrulama izlenebilirliği ve sonraki adımlar

| Gereksinim | Başlangıç kanıtı | Kalan doğrulama |
| --- | --- | --- |
| FR04–05 | Biçim, güven ve izin testleri | Gerçek OCR üzerinde yeniden test |
| FR06 | Tekrar ve eşzamanlılık testleri | Cihazda eski/tekrar yanıt testi |
| FR07 ve FR11 | Sanal durum ve HTTP testi | Servo ve alan sensörü testi |
| FR08–09 | Liste ve SQLite kalıcılık testi | Yönetici erişimi ve veri saklama |
| FR10 | Sentetik hata girdileri | Gerçek ağ/OCR arızası |
| FR01–03 | Henüz yok | Gerçek kart ve görüntü deneyi |

Test adları ve ayrıntılı eşleme docs/project-spec.json ve tests/test_demo.py içinde bulunur. Kod testleri geliştirme doğrulamasıdır; tam sistem kabulü değildir. Rust testleri yerelde ve uzak CI bu sürümde çalıştırılmadı.

### İlk entegrasyon hedefi

Kart ve güç doğrulandıktan sonra sensör tetiklemesiyle JPEG çekip PC’ye göndermek ilk hedef olacak. Ardından aynı karar çekirdeğine FastAPI ve gerçek OCR eklenir. Fiziksel bariyer hareketi ancak yerel durum ve alan boşluğu davranışı test edildikten sonra bağlanır.

### Kaynaklar

S1  Ana proje sunumu. Ortak Drive PDF, 10 sayfa, 4 Ekim 2026 içerik tarihi. Kapsam ve bileşen önerileri. https://drive.google.com/file/d/1L5Am6SDtG7YU6WwXuPOf-1LHQXYvsT16/view

S2  Rapor örneği. Kullanıcının paylaştığı rapor-ornegi.PDF, 48 sayfa. Bölüm yapısı ve boş süreç formu tasarımı için referans. Örneğin kişi ve sonuçları bu projeye aktarılmadı.

S3  ESP32 kamera sürücüsü. Espressif esp32-camera resmi kaynak ve README. https://github.com/espressif/esp32-camera

S4  ESP32 GPIO kısıtları. Espressif ESP-IDF GPIO belgesi. https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html

S5  Rust ESP-IDF desteği. Güncel esp-rs/esp-idf kaynakları. https://github.com/esp-rs/esp-idf

S6  EasyOCR. JaidedAI resmi kaynakları. https://github.com/JaidedAI/EasyOCR

S7  FastAPI. Resmi başlangıç dokümantasyonu. https://fastapi.tiangolo.com/tutorial/first-steps/

S8  HC SR04 sinyal seviyeleri. Portland State University doğrudan eğitim materyali. Varyant seçimine göre değerlendirilir. https://web.cecs.pdx.edu/~gerry/class/IB/sensors/HC-SR04/

Belge sürümü 0.1.0-demo. Hazırlama tarihi 11 Ekim 2026. Sonraki değişiklikler ortak Drive ve repository durum kaydı birlikte güncellenerek yapılacak.
