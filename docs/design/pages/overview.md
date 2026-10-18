# Genel Bakış dashboard'u

## Amaç ve sınır

Operatör sanal bariyer durumunu, sentetik gözlemlerden çıkan erişim kararlarını
ve izinli listeyi tek bakışta anlayabilmelidir. Bu bir otopark doluluk/ödeme
ürünü veya fiziksel cihaz kontrol paneli değildir. Tasarım henüz uygulanmadı.
Görsel kurallar [tasarım ana sayfası](../README.md), tokenlar
[design-system.md](../design-system.md), yerleşim [layout-spec.md](../layout-spec.md),
desenler [component-spec.md](../component-spec.md) içindedir.

Kanonik sözleşme [docs/api.md](../../api.md) değişmez. Aşağıdaki alan eşlemesi,
[server.py](../../../backend/server.py) ve [store.py](../../../backend/store.py)
okumasıyla desteklenen tasarım bağımlılığıdır; ek API sözleşmesi oluşturmaz.

## İçerik sırası ve kart düzeni

| Sıra | Masaüstü / içerik | Hedef |
|---|---|---|
| Header | Yüzeysiz; “Genel Bakış”, simülasyon etiketi, sınırlı kayıt araması ve yenileme | Veri kapsamı ve sayfa yönü |
| 1 | 8 sütun sanal bariyer/etiket-değer hücreleri + 4 sütun simülasyon aksiyon kartı | Durum önce, yeni sentetik gözlem sonra |
| 2 | Üç eşit kart: “Yüklenen denemeler”, “Bu kayıtlarda izin”, “İzinli plakalar” | Kanıtlı ve sınırlı özet |
| 3 | 8 sütun karar dağılımı + 4 sütun son kayıt ayrıntısı | Grafik hiyerarşisi ve bağlam |
| 4 | Tam genişlikte erişim denemeleri; başlangıçta ilk 10 kayıt, eldeki en fazla 50 kaydı açan “Yüklenenlerin tümünü göster” | Okunur, sıkıştırılmamış geçmiş |
| 5 | İzinli liste bölümü; kompakt metrikten erişilir, ekle/sil kontrolleri burada | Overview'u büyük ikinci tabloya boğmadan yönetim |

Üst durum kartı mod, sanal durum ve fiziksel bağlantı yok açıklaması taşır;
ayrı bir tüm-sayfa paneli oluşturmaz. Aksiyon kartında siyah “Sentetik gözlem
oluştur”, ikincil “Alanı boş doğrula” ve önceki gözlem varsa açık etiketli
“Aynı gözlemi tekrarla” bulunur. “Bariyeri aç” veya fiziksel kontrol iddiası yoktur.
Manuel alan doğrulaması yalnız sanal açık durumda etkin ve açıklamalı teyitlidir.

Navigasyon hedefleri Genel Bakış, Erişim Denemeleri, İzinli Plakalar ve
Simülasyon'dur; bu sözleşme ayrı route veya uygulama dosyası oluşturmaz.
Varsayılan okuma isteği sayfa açılışı, kullanıcı yenilemesi ve başarılı mutasyon
sonrasıdır. Otomatik polling/canlı stream yok; “gerçek zamanlı” etiketi kullanılmaz.

## Widget ve veri kaynağı haritası

Durum sözlüğü: **IMPLEMENTED** mevcut API/kaynakta var; **DERIVED** yalnız eldeki
yanıttan istemcide hesaplanır; **PROPOSED** yeni sözleşme/ekip işi gerekir;
**UNAVAILABLE** mevcut veriyle desteklenmez, ilk sayfaya konmaz. Bu etiketler
tasarım izlenebilirliğidir; kullanıcıya teknik enum olarak gösterilmez.

