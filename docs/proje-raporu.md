# Proje Raporu

Akıllı Plaka Tanıma ve Bariyer Sistemi

Sürüm 0.1.0-demo / 11 Ekim 2026

## Özet ve raporun kullanımı

Bu proje, yaklaşan aracı algılayıp plaka görüntüsünü işleyen ve izinli plaka eşleşmesine göre bariyer erişimini yöneten bir eğitim prototipi geliştirmeyi amaçlıyor. Yedi kişilik ekip, yazılım, gömülü sistemler ve mekanik tasarımı birlikte ele alacak.

11 Ekim 2026 başlangıç sürümünde yerel yazılım demosu hazırlandı. Demo sentetik plaka metni ve güven skoru kullanıyor. İzin kontrolü, kalıcı kayıt ve sanal bariyer durumları çalışıyor. Gerçek görüntüden OCR, ESP32 haberleşmesi, fiziksel servo hareketi ve kasa montajı doğrulanmadı.

Bu belge 8–10 haftalık geliştirme boyunca doldurulacak rapor taslağıdır. Plan, uygulama ve ölçüm birbirinden ayrılır. Sonuç tablolarına yalnızca tekrar üretilebilir deneylerden sonra sayı girilir. Köşeli parantezli alanlar ekip tarafından doldurulacaktır.

### İçerik

- 1 Giriş ve problem tanımı
- 2 Takım ve proje organizasyonu
- 3 Literatür taraması ve teknik konumlandırma
- 4 Veri ve yöntem
- 5 Sonuçlar ve değerlendirme
- 6 Proje yönetimi ve çalışma takvimi
- 7 Elektriksel ve mekanik ekipmanlar
- 8 Etik toplumsal etki ve sürdürülebilirlik
- 9 Bireysel öz değerlendirmeler
- 10 Kaynakça ve ekler

Sistem Analizi ayrı bir belge olarak gereksinimleri ve kabul ölçütlerini tanımlar. Bu rapor süreç, yöntem, deney ve ekip katkılarının dönem boyunca biriken kaydıdır.

## 1 Giriş ve problem tanımı

Bir bariyer erişim noktasında araçların izinli olup olmadığını değerlendirmek için algılama, görüntü işleme ve fiziksel kontrol arasında tutarlı bir veri akışı gerekir. Projemiz bu akışı kontrollü bir eğitim ortamında göstermeyi ve görüntü koşullarının karar başarısına etkisini incelemeyi hedefliyor.

### Amaç ve kapsam

Hedef mimari ESP32-CAM, HC-SR04, SG90, durum LED’leri, PC üzerinde Python FastAPI ve OpenCV/EasyOCR, SQLite ve web yönetim arayüzünden oluşuyor. PLA ile üretilecek kasa bir çalışma önerisidir. Kart varyantı, güç kaynağı ve mekanik ölçüler henüz kesinleşmedi.

Yarınki gösterim donanımsız simülasyondur. Demo için bir PC, Python 3.10 veya sonrası ve tarayıcı yeterlidir. Demo yerel çalışır, internetten model indirmez. Sentetik OCR gözlemini kullanıcı girer.

### Kapsam dışında kalan işler

- Gerçek otopark kullanımı ve endüstriyel güvenlik uygunluğu
- Gerçekleşmiş giriş/çıkış yönünü ve araç geçişini kanıtlama
- Çoklu şerit ve hareket halindeki araçları izleme
- İlk aşamada özel OCR modeli eğitme veya bulut dağıtımı

### Araştırma soruları

- Işık, açı ve mesafe tam plaka doğruluğunu nasıl değiştiriyor?
- Ön işleme ham görüntüye göre hangi koşullarda yarar sağlıyor?
- Güven eşiği yanlış kabul ve yanlış ret dengesini nasıl etkiliyor?
- Cihazdan karara kadar gecikmenin hangi kısmı kamera, ağ veya OCR kaynaklı?

Demo testleri bu araştırma sorularını yanıtlamaz. Gerçek veri ve donanım ölçümleri daha sonraki haftalarda yapılacaktır.

## 2 Takım ve proje organizasyonu

Ekip yedi kişidir. Üye adları, bölümleri ve öğrenci numaraları ortak Drive’daki güncel raporda yer alır. Kesin görev atamaları ekipçe belirlenecek. Ömer Ufuk Boz yazılım ve gömülü sistem programlama tarafına ağırlık vermeyi planlıyor. Diğer görevler ekipçe atanacak.

