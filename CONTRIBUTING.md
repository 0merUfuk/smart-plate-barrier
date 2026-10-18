# Katkı süreci

## İş kapsamı ve dal akışı

Her işin amacı ve gözlenebilir kabul ölçütü issue veya yazılı görev talebinde
bulunsun. Etkilenen kapsamı, alan sahibini, bağımlılıkları ve doğrulama yöntemini
belirt; planlanan ve uygulanmış davranışı ayır. Küçük belge işlerinde aynı
bilgiyi ayrı bir issue ve ek formlarda tekrar yazmak gerekmez.

Başlamadan origin, dal, HEAD ve çalışma ağacını kontrol et. Resmî kod repository'si
https://github.com/0merUfuk/smart-plate-barrier adresidir. Beklenen ve yetkili
mevcut değişiklikleri koruyarak işe devam et; kirli çalışma ağacı tek başına
engel değildir. Beklenmeyen/ilgisiz değişiklikleri ezme; çakışan kapsamı
netleştirmeden düzenleme yapma. Bağımsız, yetkili işe devam edilebilir.
Yeni işte güncel main tabanından küçük ve kısa ömürlü bir dal aç; yetkili devam
işinde mevcut dalı koru. main üzerinde çalışma.
Dal adları `docs/<konu>`, `feature/<konu>`, `fix/<konu>` veya Codex işleri için
`codex/<konu>` olabilir. Var olan dalı zorla sıfırlama veya üzerine yazma.
İlgisiz temizlik, yeniden biçimlendirme ve refactor'u aynı işe ekleme.

## Sahiplik ve mimari sınırlar

| Rol | Sorumluluk |
|---|---|
| Frontend ve API sözleşmesi ekibi | web/, frontend testleri ve framework'ten bağımsız API sözleşmesi tasarımı |
| Python/backend uygulama ekibi | Python kaynakları, kütüphaneleri ve testleri; FastAPI uçları, SQLite kalıcılığı ve iş mantığı |
| OCR ve görüntü işleme ekibi | OCR uygulaması, görüntü işleme ve ilgili deneyler |
| Firmware ve donanım alan sahipleri | Firmware, cihaz iletişimi, sensörler ve fiziksel bariyer entegrasyonu |

Bunlar rol sınırlarıdır; bireysel görev ataması değildir. Normal frontend/API
sözleşmesi işinde diğer alanların kaynakları değiştirilmez. Gereken değişikliği
alan sahibine bağımlılık olarak bildir; kapsam dışı uygulama için açık onay gerekir.
API tasarlamak Python uygulamasını değiştirme yetkisi vermez.

Kalıcı mimari ve güvenlik sınırları [AGENTS.md](AGENTS.md), teknoloji kararları
[docs/decisions.md](docs/decisions.md), mevcut mimari ve veri akışı
[Sistem Analizi](docs/sistem-analizi.md) içindedir. ADR-09 uyarınca frontend geçişi
ilke olarak onaylıdır; uygulama aşaması açıkça yetkilendirilmelidir.

## API değişikliklerini koordine etme

1. Frontend özelliği öncesi gereken davranışı ve docs/api.md sözleşmesini incele;
   backend kaynaklarına yalnızca mevcut davranışı anlamak için bak.
2. Gereken uçları uygulanmış, planlı veya eksik olarak sınıflandır; kanıtını belirt.
3. Yeni/değişen sözleşme önerisini issue/PR içinde açıkça **öneri** olarak yaz:
   HTTP yöntemi/yolu, parametreler, istek/yanıt şemaları, durum kodları ve
   hata koşulları, doğrulama, güvenlik, sürümleme ve geriye uyumluluk etkileri.
4. Python/backend uygulama alan sahibiyle koordine et; gereken uygulama ve test işini ona aktar.
   Kabul edilen sözleşmeyi docs/api.md içinde incelemeyle güncelle; planlı ve
   uygulanmış durumunu açık tut. Sessiz veya kırıcı sözleşme değişikliği yapma.
