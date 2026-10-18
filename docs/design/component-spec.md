# Bileşen davranış sözleşmesi

Bu dosya gelecek uygulama desenlerini tanımlar; bileşen veya route henüz yazılmadı.
Stil değerleri [design-system.md](design-system.md), yerleşim [layout-spec.md](layout-spec.md),
widget kaynakları [pages/overview.md](pages/overview.md) içindedir. Ortak durum
kuralı: veri yok, yükleniyor ve sıfır değer birbirinin yerine gösterilmez.

## Sidebar navigasyonu

- **Sorumluluk/yapı:** ana sayfa bağlantısı, tek ikon ailesi ve gerçek bölüm linkleri; ürünün tam adı header'da, mobil menüde link etiketleri görünür; ayrı sidebar kartı yok.
- **Varyant/durum:** normal, hover, odak, aktif; tek aktif hedef mavi daireyle belirginleşir.
- **Etkileşim:** aktif hedef yerel kaydırma veya sonradan onaylanacak route ile tutarlı olur.
- **Responsive:** desktop/tablet ikon rayı; mobilde etiketli açılır menü.
- **Erişilebilirlik:** nav adı, link adı ve uygun `aria-current`; tooltip klavye odağında da görünür, link adı yerine geçmez.

## Sayfa header'ı

- **Sorumluluk/yapı:** küçük proje adı, tek h1, mod işareti, sınırlı arama ve yenileme; dev başlık kartı yok.
- **Varyant/durum:** ilk yükleme, güncel veri, yenileniyor, son yenileme başarısız.
- **Etkileşim:** yenileme yalnızca snapshot okur; “Son yenileme” istemcinin başarılı okuma zamanıdır, cihaz heartbeat'i değildir.
- **Responsive:** kontroller iki satıra, mobilde tam genişliğe açılır.
- **Erişilebilirlik:** başlık sırası ve etiketli yenileme butonu; sonuç nazik canlı bölgede, otomatik odak atlaması olmadan duyurulur.

## Arama ve filtreler

- **Sorumluluk/yapı:** “Yüklü kayıtlarda plaka ara” girdisi ve karar seçimi; küresel arama/tarih raporu görünümü yok.
- **Varyant/durum:** boş, dolu, odak, sonuç yok; “Temizle” ve eşleşen/yüklenen adet görünür.
- **Etkileşim:** yalnızca eldeki events üzerinde; API çağrısı veya tüm DB araması iddiası yok. Filtreler tabloyu etkiler; üst metrik/dağılımın filtresiz pencereyi anlattığı yazılır.
- **Responsive:** desktop yatay, mobil alt alta; filter chip'leri sarılır, kesilmez.
- **Erişilebilirlik:** placeholder dışında label; karar seçimi etiketli select veya tek seçimli grup; sonuç adedi duyurulur.

## Aksiyon butonları

- **Sorumluluk/yapı:** metin öncelikli hap buton; ikon metni destekler. Primary, secondary, tertiary ve destructive varyantlar tokenlara uyar.
- **Varyant/durum:** normal, hover, odak, disabled, pending; aynı işlem beklerken ikinci gönderim kapalıdır.
- **Etkileşim:** gerçek buton/link semantiği; yenileme ile mutasyon karıştırılmaz. İşlem sonucu ve başarısızlık görünürdür.
- **Responsive:** mobil kritik aksiyon tam genişlik; en az 44px hedef, metin kesilmez.
- **Erişilebilirlik:** ikon-only adlandırılır; `aria-busy` ve görünen bekleme metni, disabled nedeni erişilebilir açıklamayla verilir.

## Metrik kartları

- **Sorumluluk/yapı:** küçük başlık → büyük değer → veri penceresi/kaynak açıklaması; en fazla bir ikincil bilgi.
- **Varyant/durum:** sayı, skeleton, yüklenemedi; sıfır yalnızca doğrulanmış boş snapshot'ta.
- **Etkileşim:** ilgili bölüme gerçek bağlantı dışında gereksiz menü/ellipsis yok. Rastgele yüzde değişim, mini trend veya saat şeritleri eklenmez.
- **Responsive:** desktop üçlü, tablette 2+1, mobil tek sütun; görsel hiyerarşi korunur.
- **Erişilebilirlik:** başlık/değer ilişkisi açık; payda metni yüzdeye eşlik eder, renk tek bilgi taşıyıcısı değildir.

## Durum göstergeleri

- **Sorumluluk/yapı:** karar, sanal bariyer ve veri erişimi ayrı etiketlenir; ikon + metin + ölçülü semantik renk.
- **Varyant/durum:** allow/deny/unreadable/error; closed/open_waiting_clear; ayrıca yalnız UI için yükleniyor/bilinmiyor/eski veri. UI durumları yeni API enum'u değildir.
- **Etkileşim:** geçmiş olayın barrier değeri güncel durum yerine kullanılmaz; hata halinde eski durum güncelmiş gibi sunulmaz.
- **Responsive:** uzun “Açık — alan boşluğu bekleniyor” etiketi iki satıra açılır.
- **Erişilebilirlik:** renk körlüğünde de anlam korunur; değişim `role=status` ile ölçülü duyurulur, odak çalınmaz.

## Erişim denemesi tablosu