| Üye | Ad soyad ve bölüm | Önerilen iş alanı |
| --- | --- | --- |
| 1 | Ömer Ufuk Boz / [Öğrenci no] | Yazılım ve gömülü sistemler |
| 2 | [Doldurulacak] | Elektronik ve güç tasarımı |
| 3 | [Doldurulacak] | Veri ve OCR deneyleri |
| 4 | [Doldurulacak] | Backend ve kayıt yönetimi |
| 5 | [Doldurulacak] | Web arayüzü |
| 6 | [Doldurulacak] | Mekanik ve 3D tasarım |
| 7 | [Doldurulacak] | Test ve dokümantasyon |

Tablodaki görevler öneridir, tamamlanmış atama değildir. Her iş alanının bir sorumlusu ve inceleyen ikinci üyesi belirlenecek. Alanlar arasındaki entegrasyon tüm ekibin sorumluluğudur.

### Haftalık koordinasyon

Dönüşümlü liderlik örnek rapordan alınan bir süreç önerisidir. Uygulanırsa yedi üye ilk yedi haftada dönüşümlü koordinasyon yapabilir; 8–10. haftaların liderleri ekipçe seçilir. Gerçek toplantı ve liderlik kayıtları Ek A’ya işlendikçe rapor güncellenir.

### Katkı ve inceleme süreci

Kod için issue, kısa ömürlü dal ve PR incelemesi öneriliyor. Ortak Google Drive belgeleri ekip tarafından düzenlenebilir. Her güncellemede güncel sürüm kontrol edilir, değişiklikler tek bir kişinin çalışması olarak varsayılmaz. AI ile hazırlanan kod ve metinler ekip incelemesi ve doğrulama gerektirir.

## 3 Literatür taraması ve teknik konumlandırma

Başlangıç taraması ürün ve kütüphane belgelerine dayanıyor. Henüz sistematik bir akademik literatür taraması tamamlanmadı. S3–S8 teknik kaynakları aday yaklaşımın uygulanabilirliğini incelemek için kullanılacak.

| Kaynak alanı | İncelenecek konu | Rapor kaydı |
| --- | --- | --- |
| ESP32 ve kamera | Kamera sürücüsü, JPEG ve PSRAM gereksinimleri | S3 ve S4 |
| Rust ve C++ | Gerçek kartta sürücü ve araç zinciri uyumu | S5 ve uygulanabilirlik deneyi |
| OCR | Algılama, metin tanıma ve güven skoru | S6 ve gerçek deneyler |
| Backend | Görüntü aktarımı, hata ve API sözleşmesi | S7 |
| Elektriksel uyum | Sensör Echo seviyesi ve kart girişleri | S8 ve kartın üretici föyü |

### Tamamlanacak akademik tarama

- Plaka tanıma üzerine en az birkaç doğrudan ilgili çalışma seçilecek.
- Her çalışma için veri, yöntem, metrik, ortam ve projeye aktarılabilir bulgu kaydedilecek.
- Genel OCR başarısı plaka tanıma başarısıyla eş tutulmayacak.
- Kaynaklardan alıntı yapılan her sonuç kendi veri ve deney koşullarıyla verilecek.

### Teknik çalışma kararları

Tek repository kullanıcı tercihidir. Rust gömülü yazılım için öncelikli aday, C++ alternatifidir. Kart üzerinde kısa bir uygulanabilirlik deneyi yapılmadan nihai dil seçimi yapılmayacak. Demo, kurulum bağımlılığını azaltmak için standart Python HTTP adaptörü kullanıyor. FastAPI ve gerçek OCR hedef mimaride bulunuyor, bu sürüme henüz eklenmedi.

Karar kaydı repository içinde docs/decisions.md dosyasında tutuluyor. Bu kararların ekipçe gözden geçirilmesi bekleniyor.

## 4 Veri ve yöntem

Bugünkü demo sentetik metin gözlemleri kullanıyor. Gerçek plaka görüntüsü veri kümesi, etiket sayısı ve OCR sonuçları henüz mevcut değil. Hazır EasyOCR kullanımı aday yöntemdir; özel model eğitimi için gereksinim oluşursa kapsam ayrıca değerlendirilecek.

### Veri toplama ve etiketleme planı

Kontrollü ve izinli çekimler veya sentetik plakalar kullanılacak. Her görüntü için sample_id, doğru plaka metni, çekim oturumu, ışık, açı, mesafe, kaynak/izin ve veri bölümü kaydedilecek. Aynı fiziksel plaka ve oturumun ayar ve test kümelerine dağılması engellenecek.