5. Uygulama ve doğrulama kanıtı gelmeden ucu kullanılabilir sayma. Mock gerekiyorsa
   sentetik olduğunu ve eksik entegrasyonu belirt; üretim yanıtı olarak sunma.

request_id tekilleştirmesi, bariyer durum geçişleri ve alan boşluğu güvenlik
kuralları korunur. Frontend hiçbir akışta backend kararlarını veya fiziksel
güvenlik denetimlerini atlayamaz. Sözleşmeler frontend framework'ünden bağımsızdır.

## PR ve inceleme

PR başlığı somut değişikliği anlatsın. Açıklamada ilgili issue/görev, problem ve sonuç,
değişen kapsam, kabul ölçütlerinin durumu, doğrulama komutları/sonuçları,
kalan sınırlar ve ekip bağımlılıkları bulunsun. UI değişikliğinde ilgili
ekran/durum kanıtını ekle; özel veri kullanma. Bir PR tek anlaşılır iş taşımalı.

En az bir ekip arkadaşı incelemeden birleştirme. API veya alanlar arası işlerde
etkilenen alan sahibinin incelemesi de gerekir. İnceleyen kapsamı, mimariyi,
sahipliği, uyumluluğu, güvenliği ve kabul kanıtını kontrol eder. İlgili kontroller
geçmeli, engelleyici yorumlar çözülmeli; eksik entegrasyon tamamlanmış sayılmamalı.
Ekip hesabı/izinleri üyeler belli olduğunda ayarlanacak. Bu kurallar inceleme
sorumluluğudur; otomatik branch protection veya CODEOWNERS tanımlandığı anlamına gelmez.
Codex yalnızca açık kullanıcı talimatıyla commit/push/merge yapar.

## Birleştirme öncesi doğrulama

Kod veya belge değişikliği tek başına tamamlandı kanıtı değildir. Doğrulama komutunu,
çekim koşulunu, test çıktısını veya donanım gözlemini ekle. AI ile üretilen kodu
incele ve çalıştır. Sentetik test sonucunu gerçek OCR ölçümü olarak sunma.

- `git status --short` ile üç kapsamı ayrı belirle: izlenen unstaged değişiklikler,
  staged değişiklikler ve izlenmeyen yeni dosyalar. `git diff` ve
  `git diff --check` unstaged; `git diff --cached` ve `git diff --cached --check`
  staged kapsam için incelenir. İlgisiz dosya/bağımlılık değişikliği olmamalı.
- Normal diff komutları izlenmeyen dosyaları içermez. Her yeni dosyanın tam
  içeriğini ayrıca oku; `git ls-files --others --exclude-standard` ile listele.
  Metin dosyası için `git diff --no-index -- /dev/null YENI_DOSYA` ile içeriği,
  `git diff --no-index --check -- /dev/null YENI_DOSYA` ile whitespace'i denetle
  (YENI_DOSYA yerine gerçek yolu yaz, boşluk içeren yolu tırnakla).
  İçerik farkı nedeniyle çıkış kodu 1 normaldir; whitespace tanısı ve diğer
  hatalar ayrıca incelenmelidir. Metinlerde tutarlı satır sonu ve son newline'ı
  doğrula; yeni Markdown belgeleri UTF-8 ve LF kullanır. Kontrol için stage etme.
- Belge işinde bağlantı/dosya varlığı, sahiplik, teknoloji ve plan/uygulama
  tutarlılığı denetlenir. Yalnızca belge değişikliğinde uygulama testlerini
  gereksiz yere tekrar çalıştırmak gerekmez.
- Yetkilendirilmiş Python davranış değişikliğinde README'deki unittest,
  sentetik karar deneyi ve compileall kontrolleri çalıştırılır; gerekli
  regresyon kapsamını Python alan sahibi sağlar. CI bu kontrolleri Python
  3.10/3.12 üzerinde ve Rust çekirdeğinin testlerini ayrı işte çalıştıracak şekilde tanımlıdır.