| Widget/veri | Durum | Kaynak / sınır ve UI metni |
|---|---|---|
| Mod ve sürüm | IMPLEMENTED | GET /api/health: mode ve version; health başarısı fiziksel cihaz sağlığı değildir |
| Güncel sanal bariyer | IMPLEMENTED | GET /api/state: barrier; closed → “Kapalı”, open_waiting_clear → “Açık — alan boşluğu bekleniyor” |
| Donanım/OCR sınırı | IMPLEMENTED | Snapshot'ta mode=simulation, real_ocr=false, physical_hardware=false kaynakta mevcut; alanlar docs/api.md'de ayrıntılı şemalanmamış. Görünür açıklama her durumda “Sentetik demo; fiziksel bariyer bağlı değil”; yeni fiziksel mod varsayılmaz |
| Yüklenen denemeler N | DERIVED | GET /api/state events.length; N≤50. “Yüklenen son N deneme”; toplam DB kaydı veya araç sayısı değil |
| İzin özeti A / N | DERIVED | events içinde decision=allow sayısı; “Bu kayıtlarda A izin kararı”. N=0 iken oran hesaplanmaz; fiziksel giriş/başarı oranı değildir |
| İzinli plaka sayısı | DERIVED | allowed_plates.length; listedeki anlık kayıt sayısı, aktif kullanıcı sayısı değil |
| İzinli liste | IMPLEMENTED | GET /api/state allowed_plates; ekle/sil sonrası snapshot yenilenir |
| Karar dağılımı | DERIVED | Aynı events penceresinde allow/deny/unreadable/error adetleri; dört adedin toplamı N. “Yüklenen kayıtların karar dağılımı”; trend veya OCR doğruluğu değil |
| Son kayıt / tablo | IMPLEMENTED | events içindeki decision, plate, confidence, reason, created_at, barrier_action, request_id kaynakta mevcut; ilk öğe en son kaydedilen olaydır. Payload ayrıntıları kanonik belgede tam şemalanmamış |
| Son yenileme zamanı | DERIVED | İstemcide son başarılı snapshot okuma zamanı; cihazın son bağlantısı veya verinin sürekli güncel olduğu iddiası değil |
| Yerel arama/karar filtresi | DERIVED | Yalnız eldeki events; “X / N yüklü kayıt eşleşiyor”. Üst özetler ve grafik aynı filtresiz N penceresinde kalır |
| Tüm dönem toplamları / günlük-haftalık karşılaştırma | PROPOSED | Tam geçmiş, zaman filtresi, sayfalama veya aggregate sözleşmesi gerekir; bu sürümde gösterilmez |
| Gerçek OCR, kamera, cihaz heartbeat'i ve fiziksel bariyer telemetrisi | PROPOSED | Python/OCR/firmware alan sahipleriyle sözleşme ve gerçek entegrasyon doğrulaması gerekir; uygulanmış sayılmaz |
| Doluluk, gelir, rezervasyon, gerçekleşmiş araç giriş/çıkış sayısı | UNAVAILABLE | Veri modeli ve doğrulanmış olay yok; kart, yüzde veya sahte demo sayısı eklenmez |

`events` en son 50 kaydedilmiş gözlemdir, tüm HTTP çağrıları değildir. Tekrar
istek yeni kayıt üretmediği için bu pencereden tekrar/duplicate oranı çıkarılmaz.
N=50 olması tüm geçmişin geldiğini göstermez; filtre boşluğu tüm DB'de yokluk
anlamına gelmez. `actions` son 20 sanal hareketi sağlar; N ile aynı pencereyi
garanti etmez, fiziksel hareket KPI'ına veya deneme oranına karıştırılmaz.
Geçmiş event yanıtındaki barrier alanı güncel durum kaynağı değildir.
Saat UTC'den tarayıcı saat dilimine çevrilir ve kullanılan dilim açıklanır;
tam tarih/saat ayrıntıda görülebilir. İstemci filtrelemesi yeni yetkilendirme kararı vermez.

## Aksiyon bağımlılıkları

| Kullanıcı aksiyonu | Durum | Mevcut API bağımlılığı ve davranış |
|---|---|---|
| Yenile | IMPLEMENTED | GET /api/state ve gerektiğinde health; okuma hatası ayrı gösterilir |
| Sentetik gözlem oluştur | IMPLEMENTED | POST /api/demo/scan; alanlar kanonik sözleşmeden gelir. Yeni kimlik; başarılı sonuç sonrası state yenile |
| Aynı gözlemi tekrarla | IMPLEMENTED | Aynı scan, aynı kimlik ve normalize aynı yük. Session'da önceki yük yoksa disabled; aynı kimlikle başka veri gönderme. Geçmiş cevap yeni hareket değildir |
| Sanal alanı boş doğrula | IMPLEMENTED | POST /api/demo/clear; açık durum ve manuel teyit; gerçek sensör veya zamanlayıcı yerine gösterilmez |
| Sentetik plaka ekle/sil | IMPLEMENTED | POST /api/plates/add ve /api/plates/remove; liste bölümünde, silmede hedef teyidi; hata/sonuç ve snapshot yenileme |

Mutasyon pending iken yeniden gönderim engellenir; otomatik iyimser bariyer
açma/kapatma yapılmaz. Sonuç belirsizse yeni request_id ile otomatik scan tekrarı
yapılmaz; aynı gözlem verisi korunur. HTTP hata anlamları docs/api.md'den alınır.
UI'da bilinmeyen karar/durum gelirse güvenli “Bilinmeyen durum” gösterilir,
başarı/izin varsayılmaz; mutasyonlar kapalı tutulur ve sözleşme uyumsuzluğu bildirilir.