### İşleme ve erişim kararı

Hedef zincir JPEG alma, görüntü kalite kontrolü, gerekirse plaka ilgi alanı seçimi, ön işleme, OCR, metin normalizasyonu ve izinli listeyle tam eşleşmedir. Demo yalnızca son üç adımı sentetik gözlem üzerinde uygular. Boşluk ve harf büyüklüğü normalizasyonu yapılır, O/0 veya I/1 gibi karakterler otomatik düzeltilmez.

0.85 güven eşiği başlangıç önerisidir. Gerçek veriyle kalibre edilmedi. Düşük güven veya uygun olmayan biçim okunamadı sonucu üretir. OCR hatası ve ağ zaman aşımı demoda hata girdileridir; gerçek kütüphane ve ağ deneyi yapılmadı.

### Deney tasarımı

| Deney | Karşılaştırma | Kayıt |
| --- | --- | --- |
| E01 | Ham görüntü ve ön işleme | Aynı sabit test kümesi |
| E02 | Işık ve kamera açısı | Koşullara göre hata dağılımı |
| E03 | Güven eşiği değişimi | Yanlış kabul ve yanlış ret |
| E04 | Uçtan uca süre | Kamera, ağ ve OCR süreleri |

Gerçek deneyler için yazılım sürümü, model ağırlığı, cihaz/PC özellikleri ve rastgelelik ayarları kaydedilecek. Eşik seçimi ayar kümesinde yapılacak, test sonuçları son değerlendirmeye ayrılacak.

## 5 Sonuçlar ve değerlendirme

Bu bölüm başlangıç yazılım doğrulaması ile sonraki gerçek görüntü/donanım sonuçlarını ayrı tutar. 20 Python testi ve 8 sentetik karar senaryosu bu çalışma ortamında geçti. Uzak GitHub Actions henüz çalışmadı. Rust çekirdeğinin üç testi tanımlı, yerel Rust araç zinciri olmadığı için çalıştırılmadı.

| Kontrol | Kanıt | Durum |
| --- | --- | --- |
| İzin ve güven kararları | Python testleri | Geçti |
| Tekrar ve eşzamanlı istek | 12 eşzamanlı aynı istek testi | Tek kayıt ve tek sanal açma |
| Kalıcı kayıt ve liste | SQLite yeniden açma testi | Geçti |
| HTTP uçları | Yerel gerçek HTTP testleri | Geçti |
| Karar fixture deneyi | experiments.evaluate_decisions | 8/8 geçti |

Bu sonuçlar sentetik girişlerde yazılım davranışını doğrular. OCR doğruluğu, fiziksel bariyer güvenliği veya gerçek sahadaki gecikme hakkında sonuç vermez. Arayüz için ekip bilgisayarında tarayıcı provası yapılmalıdır.

### Gerçek deney sonuçları için alanlar

| Metrik | Tanım | Sonuç |
| --- | --- | --- |
| Tam plaka doğruluğu | Tam doğru metin / test görüntüleri | [Ölçülmedi] |
| Karakter hata oranı | Toplam düzenleme uzaklığı / doğru karakter sayısı | [Ölçülmedi] |
| Yanlış kabul oranı | İzinsiz olduğu halde izin verilen / izinsiz denemeler | [Ölçülmedi] |
| Yanlış ret oranı | İzinli olduğu halde izin verilmeyen / izinli denemeler | [Ölçülmedi] |
| p50 ve p95 gecikme | Gerçek uçtan uca süre yüzdelikleri | [Ölçülmedi] |

Eklenecekler: örnek sayısı, koşullar, başarısız örnekler, belirsizlik ve sınırlılıklar. Hiçbir boş alan sıfır başarı/hata değeri olarak yorumlanmamalıdır.

## 6 Proje yönetimi ve çalışma takvimi

Aşağıdaki 10 haftalık göreli plan öneridir. İlk sekiz hafta çekirdek geliştirme ve kabulü kapsar; 9–10. haftalar ders takvimi uygunsa iyileştirme içindir. Takvim, bütçe ve ekip atamaları kesinleşince güncellenecek. Gelecek işler tamamlandı olarak işaretlenmez.