- Yetkilendirilmiş firmware işinde mevcut Cargo testleri ve etkilenen gerçek
  cihaz davranışı doğrulanır; durum çekirdeği testleri donanım doğrulaması değildir.
- Gelecekteki frontend geçişinde typecheck, lint, build ve uygun frontend
  test komutları ayrıca tanımlanır; bugün böyle bir araç zinciri yoktur.
  Özellik kabulü API hata/boş/yükleniyor/başarı durumlarını, klavye/erişilebilirlik
  ve duyarlı görünümü kapsar. Backend değişikliği gereksinimi alan sahibine aktarılır.
- Çalıştırılan komutu, ortamı ve sonucu yaz. Çalıştırılamayan kontrolü nedeni ve
  etkisiyle belirt; CI tanımı veya eski rapor yeni çalıştırma kanıtı değildir.

## Kanonik belgeler ve güncelleme

| Kaynak | Sorumluluk |
|---|---|
| [README.md](README.md) | Proje özeti ve kurulum |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Katkı, geliştirme, PR ve inceleme süreci |
| [AGENTS.md](AGENTS.md) | Codex talimatları ve repository koruma kuralları |
| [docs/api.md](docs/api.md) | Framework'ten bağımsız API sözleşmesi |
| [docs/decisions.md](docs/decisions.md) | Mimari ve teknik kararlar |
| [docs/project-spec.json](docs/project-spec.json) | Yapılandırılmış kapsam ve uygulama durumu |
| [docs/sistem-analizi.md](docs/sistem-analizi.md) | Gereksinimler, mimari akış ve kabul ölçütleri |
| [docs/proje-raporu.md](docs/proje-raporu.md) | Proje raporu ve planlanan teknik yön |
| Kaynak kod, tests/ ve .github/workflows/ci.yml ile çalışma sonuçları | Gerçek uygulama ve doğrulama kanıtı |

Değişiklik ilgili kanonik belgeye yansıtılır; aynı sözleşme veya kural başka
belgelere kopyalanmaz, bağlantıyla gösterilir. Türkçe anlatımı ve mevcut karar
tablosu biçimini koru. Rapor hedefi, kaynak kod davranışı ve doğrulama sonucu
birbirinin yerine geçmez. Çelişkileri kanıtıyla bildir; ekip kararlarını sessizce ezme.

Ortak Drive belgeleri ekip tarafından düzenlenebilir. Repository'ye rapor aktarırken
güncel Drive sürümünü kontrol et; eski kopyayla ekip değişikliklerini ezme.
PR incelemesi kod için, ortak Drive güncel çalışma belgeleri için kullanılır.

## Güvenlik ve engeller

Öğrenci numarası, gerçek plaka fotoğrafı, token veya Wi-Fi şifresi commit etme.
Yeni dış veri veya bağımlılık için kaynak/lisans ve sürüm bilgisi ekle.
Demo yalnızca loopback'te kullanılır; üretim kimlik doğrulaması yoktur. İnternete
açılmaz veya gerçek bariyere bağlanmaz. Manuel alan boşluğu gerçek sensör
doğrulaması, izin kararı gerçekleşmiş geçiş kaydı değildir.

Engeli issue/PR veya teslim raporunda bildir: gereken davranış, mevcut kanıt,
etkilenen kabul ölçütü, sorumlu alan ve gereken karar/aksiyon. Kapsam dışı dosyayı
değiştirerek engeli aşma; bağımsız ve yetkili işlere devam et.

## Teslim raporu

Tamamlanan kapsamı, değişen dosyaları, doğrulama sonuçlarını, açık sorunları ve
sonraki adımı kısa yaz. Göreve özel rapor biçimi varsa onu izle. Mevcut uygulama,
planlanan geliştirme ve doğrulanmamış işlevleri ayır; ilgisiz rapor bölümleri ekleme.