## Eksik sözleşme ve entegrasyon işleri

İlk sayfanın temel özeti için yeni business endpoint zorunlu değildir. Ancak
Next.js entegrasyon planından önce aşağıdaki bağımlılıklar çözülmelidir:

- Mevcut docs/api.md özet sözleşmesi ayrıntılı state/plate/clear yanıt şemalarını
  tam tanımlamıyor. Kullanılan alanlar kaynakta incelendi; TypeScript istemci
  sözleşmesi olarak sabitlenmeden Python ekibiyle şema/boş değer/hata örnekleri
  doğrulanmalı. Kaynaktan çıkarılan alanlar burada yeni API garantisi sayılmaz.
- Mevcut stdlib sunucusu yalnız belirli vanilla dosyaları sunar; Next.js barındırma
  ve aynı-origin geliştirme bağlantısı henüz tanımlı değildir. Mutasyon Origin
  kısıtı vardır; farklı port otomatik çalışır veya CORS hazır varsayılmaz.
  Frontend/API ekibi bağlantı önerisini Python alan sahibiyle koordine eder.
  Çözüm Next.js'te yinelenen business API veya doğrudan SQLite erişimi olamaz.
- Global filtre/istatistik veya fiziksel veri istenirse yeni sözleşme önerisi
  hazırlanır; bu sayfa onların onayını, endpoint yolunu veya uygulanmasını varsaymaz.
  Kimlik doğrulamasız demo loopback sınırında kalır.

## Yükleme, hata ve boş durumlar

- İlk okumada skeleton ve “Durum alınıyor”; sayılara 0, bariyere “Kapalı” uydurulmaz.
- Başarılı boş events: “Henüz erişim denemesi yok”; sentetik gözlem aksiyonu.
  Boş allowlist: ayrı “İzinli plaka yok” ve ekleme aksiyonu; otomatik tohumlama yok.
- Yerel filtre sonucu boş: arama/filtreyi temizle; yeni kayıt olmadığı iddia edilmez.
- State hatasında durum bilinmiyor; önceki snapshot tutuluyorsa “Eski veri” ve
  son başarılı okuma zamanı. Güncel state tekrar alınana kadar mutasyonlar kapalı.
- Health hatası ayrı bildirilir; başarılı state çöpe atılmaz. State yanıtında
  simulation doğrulansa bile health başarısı olmadan sürüm/sağlık uydurulmaz.
- Mutasyon başarılı, yenileme başarısız: “İşlem yanıtı alındı; güncel durum
  yenilenemedi”; eski kartlar başarıyla güncellenmiş gibi değiştirilmez.
- POST hatası kullanıcı girdisini silmez; alan doğrulaması ve sunucu hatası ayrılır.
  Simüle network_timeout kararını gerçek HTTP bağlantı hatasıyla karıştırma.

## Ekran davranışı ve kabul ölçütleri

Desktop'ta üst 8:4 ve üçlü metrik sırası korunur; tablette 8 sütunlu düzen,
mobilde tek sütun ve açılır navigasyon [yerleşim sözleşmesine](../layout-spec.md)
uyar. DOM sırası görsel sırayla aynıdır. Tabloda önce ilk 10 kayıt gösterimi
yerel görünüm seçimidir; backend sayfalaması veya ek veri yükleme değildir.

Görsel incelemede şu koşulların tümü sağlanmalıdır:

- Full-bleed tek tuval; çerçevesiz sidebar ve bağımsız floating-island kartlar;
  kartlar/uygulama etrafında dev beyaz panel yok.
- Referanstaki sakin açık mod, kompakt bilgi hücreleri, geniş analiz/dar yan kart,
  tutarlı köşe ve boşluk hiyerarşisi korunur; otomobil/logo kopyası yok.
- “Simülasyon” ve “Fiziksel bariyer bağlı değil” ilk görünümde okunur; allow
  etiketi gerçek giriş, confidence gerçek OCR başarısı olarak sunulmaz.
- Dört kararın her biri, kapalı/açık sanal durum ve duplicate sonucu için
  ayrı sentetik örneklerle doğru metin ve aksiyonlar incelenir.
- N=0, N=1, N=50, uzun plaka/neden, filtre boşluğu, okuma/POST hatası,
  pending ve eski veri senaryoları gösterilir; desteklenmeyen KPI yok.
- Klavye ile menü/form/dialog tamamlanır; odak görünür ve geri döner;
  kontrast, 320px reflow, %200 zoom ve reduced-motion kontrol edilir.

Bu ölçütler gelecekteki yetkili uygulama incelemesine aittir; bu belge görevi
tarayıcı testi veya fiziksel sistem kabulü gerçekleştirildiği iddiası taşımaz.