| İş | Paket | Haftalar | Beklenen çıktı |
| --- | --- | --- | --- |
| WP01 | Kapsam ve sistem analizi | 1–1 | Gereksinimler ve açık kararlar |
| WP02 | Kart ve güç doğrulaması | 1–2 | Pin matrisi ve bileşen testleri |
| WP03 | Gömülü uygulanabilirlik | 2–3 | Rust kararı ve JPEG iletimi |
| WP04 | Veri toplama ve etiketleme | 2–4 | Kaynak ve çekim koşulu kayıtları |
| WP05 | OCR ve ön işleme deneyleri | 3–5 | Ayrı ayar ve test kümeleri |
| WP06 | Backend ve yönetim arayüzü | 2–5 | Görüntü API ve kimlik doğrulama |
| WP07 | Mekanik ve fiziksel entegrasyon | 3–6 | Kasa ve güvenli kapanma |
| WP08 | Entegrasyon ve kabul deneyleri | 6–8 | Gerçek cihaz ve hata senaryoları |
| WP09 | İyileştirme ve tekrar deneyleri | 9–10 | Takvim uygunsa ek çalışma |
| WP10 | Raporlama ve ekip kayıtları | 1–10 | Haftalık güncelleme ve kanıtlar |

### Bağımlılıklar ve ara hedefler

- Kart ve güç doğrulaması fiziksel entegrasyondan önce tamamlanmalı.
- Veri toplama gerçek OCR ölçümünden önce başlamalı.
- İlk birleşik hedef gerçek karttan JPEG alıp PC’ye iletmek.
- Fiziksel kapanma alan algılama deneyi geçmeden otomatikleştirilmemeli.
- Rapor ve toplantı kayıtları her hafta güncellenmeli.

Hafta 1 başlangıç durumu: kapsam ve başlangıç demo yazılımı hazır. Donanım envanteri ve görev atamaları bekliyor. Kişilerin fiili katkıları PR, toplantı kaydı ve deney kanıtıyla ayrıca kaydedilecek.

## 7 Elektriksel ve mekanik ekipmanlar

Bileşenler kaynak sunumdan alınan aday listedir. Satın alındığı veya çalıştığı teyit edilmedi. Kesin miktar, fiyat ve tedarik tarihi ekip tarafından girilecek.

| Bileşen | Görev | Durum |
| --- | --- | --- |
| ESP32-CAM | Kamera ve ağ bağlantısı | Kart varyantı bekliyor |
| HC-SR04 | Yaklaşma algılama | Sinyal seviyesi bekliyor |
| SG90 | Maket bariyer hareketi | Yük ve akım ölçümü bekliyor |
| LED ve dirençler | Durum gösterimi | Pin ve değer kontrolü bekliyor |
| Besleme ve adaptör | Güç ve programlama | Kapasite seçimi bekliyor |
| PLA ve kasa | Mekanik montaj | Ölçü ve tasarım bekliyor |

### Bağlantı tasarımının durumu

Kaynak PDF’deki GPIO12/13/14/16/15 tablosu onaylanmış şema olarak kullanılmayacak. GPIO16 bellekle çakışabilir; GPIO12/15 açılış ayarlarında rol oynar. Kamera, PSRAM ve microSD kullanımı kart şeması üzerinden birlikte incelenecek [S3, S4]. Standart 5 V HC-SR04 Echo hattı için giriş seviyesine uygun düşürme gerekir [S8].

### Mekanik ve güç doğrulaması

- Servo açı sınırı, bariyer kolu yükü ve sıkışma riski kaydedilecek.
- Servo hareketinde besleme gerilimi ve kart yeniden başlama davranışı ölçülecek.
- Ortak toprak ve güç dağıtımı şemada açık gösterilecek.
- Kamera açısı ve plaka netliği kasa tasarımından önce denenecek.
- Alan boşluğunu doğrulayacak sensör düzeni kararlaştırılacak.

Bütçe kaydı: [Parça, miktar, birim fiyat, toplam, kaynak, satın alma tarihi]. Toplam bütçe henüz hesaplanmadı.

## 8 Etik toplumsal etki ve sürdürülebilirlik

Proje, otomatik erişim kararının yanlış sonuç verebileceğini kabul eder. Düşük güvenli gözlemde açmama ve yaklaşık plaka eşleştirmesinden kaçınma başlangıç ilkeleridir. Fiziksel kullanım için ek güvenlik ve alan algılama gerekir; eğitim demosu bu uygunluğu kanıtlamaz.

### Veri ve erişim