- **Sorumluluk/yapı:** zaman, sentetik plaka, güven, karar, neden ve sanal hareket; başlıkta yüklenen pencere belirtilir.
- **Varyant/durum:** dolu, gerçek boş, filtre sonucu yok, yükleme, yenileme hatası. Sayfalama verisi yokken paginator gösterilmez.
- **Etkileşim:** gerekirse satır ayrıntısında request_id/tam zaman; salt okuma. Kayıt sırası backend snapshot sırasını izler; kimlik/tarih kesilmesi tam değeri gizlemez.
- **Responsive:** genişte semantik tablo ve lokal scroll; mobilde etiket/değer satır kartları.
- **Erişilebilirlik:** caption, sütun başlıkları ve scroll bölgesi adı; satırın tamamı gizli tıklama alanı yapılmaz, ayrıntı gerçek butondur.

## Bilgi ve son karar kartları

- **Sorumluluk/yapı:** etiket/değer hücreleriyle mod, sürüm, entegrasyon sınırı veya son kayıt; gereksiz dekoratif resim yok.
- **Varyant/durum:** bilgi, son olay, kayıt yok, veri bilinmiyor; deneysel eşik gösterilecekse “öneri/kalibre edilmedi” açıklaması gerekir.
- **Etkileşim:** yalnız gerekli açıklama/ilgili bölüm bağlantısı; backend onayını geçersiz kılan “Aç” butonu yok.
- **Responsive:** genişte küçük hücreler, mobilde metin sırasıyla tek/iki sütun.
- **Erişilebilirlik:** açıklama listesi (`dl`) veya başlıklı bölüm; kritik mod uyarısı tooltip arkasına saklanmaz.

## Karar dağılımı grafiği

- **Sorumluluk/yapı:** yüklenmiş olayların dört karar adedi; Parkora'nın geniş grafik/dar yardımcı kart oranı korunur, iş anlamı uyarlanır.
- **Varyant/durum:** veri varsa dört yatay çubuk ve tam adetler; N=0 ise boş durum, N bilinmiyorsa yükleme/hata. Yüzde varsa payda N ile birlikte verilir.
- **Etkileşim:** tooltip tek veri kaynağı değildir; karşılaştırma dönemi, doluluk göstergesi veya büyüme trendi üretilmez.
- **Responsive:** çubuklar yatay kalır; lejant/metin alta akar, okunmaz minyatüre dönüşmez.
- **Erişilebilirlik:** yanında aynı dört değerin metinsel listesi; anlamlı çubuk sınırı/etiketi kontrastlı; hover-only veri veya renkle ayırt etme yok.

## Boş, yükleniyor ve hata desenleri

- **Sorumluluk/yapı:** veri bölgesinin boyutunu koruyan sade skeleton ya da kısa açıklama; büyük illüstrasyon yok.
- **Varyant/durum:** “Henüz deneme yok”, “Filtreye uygun kayıt yok”, “Durum alınamadı”, “Eski veri — yenileme başarısız” ayrı metinlerdir.
- **Etkileşim:** boşta gözlem aksiyonu, filtre boşluğunda temizleme, okuma hatasında yeniden dene. Son başarılı veri saklanıyorsa eski etiketi zorunlu; mutasyonlar taze durum okunana kadar kapalı.
- **Responsive:** metin/aksiyon sarılır; sabit yükseklik hata mesajını kesmez.
- **Erişilebilirlik:** skeleton dekoratiftir, bölge busy olarak işaretlenir; hatada erişilebilir açıklama ve gerekirse tek alert kullanılır, her kart aynı hatayı tekrar duyurmaz.

## Gözlem formu ve işlem sonucu

- **Sorumluluk/yapı:** sentetik plaka, güven ve hata senaryosu; açık simülasyon başlığıyla yeni gözlem oluşturma.
- **Varyant/durum:** düzenleme, alan hatası, gönderiliyor, sonuç, belirsiz ağ sonucu. Gösterilen güven gerçek OCR ölçümü değildir.
- **Etkileşim:** alanlar kanonik sözleşmeye uyar; yeni gözleme yeni request_id, aynı gözlemi tekrara aynı kimlik ve yük. Belirsiz POST sonucu yeni kimlikle otomatik tekrar edilmez; idempotency korunur. Başarıda snapshot yenilenir, başarısız yenilemede durum eski işaretlenir.
- **Responsive:** desktop sınırlı genişlikte dialog; mobil uygun boşlukla tam genişlik/yükseklik, içerik kaydırılır.
- **Erişilebilirlik:** her alanın label/hata ilişkisi; ilk geçersiz alana odak, sonuç canlı bölge; range varsa sayısal değer klavyeyle de düzenlenebilir.

## Dialog ve doğrulama

- **Sorumluluk/yapı:** gözlem formu, izinli plaka ekleme/silme ve manuel alan boşluğu doğrulaması; gereksiz onay adımları eklenmez.
- **Varyant/durum:** açık, iptal, pending, hata, başarı. Plaka silmede hedef plaka; manuel boşlukta “Bu yalnızca sanal demodur” açıklaması görünür.
- **Etkileşim:** yeni gözlem için ek onay yok; plaka silme ve manuel boşluk için açık hedef/sonuç teyidi vardır. Manuel boşluk yalnız güncel open_waiting_clear durumunda etkin; zamanlayıcıyla kapanma yok. Pending'de yeniden gönderim engellenir, kapanış/ESC sunucu isteğini iptal etti diye sunulmaz.
- **Responsive:** küçük ekranda içerik kaydırılır, başlık/iptal erişilebilir kalır.
- **Erişilebilirlik:** dialog adı/açıklaması, modal odak yönetimi ve dönüşü; yıkıcı işlemde başlangıç odağı iptal veya başlıktadır. Arka içerik modal açıkken etkileşimsizdir.