Public kaynaklarda sentetik plakalar kullanılacak. Gerçek görüntüler için izin, erişim yetkisi ve saklama süresi ekipçe belirlenecek. Kimlik bilgileri, öğrenci numaraları, Wi-Fi parolaları ve gerçek plaka görüntüleri public repository’ye eklenmeyecek. Backend demo adaptöründe üretim kimlik doğrulaması yoktur ve yalnızca yerel bağlantıyla çalışır.

### Toplumsal değerlendirme

İzinli bir aracın yanlış reddedilmesi erişim sorununa, izinsiz aracın yanlış kabulü erişim kontrolü hatasına yol açabilir. Bu iki hata ayrı raporlanacak. Plaka eşleşmesi araç sahibinin kimliği veya yetkisinin güçlü doğrulaması olarak sunulmayacak.

### Enerji ve karbon kaydı

Henüz enerji veya karbon ölçümü yapılmadı. PC, kart ve servo çalışma süresi ve ortalama güç ayrı kaydedilecek. Enerji hesabı E = P × t / 1000, P watt ve t saat olduğunda kWh verir. Karbon tahmini E × emisyon katsayısı ile hesaplanır. Katsayının kaynağı, yılı ve bölgesi belirtilmeden sonuç yazılmayacak.

| Cihaz veya süreç | Güç W | Süre saat | Enerji kWh |
| --- | --- | --- | --- |
| [PC OCR deneyi] | [Ölçülecek] | [Kaydedilecek] | [Hesaplanacak] |
| [Kart ve servo] | [Ölçülecek] | [Kaydedilecek] | [Hesaplanacak] |
| [3D baskı] | [Ölçülecek] | [Kaydedilecek] | [Hesaplanacak] |

PC etiketi veya tepe güç değeri ölçülmüş ortalama güç yerine kullanılmayacak. Baskı atığı, tekrar kullanılabilen parçalar ve onarım ihtiyacı dönem sonunda değerlendirilecek.

## 9 Bireysel öz değerlendirmeler

Her ekip üyesi kendi katkısını ve öğrendiği konuları dönem boyunca yazacak. Bu taslak hiçbir üye adına tamamlanmış iş, liderlik deneyimi veya kişisel öğrenme iddiası içermez.

| Üye | Kanıt ve katkı kaydı | Öz değerlendirme |
| --- | --- | --- |
| 1 | [PR, deney veya toplantı kaydı] | [Üye tarafından yazılacak] |
| 2 | [PR, deney veya toplantı kaydı] | [Üye tarafından yazılacak] |
| 3 | [PR, deney veya toplantı kaydı] | [Üye tarafından yazılacak] |
| 4 | [PR, deney veya toplantı kaydı] | [Üye tarafından yazılacak] |
| 5 | [PR, deney veya toplantı kaydı] | [Üye tarafından yazılacak] |
| 6 | [PR, deney veya toplantı kaydı] | [Üye tarafından yazılacak] |
| 7 | [PR, deney veya toplantı kaydı] | [Üye tarafından yazılacak] |

### Her üye için doldurulacak alanlar

- Ad soyad, bölüm ve öğrenci numarası
- Üstlenilen iş ve varsa liderlik haftası
- Somut çıktı ve bağlantısı
- Karşılaşılan sorun ve denenen çözüm
- Öğrenilen teknik veya ekip çalışması konusu
- Geliştirilmesi gereken yön ve sonraki adım

Bir çıktıyı kimin yazdığı, kimin incelediği ve kimin donanımda doğruladığı ayrı belirtilmeli. Ortak katkılar tek kişiye mal edilmemeli. AI desteği kullanılan çalışmalarda inceleme ve doğrulama sorumluluğu ekipte kalır.

## 10 Kaynakça ve ekler

Teknik web kaynaklarının inceleme tarihi 11 Ekim 2026’dır. Kaynak listesi dönem boyunca akademik çalışmalar ve üretici föyleriyle genişletilecek.

S1  Ana proje sunumu. Ortak Drive PDF, 10 sayfa, 4 Ekim 2026 içerik tarihi. Kapsam ve bileşen önerileri. https://drive.google.com/file/d/1L5Am6SDtG7YU6WwXuPOf-1LHQXYvsT16/view

S2  Rapor örneği. Kullanıcının paylaştığı rapor-ornegi.PDF, 48 sayfa. Bölüm yapısı ve boş süreç formu tasarımı için referans. Örneğin kişi ve sonuçları bu projeye aktarılmadı.

S3  ESP32 kamera sürücüsü. Espressif esp32-camera resmi kaynak ve README. https://github.com/espressif/esp32-camera

S4  ESP32 GPIO kısıtları. Espressif ESP-IDF GPIO belgesi. https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/gpio.html

S5  Rust ESP-IDF desteği. Güncel esp-rs/esp-idf kaynakları. https://github.com/esp-rs/esp-idf

S6  EasyOCR. JaidedAI resmi kaynakları. https://github.com/JaidedAI/EasyOCR

S7  FastAPI. Resmi başlangıç dokümantasyonu. https://fastapi.tiangolo.com/tutorial/first-steps/

S8  HC SR04 sinyal seviyeleri. Portland State University doğrudan eğitim materyali. Varyant seçimine göre değerlendirilir. https://web.cecs.pdx.edu/~gerry/class/IB/sensors/HC-SR04/

### Eklerin kullanım durumu

Ek A toplantı ve haftalık ilerleme için boş formdur. Ek B örnek rapordaki A–K değerlendirme alanlarını başlangıç formuna dönüştürür. Bu ağırlıklar resmi ders ölçütü olarak teyit edilmedi. Sayısal öz değerlendirme veya başarı puanı henüz girilmedi.

Kod ve deney kanıtı: backend, tests ve experiments klasörleri. Güncel durum kaydı: docs/project-spec.json. Ortak Drive belgeleri ile kodun durum bilgisi birlikte güncellenecek.

## Ek A Haftalık ilerleme ve toplantı formu

Bu sayfa her hafta çoğaltılabilir. Yapılmamış toplantı, katılım veya imza kaydı oluşturulmadı.

| Alan | Ekip tarafından doldurulacak |
| --- | --- |
| Hafta ve tarih | [Hafta] [Tarih] |
| Koordinatör | [Ad soyad] |
| Katılanlar | [Katılan üyeler] |
| Gündem | [Gündem maddeleri] |
| Kararlar | [Karar, gerekçe, sorumlu] |
| Tamamlanan işler | [İş, kanıt bağlantısı, inceleyen] |
| Açık sorunlar | [Sorun, etki, çözüm adımı] |
| Gelecek hafta | [İş, sorumlu, kabul ölçütü] |

### Hafta bazında kayıt dizini

| Hafta | Kayıt ve lider | Durum |
| --- | --- | --- |
| 1 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 2 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 3 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 4 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 5 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 6 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 7 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 8 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 9 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |
| 10 | [Toplantı bağlantısı ve koordinatör] | [Güncellenecek] |

Açıklama: Tarih, lider ve katılım alanları toplantıdan sonra gerçek kayıtla doldurulacak. 9–10. haftalar ders takvimine bağlıdır.

## Ek B Değerlendirme formu

Örnek rapordan uyarlanan ölçütler aşağıdadır. Ağırlıkların dersin resmi rubriğiyle uyumu öğretim elemanından teyit edilmelidir. Her üye için bu form çoğaltılabilir.

| Kod | Ölçüt | Ağırlık yüzde | Puan ve kanıt |
| --- | --- | --- | --- |
| A | Problem tanımı ve amaç | 10 | [Doldurulacak] |
| B | Çok disiplinli takım çalışması | 10 | [Doldurulacak] |
| C | Dönüşümlü liderlik ve görev paylaşımı | 10 | [Doldurulacak] |
| D | Literatür taraması ve konumlandırma | 10 | [Doldurulacak] |
| E | Veri ön işleme ve yöntem seçimi | 15 | [Doldurulacak] |
| F | Deneysel kurgu ve sonuç analizi | 15 | [Doldurulacak] |
| G | Proje yönetimi ve çalışma takvimi | 8 | [Doldurulacak] |
| H | Etik toplumsal etki ve karbon ayak izi | 7 | [Doldurulacak] |
| I | Bireysel değerlendirme ve öğrenme | 5 | [Doldurulacak] |
| J | Yazılı rapor kalitesi | 5 | [Doldurulacak] |
| K | Sunum | 5 | [Doldurulacak] |

Ad soyad: [Doldurulacak]. Değerlendirme tarihi: [Doldurulacak]. Puan ölçeği ve hesaplama yöntemi: [Resmi rubriğe göre teyit edilecek].

### Rapor güncelleme kontrolü

- Her tamamlandı ifadesinin kanıtı var mı?
- Sentetik karar testleri gerçek OCR ölçümlerinden ayrılmış mı?
- Güncel ekip değişiklikleri korundu mu?
- Metriklerde örnek sayısı ve koşullar belirtilmiş mi?
- Rapor, Sistem Analizi ve sunum aynı kapsamı gösteriyor mu?
