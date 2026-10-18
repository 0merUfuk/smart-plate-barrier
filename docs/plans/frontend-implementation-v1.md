# Frontend uygulama planı — V1

18 Ekim 2026. **İncelemeye sunulan plan; uygulama yetkisi değildir.**
Resmî repository: https://github.com/0merUfuk/smart-plate-barrier.
PR #3'ün merge edildiği güncel main `0ed2625632d5d06e07ee3c090dec08f36e63bd47`
incelendi; çalışma dalı `docs/frontend-implementation-plan`, başlangıç ağacı temiz.
Bu görevde yalnızca bu belge oluşturulur; aşağıdaki dosyalar/komutlar gelecekteki
ayrı yetkilendirilmiş işlerin önerileridir, şimdi oluşturulmuş veya çalıştırılmış değildir.

## 1. Yönetici özeti

V1 önerisi: web/ içinde App Router, strict TypeScript ve semantik Tailwind
tokenları; tek `/` sayfası ve gerçek bölüm bağlantıları; tarayıcıda çalışan
tek dashboard veri sahibi; küçük sunum bileşenleri ve tek API istemcisi.
Python karar/kayıt otoritesi olarak kalır. Yeni business API, Next.js Route
Handler/Server Action iş katmanı, SQLite bağlantısı veya OCR kodu eklenmez.

Yerel bağlantı önerisi Next.js rewrites üzerinden Python'a aynı-origin API
yönlendirmesidir. **Bu tek başına POST'u çalıştırmaz:** mevcut Python Origin
kontrolü frontend portunu reddeder. Python ekibinin dar yerel allowlist onayı
ve gerçek tarayıcı/proxy deneyi mutasyon aşamalarının ön koşuludur.
Onay gelene kadar iskelet/görsel işler ve açıkça sentetik fixture testleri
ilerleyebilir; entegrasyon hazır sayılmaz, üretim verisi uydurulmaz.

Plan sırası: bağımlılık kararları → iskelet → görsel kabuk → salt okuma →
kayıtlar/grafik → simülasyon mutasyonları → izinli liste → erişilebilirlik ve
regresyon. Her faz ayrı küçük iş/PR; bağımsız inceleme için bölüm 10'u kullan.

## 2. Mevcut frontend ve hedef

| Alan | Mevcut kanıt | Hedef V1 |
|---|---|---|
| Arayüz | [index.html](../../web/index.html), [app.js](../../web/app.js), [style.css](../../web/style.css): vanilla, Türkçe, koyu demo | Onaylı [tasarım sözleşmesine](../design/README.md) uyan açık dashboard; henüz yok |
| Barındırma | [server.py](../../backend/server.py): yalnız `/`, `/app.js`, `/style.css` dosyalarını sunar | Ayrı Next.js yerel süreci; Python statik sunucusu Next build'i sunabilir varsayılmaz |
| API | Stdlib HTTP, loopback, SQLite; [api.md](../api.md) | Aynı domain kurallarını tüketen frontend; FastAPI geçişi ayrı backend işi |
| Veri | Sentetik gözlem, kalıcı izin/deneme kayıtları, sanal durum | Aynı veri, açık simülasyon etiketleri ve sınırlı pencere özetleri |
| Araçlar | package.json/Node frontend araç zinciri yok; CI Python/Rust | Node araçları yalnız gelecekte yetkilendirilmiş frontend fazında web/ içine |

**Vanilla dosyalarının geçişi:** planlama sırasında hiçbiri değişmez. Gelecekte
faz 1–8 boyunca mevcut üç dosya aynı yerde ve aynı içerikle tutulur; Python
8080 üzerindeki demo geri dönüş yolu olarak çalışır. Next `src/app/` kendi
3000 portunda `/` sunar; eski dosyalar `public/` içine kopyalanmaz, JS/CSS'i yeni
sayfaya yüklenmez. CSS ve DOM event bağlama kodu doğrudan taşınmaz; davranış
testleri korunarak yeniden yazılır. Legacy kaldırma/taşıma ve Python statik
eşlemesini değiştirme V1 temizliğinin otomatik parçası değildir; ayrıca alan
sahibi kararı ve kapsam yetkisi gerektirir. Kalıcı ikinci frontend hedeflenmez.

## 3. Onaylı mimari sınırlar

[AGENTS.md](../../AGENTS.md), [CONTRIBUTING.md](../../CONTRIBUTING.md) ve
[ADR-01–09](../decisions.md) geçerlidir. Frontend Next.js + React + TypeScript +
Tailwind CSS ile web/ içinde kalır; genel klasörler ve sistem mimarisi korunur.
Frontend/API sözleşmesi ekibi UI/istemci ve sözleşme önerisini üstlenir.
Python/FastAPI uygulaması, SQLite kalıcılığı, Python testleri, OCR/OpenCV/EasyOCR,
firmware ve donanım kaynakları ilgili alan sahiplerinin işidir.

Redux/Zustand, query framework'ü, UI kit, tablo/grafik kütüphanesi veya monorepo
aracı V1 için önerilmez. React state/reducer, native fetch, semantik HTML,
native dialog ve küçük CSS çubuk grafiği yeterlidir. Gereksinim çıkmadan ek
katman, genel repository/service deseni veya uygulama çapında store kurulmaz.
UI doğrulaması kullanıcıya yardım eder; izin kararı veya bariyer geçişi hesaplayamaz.

## 4. Önerilen frontend yapısı

Aşağıdaki ağaç **gelecek hedefidir**; dosyalar yalnız ilgili fazda gerektiğinde açılır:

```text
web/
  index.html, app.js, style.css         # mevcut demo; korunur
  package.json, package-lock.json      # tek npm paketi/lockfile; workspace yok
  tsconfig.json, next-env.d.ts          # strict; Next'in ürettiği tip bildirimi
  next.config.ts, postcss.config.mjs
  eslint.config.mjs, .gitignore         # .next/node_modules/test çıktıları yerel ignore
  vitest.config.ts, playwright.config.ts
  src/
    app/
      layout.tsx, page.tsx, globals.css
      error.tsx                       # render hatası sınırı; fetch durumundan ayrı
    components/
      app-shell.tsx, sidebar.tsx, page-header.tsx
      ui/button.tsx, ui/card.tsx, ui/dialog.tsx, ui/feedback.tsx
    features/dashboard/
      dashboard.tsx, use-dashboard.ts, selectors.ts
      barrier-status-card.tsx, summary-cards.tsx
      decision-distribution.tsx, recent-observation.tsx
      access-attempts.tsx, allowed-plates.tsx
      observation-form.tsx, area-clear-confirmation.tsx
    lib/api/
      client.ts, types.ts, decode.ts
  e2e/                                # frontend entegrasyon/proxy senaryoları
```

Unit/component testleri ilgili dosyanın yanında `*.test.ts(x)` olur; kök
tests/ Python alanına frontend testleri eklenmez. Tek kullanımlık hücre/buton
wrapper'ları açılmaz; `ui/` yalnız gerçek tekrar eden desenleri barındırır.
`public/` ancak yerel, lisansı uygun varlık gerekirse eklenir; harici font ve
Parkora görseli zorunlu değildir. Scaffold mevcut web/ üzerine körlemesine
çalıştırılmaz: gerekli dosyalar kontrollü eklenir, legacy içerik karşılaştırılır.

- **App Router:** layout/page varsayılan server bileşenleri olarak statik kabuğu
  kurar; Dashboard istemci sınırıdır. API ilk okuması mount sonrası tarayıcıda;
  build sırasında Python'a istek yok, server/client arasında ikinci cache yok.
  Statik içerik ve interaktif küçük parçalar ayrılır; bütün uygulamaya gereksiz
  `use client` yayılmaz. Route `loading.tsx` istemci fetch skeleton'ı yerine geçmez.
- **Tip/validasyon:** `client.ts` transport ve altı endpoint çağrısı; `types.ts`
  ortak DTO/union'lar; `decode.ts` unknown JSON için küçük açık type guard'lar.
  Başlangıçta schema kütüphanesi gerekmez. `any`, kontrolsüz cast ve eksik sayıyı
  0'a çevirme yok. DTO'lar bölüm 7–9 onayı sonrası sabitlenir; tarih/sonlu sayı,
  enum ve zorunlu alan bozuksa uyumsuzluk sonucu üretir. Ek alanlar tolere edilir.
- **Veri sahibi:** tek `use-dashboard` son iyi snapshot, health, okuma durumu,
  fetchedAt, mutasyon kilidi ve son scan yükünü tutar. Form alanları kendi
  bileşenindedir. Props/callback yeterli; provider ancak gerçek ihtiyaçta.
- **İstemci:** göreli `/api/...`, GET'te no-store, JSON POST, sonlu timeout;
  HTTP, bağlantı, timeout, JSON/protokol ve domain kararını ayrı sonuçlar olarak
  döndürür. Hata gövdesi JSON değilse güvenli genel mesaj; HTML veya hata metni
  DOM'a HTML olarak basılmaz. Herhangi bir POST otomatik retry edilmez.
- **Tema:** globals.css'te tasarım tokenları; seçilecek Tailwind sürümünde
  desteklenen tema eşlemesiyle semantik utility'ler. Tailwind v4 seçilirse
  CSS `@theme` eşlemesi uygundur; mevcut token değerleri yeniden icat edilmez.
  Tablet/desktop eşikleri tasarım şartnamesinden gelir; varsayılan `lg`
  breakpoint'i sözleşmeyle aynı sanılmaz. Native CSS küçük özel desenlerde yeterlidir.

## 5. Tasarımdan bileşene eşleme

Görsel değerlerin tek kaynağı [design-system.md](../design/design-system.md);
oran/yerleşimin kaynağı [layout-spec.md](../design/layout-spec.md). Aşağıdaki
tablo bunları tekrar tanımlamaz. “B” [component-spec.md](../design/component-spec.md),
“O” [Overview şartnamesi](../design/pages/overview.md) anlamındadır.

| Bileşen | Sorumluluk / veri | Yeniden kullanım | Durum/etkileşim | Görsel referans |
|---|---|---|---|---|
| AppShell / Sidebar | Full-bleed tuval, bölüm hedefleri; API yok | Sayfa kabuğu | Hash/aktif link, mobil menü, skip link; çevreleyen panel yok | Layout; B Sidebar |
| PageHeader | h1/proje adı; mode, version, fetchedAt | Ortak başlık | Yenileme, busy/eski/bilinmiyor; sağlık ayrı | B Header; O Header |
| Dashboard | Kart kompozisyonu; tek snapshot sahibi | V1 sayfa düzeni | Props/callback bağlar; tek primary aksiyon hiyerarşisi | O sıra/grid |
| BarrierStatusCard | Güncel state.barrier/mod; fiziksel veri iddiası yok | Domain'e özgü | Açık/kapalı/bilinmiyor/eski; geçmiş event durumunu kullanmaz | B Durum/Bilgi; O üst kart |
| SummaryCards | N, allow adedi, allowlist.length; selectors | Tek ortak metric kart deseni | Loading/0/error ayrımı, pencere/payda etiketi | B Metrik; O üçlü özet |
| DecisionDistribution | Dört kararın adetleri | Domain'e özgü | N=0 boş; metin listesi + CSS çubukları; filtre dışı pencere | B Grafik; O analiz |
| RecentObservation | events[0], zaman, reason, sentetik güven | Domain'e özgü | Kayıt yok/unknown/uzun metin; salt okuma | B Bilgi; O yan kart |
| AccessAttempts | events; yerel plaka/karar filtresi | Aynı satır verisi desktop/mobil | İlk 10/tüm yüklüler, X/N; grafik sayıları değişmez; gerçek bölüm hedefi | B Tablo/Filtre; O geçmiş |
| AllowedPlates | allowed_plates; add/remove sonuçları | Tek yönetim bölümü | Pending kilidi, ekle, hedefi belirtilmiş silme teyidi; yeni snapshot | B Dialog; O izinli liste |
| ObservationForm | scan isteği ve sonucu | Tek simülasyon akışı | Alan hatası, pending, belirsiz sonuç; kimlik/yük korunur, tekrar açık aksiyon | B Gözlem; O aksiyonlar |
| AreaClearConfirmation | Taze barrier ve kullanıcı teyidi | Tek domain teyidi | Açıkta etkin, bilinmiyor/eski/pending'de kapalı; otomatik kapanma yok | B Dialog; O manuel boşluk |
| Button/Card/Dialog/Feedback | Ortak yüzey, etkileşim, odak ve durum metni | Gerçek paylaşılan desenler | Dialog aç/kapat/ESC/odak dönüşü; skeleton, empty, error, stale ayrı | B Buton/Boş/Hata; tokenlar |

Gözlem formu Simülasyon bölümündeki gerçek bir aksiyonla dialog olarak açılır;
anchor hedefi dialogun gizli içi değil görünür bölüm başlığıdır. İzinli liste
ekleme formu bölüm içinde, silme teyidi ortak Dialog ile sunulur. Dialog için
native HTML öğesinin odak/ESC/aria davranışı test edilir; UI kit eklenmez.
Full-bleed, borderless sidebar, floating-island, siyah hap primary ve kontrollü
mavi vurgu kabul koşuludur; birden çok kartı saran dev beyaz panel yoktur.

## 6. Sayfa ve navigasyon kararı

| Ölçüt | A: Tek Overview + anchor | B: Bağımsız sayfalar |
|---|---|---|
| Kullanım | Durum, son karar ve simülasyon aynı bağlamda | Büyük kayıt/liste işlerinde odak avantajı |
| Maliyet/veri | Tek snapshot, az geçiş ve tek stale-state sahibi | Aynı state için cache/yenileme paylaşımı gerekir |
| Görsel tutarlılık | Onaylı Overview kompozisyonunu doğrudan korur | Ortak kabuk ve ek sayfa tasarımları gerekir |
| Büyüme | Kapsamlı kayıt/filtre gelince bölümler ayrılabilir | Tam geçmiş API'si olmadan ek sayfa faydası sınırlı |

**V1 seçimi A:** `/` üzerindeki `#genel-bakis`, `#erisim-denemeleri`,
`#izinli-plakalar`, `#simulasyon`. Gerçek görünür bölüm id'leri, `<a>` bağlantıları,
erişilebilir bölüm başlıkları ve mobil menü kapanınca hedefe anlaşılır odak akışı.
Hash ile deep-link/back/forward kontrol edilir; başlangıç aktif hedefi ve
`aria-current` uygun güncellenir. Ölü menü, sahte kullanıcı/ayar/fatura alanı yok.
Bölüm bileşenleri ileride route'a taşınabilir; bugünden çoklu route mimarisi kurulmaz.

## 7. API sözleşmesi denetimi

Kanonik kaynak [docs/api.md](../api.md) aynen korunur. Aşağıdaki **K** = belgelenmiş
ve kaynakta uygulanmış; **S** = kaynakta var fakat ayrıntılı sözleşme onayı eksik;
**Ö** = öneri/alan sahibi işi; **Y** = desteklenmeyen işlev. S yapıları yeni
resmî schema sayılmaz. Kaynaklar [server.py](../../backend/server.py),
[store.py](../../backend/store.py), [domain.py](../../backend/domain.py);
test kanıtının kapsamı [test_demo.py](../../tests/test_demo.py) içinde incelendi,
bu planlama sırasında testler yeniden çalıştırılmadı.

### Ortak HTTP kuralları ve hata ayrımı

- **K:** POST application/json, gövde en fazla 8192 bayt; durum kodları
  400/403/404/409/413/415; UTC tarihler ve scan tekilleştirmesi.
- **S:** her başarılı uç 200 JSON döndürür. POST gövdesi JSON object olmalı;
  clear için de `{}` gönderilir, boş gövde olmaz. Kontrol sırası Origin →
  Content-Type → Content-Length/gövde → endpoint. JSON hatası/yanlış tip 400;
  geçersiz sayısal Content-Length 400, eksik/0/negatif/>8192 uzunluk 413.
  JSON Content-Type parametresi kabul edilir. Hata gövdesi `{error: string}`;
  alan bazlı hata kodu/şeması tanımlı değil, metne göre iş mantığı kurulmaz.
- **S:** Origin varsa yalnız sunucunun kendi portundaki tam `http://127.0.0.1`
  veya `http://localhost` origin'i kabul edilir; yoksa bu kontrol reddetmez.
  Bu kimlik doğrulama değildir. GET'te aynı Origin filtresi yoktur; CORS yanıt
  başlıkları ve özel OPTIONS handler yok. Şu an preflight'lı doğrudan tarayıcı
  bağlantısı hazır değildir. Yanıtlar no-store; bağlantı timeout'u 5 saniye,
  SQLite timeout'u 10 saniye; uçtan uca süre garantisi belgelenmemiştir.
- **Ö:** proxy'nin HTML/502/504 yanıtı, bağlantı kesilmesi veya beklenmeyen 5xx
  işlenmeli; backend bunları standart JSON sözleşmesiyle garanti ediyor denmez.

| Endpoint | Belgelenen istek/yanıt (K) | Kaynakta ayrıntı (S) | Frontend kullanımı / koordinasyon |
|---|---|---|---|
| GET /api/health | Gövdesiz; sürüm ve simulation modu | `{status:"ok", version:"0.1.0-demo", mode:"simulation"}`; başka health/error schema yok | Header; version/status şeması D1 ile teyit, cihaz sağlığı diye sunma |
| GET /api/state | Gövdesiz; izinli plakalar, sanal durum, son 50 gözlem ve 20 hareket | mode, real_ocr=false, physical_hardware=false, barrier, allowed_plates, events, actions. events rowid DESC, actions id DESC; plaka listesi sıralı; toplam/pagination yok | Bütün okuma kartları; ayrıntılı iç içe schema ve tutarlılık D1/D4 |
| POST /api/demo/scan | request_id, plate, confidence, fault; karar/reason/barrier/action/duplicate/mode/created_at; 409 farklı yük | Yanıta request_id, normalize plate ve confidence da dahil. fault varsayılan none, plate eksikse boş metin; güven ve request_id zorunlu. Tüm allow/deny/unreadable/error kararları HTTP 200 olabilir | Form/replay; transport başarısı allow değildir. Tüm alan/reason/enum'lar D1/D3 |
| POST /api/demo/clear | Manuel alan boşluğu; ayrıntılı request/response şeması yok | Gövde `{}` yeterli; içerik kullanılmaz. `{barrier, barrier_action, mode}`. Kapalıyken none, açıkken close; events'e scan kaydı eklemez | Sanal teyit; etkinlik taze durumdan, pending sonrası yeniden oku. D1/D3/D4 |
| POST /api/plates/add | Sentetik plaka ekleme; şema ayrıntısı yok | `{plate:string}` → `{plate:normalize_deger, added:true}`; INSERT OR IGNORE. true gerçek yeni satır eklendiğini kanıtlamaz | Liste ekleme; sonuç sonrası GET state. Doğrulama ve added anlamı D1/D3 |
| POST /api/plates/remove | İzinli plaka silme; şema ayrıntısı yok | `{plate:string}` → `{plate:normalize_deger, added:false}`; eksik plaka da başarılı yanıt alır, affected count yok | Hedef teyitli silme; false bir hata değildir. Aynı schema/hata konuları D1/D3 |

### Kaynaktan çıkarılan şema ayrıntıları — onay bekliyor

- State events öğesi kaydedilmiş scan yanıtıdır: request_id, plate, confidence,
  decision, reason, duplicate, barrier, barrier_action, mode, created_at.
  Snapshot'ta kayıtlı duplicate değeri ilk yanıtın false değeridir; geçmişten
  tekrar istek oranı türetilmez. actions öğesi id/action/created_at taşır.
- scan request_id ASCII harf/rakam/alt çizgi/tire, 1–64 karakter. confidence
  boolean olmayan sonlu sayı [0,1]. fault none/ocr_error/network_timeout;
  bilinmeyen değer 400. Plate ham metin en çok 32 karakter; boşluklar kaldırılır,
  büyük harfe dönüştürülür; O/0 veya yaklaşık eşleşme yapılmaz.
- Scan'de biçimsiz/boş plaka geçerli gözlem olarak unreadable üretebilir;
  bu durum 400 diye yeniden tanımlanmaz. Hata senaryosu önce değerlendirilir.
  Add/remove aynı normalizasyon sonrası demo plaka desenine uymayı gerektirir;
  aksi 400. Frontend ulusal plaka standardı veya backend iş doğrulaması yazmaz.
- Aynı request_id + normalize plate/confidence/fault aynıysa eski karar/zaman,
  güncel barrier, duplicate=true ve action=none gelir. Farklı yük 409;
  yeni kayıt/hareket yok. Başka alanlar şu an payload karşılaştırmasına dahil
  değil; bu, gelecekteki sözleşme garantisi olarak kullanılmaz.
- reason şu an exact_match/not_in_allowlist/low_confidence/invalid_plate_format/
  ocr_error/network_timeout değerlerini alır; sabit enum olup olmadığı onay bekler.
  API istemcisi bilinmeyen reason'ı güvenli düz metinle gösterebilir; bilinmeyen
  decision/barrier/action başarıya dönüştürülemez.

**Ö:** ayrıntılı DTO/hata sözleşmesi ve dar yerel Origin yapılandırması.
**Y:** server-side tarih/plaka filtresi, tüm zamanlar toplamı, pagination,
canlı stream, fiziksel telemetri, gerçek JPEG/OCR ucu, doluluk/gelir/rezervasyon.
Bunlar V1 için yeni endpoint icat etmeyi gerektiren onaylar olarak yorumlanmaz.

## 8. Next.js ↔ Python entegrasyon önerisi

### Seçenek karşılaştırması

| Seçenek | Mevcut sunucuyla sonuç | Değerlendirme |
|---|---|---|
| Tarayıcı 3000 → doğrudan Python 8080 | Farklı origin; JSON POST preflight/Origin engelleri, GET için CORS eksik | Python ekibinden hem CORS/OPTIONS hem Origin politikası ister; V1 için fazla yüzey |
| Next.js göreli `/api` rewrites → 8080 | Tarayıcı aynı-origin görür; Python'a iletilen Origin 3000 ise POST 403 | **Tercih edilen**, dar backend Origin onayı ve deney koşuluyla; yeni süreç/dependency gerekmez |
| Ayrı yerel reverse proxy → Next + Python | Tek tarayıcı origin'i, fakat Python hâlâ dış portu reddedebilir | Ek süreç/kurulum; güvenlik sorunu kendiliğinden çözülmez, ihtiyaç yokken ekleme |
| Next Route Handler/BFF veya Origin'i silme/değiştirme | Kontrolü görünmez aşabilir, iş API'sini çoğaltabilir | Reddedildi; bu proje için çözüm değil |

Tercih edilen gelecek topoloji: tarayıcı **http://127.0.0.1:3000**, Next dev
loopback:3000, Python loopback:8080. Tarayıcı altı mevcut API yoluna göreli
istek atar; next.config.ts sabit `http://127.0.0.1:8080` upstream'ine yalnız bu
altı yolu yönlendirir. Kullanıcı girdisinden hedef URL/host türetilmez; genel
açık proxy oluşturulmaz. Next config yalnız transport yönlendirir, karar/veri
işlemez. `next dev --hostname 127.0.0.1 --port 3000` gelecekteki dev script
önerisidir; port doluysa sessiz otomatik port değişimine güvenilmez.

**Python ekibi ön koşulu:** `http://127.0.0.1:3000` tam origin'inin yalnız yerel
geliştirmede açıkça yapılandırılabilmesini değerlendirmek; mevcut 8080 demo
origin'lerini ve yabancı-origin reddini korumak. Bu bir backend değişiklik
önerisidir, uygulanmış/onaylanmış değildir. Wildcard, regex ile bütün localhost
portları, Origin null veya tüm ağ arayüzlerini açmak önerilmez. Proxy Origin
başlığını olduğu gibi taşımalıdır; silme, 8080 gibi taklit etme veya sırf kontrolü
geçmek için server-side POST wrapper ekleme yok. Proxy başlık davranışı deneyde
farklı çıkarsa yaklaşım durdurulur ve alan sahipleriyle yeniden değerlendirilir.

`localhost` ve `127.0.0.1` farklı origin'lerdir; port/şema da origin parçasıdır.
V1 geliştirme adresi olarak 127.0.0.1 seçilir; localhost:3000 desteği istenirse
ayrı tam allowlist girdisi/onay/test gerekir, DNS/IPv6 davranışı varsayılmaz.
Host/X-Forwarded-* değişikliği mevcut kontrolü çözmez; kod Origin'i ve gerçek
server_port'u karşılaştırır. CORS tarayıcının cross-origin okumasını yönetir;
Python'ın mutasyon Origin politikası ayrı bir kontroldür.

Mevcut API'de cookie/session auth yoktur; client için credentials=omit önerilir,
token veya sahte kullanıcı modeli eklenmez. Proxy'ye ileride gelen cookie ve
Set-Cookie davranışı ayrıca incelenir; gelecekte auth eklenirse omit, CSRF ve
cookie domain/SameSite kararları yeniden tasarlanır. Origin eksik isteğin bugün
kabulü kimlik doğrulama değildir; istemci header silerek bunu kullanamaz.
Next API trafiği/cache ve mutasyon logları gerçek plaka/secret taşıyacak şekilde
tasarlanmaz; yalnız sentetik geliştirme verisi, geçici test DB'si kullanılır.

### Deneysel kabul kapısı — henüz çalıştırılmadı

Onaylı backend hazırlığı sonrası gerçek tarayıcı ve test DB ile şunlar kanıtlanır:

1. İki süreç yalnız 127.0.0.1'de dinler; tarayıcı istek URL'si 3000'de kalır,
   upstream 8080'dir; method/body/Content-Type/Origin ve hata kodu kayıpsız taşınır.
2. Onay öncesi 3000-origin POST 403'tür; açık yerel onay sonrası çalışır.
   Onaysız localhost/port ve example.invalid origin'leri yine 403 alır.
   Python alan sahibi izinli Origin davranışını kendi testleriyle doğrular.
3. JSON POST, bozuk gövde, 409 ve 413/415 yanıtları korunur; proxy HTML/502
   döndürürse UI güvenli hata verir. Tarayıcı cross-origin fetch'e yönlendirilmez.
4. İstek gövdesinin Content-Length'i doğru taşınır; proxy chunked aktarım yapıyorsa
   mevcut backend'in Content-Length zorunluluğuyla uyumu ölçülür. Yanıt uzunluğu
   ve gövdesi de tutarlı kalır. Uyumsuzsa sessiz
   header hilesi yok; Python ekibine taşıma sözleşmesi bağımlılığı bildirilir.
5. Proxy/body/bağlantı timeout'ları uyumludur; timeout POST'un uygulanmadığını
   kanıtlamaz. Yeniden deneme kuralları bölüm 11'deki gibi korunur.
6. Aynı-origin isteklerde CSP, script/style yüklenmesi ve güvenlik başlıkları
   kontrol edilir; API yanıtındaki stdlib CSP'si yeni Next HTML politikası
   sayılmaz. Dev HMR gereksinimi üretim için genel gevşetme gerekçesi değildir.

**Barındırma:** V1 yerel dev hedefidir. `next build` ve loopback `next start`
önizlemesi test edilir; rewrites Node süreci gerektiren bu öneride statik export
ile Python'ın sınırlı dosya sunumu eşdeğer değildir. İnternet/LAN yayını,
TLS, kullanıcı auth ve fiziksel cihaz bağlantısı bu planla yetkilendirilmez.

**FastAPI geçişi:** planned target olarak kalır; frontend başlangıcı için tüm
backend'i taşımak gerekmez. Python ekibi geçişi yaptığında altı ucun DTO,
HTTP/domain hata ayrımı, aynı DB/karar çekirdeği ve idempotency regresyonları
korunmalı. FastAPI varsayılan 422 doğrulaması mevcut 400 sözleşmesinin sessiz
değişimi olamaz. Direct cross-origin seçilirse CORS/OPTIONS ve mutasyon Origin
politikası birlikte tanımlanır; CORSMiddleware tek başına iş güvenliği değildir.

### Dış teknik kaynaklar

18 Ekim 2026'da resmi belgeler incelendi; kurulum fazında sürümler yeniden
kontrol edilip lockfile'a sabitlenir. Bu kaynaklar proje/API kararlarının yerine geçmez:

- [Next.js kurulum](https://nextjs.org/docs/app/getting-started/installation):
  App Router/TypeScript desteği ve ayrı lint komutu. Mevcut resmi rehberde
  Node alt sınırı 20.9; proje için desteklenen LTS ve uyumlu paket sürümleri
  faz 1'de seçilmeli, bu alt sınıra körlemesine runtime sabitlemesi yapılmamalı.
- [Next.js rewrites](https://nextjs.org/docs/app/api-reference/config/next-config-js/rewrites):
  dış hedefe URL proxy yeteneği. Bu belge Origin'in güvenlik kontrolüne uygun
  iletileceği garantisini vermez; yukarıdaki deney proje gereksinimidir.
- [Tailwind tema değişkenleri](https://tailwindcss.com/docs/theme): CSS tema
  tokenlarını utility'lere eşleme; değerlerin kaynağı proje tasarım sözleşmesidir.
- [FastAPI CORS](https://fastapi.tiangolo.com/tutorial/cors/): farklı origin ve
  açık izin listesi kavramı; mevcut stdlib sunucusunda bu middleware yoktur.
- [FastAPI hata işleme](https://fastapi.tiangolo.com/tutorial/handling-errors/):
  doğrulama hatalarının özelleştirilmesi; geçişte mevcut hata sözleşmesi korunmalıdır.
- [Vitest](https://vitest.dev/guide/), [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/),
  [Playwright web server](https://playwright.dev/docs/test-webserver): aşağıdaki
  test araçları için resmi dayanak; paketler bu görevde kurulmadı.

## 9. Python ekibi bağımlılıkları

Bunlar koordinasyon sorularıdır; bu görev dış ekibe mesaj göndermez veya
docs/api.md'yi güncellemez. Kabul edilen öneriler ilgili alan sahibi incelemesiyle
kanonik sözleşmeye daha sonraki ayrı işte aktarılmalıdır.

| Kimlik | Soru/öneri | Sahip / tamamlanma kanıtı | Bloke ettiği iş |
|---|---|---|---|
| D1 | Altı ucun tam request/response, zorunlu/opsiyonel alan, enum, boş liste ve hata şemaları kabul ediliyor mu? | API sözleşmesi ekibi önerir, Python ekibi kaynak/test ile teyit eder; docs/api.md onaylı güncellemesi | Gerçek veri decoder'ı ve faz 3–6 entegrasyonu |
| D2 | Yalnız yerel 127.0.0.1:3000 origin'ini açık yapılandırma ile kabul etme uygun mu; proxy method/body/Origin/length korunuyor mu? | Python ekibi güvenlik onayı ve testleri; frontend gerçek tarayıcı kanıtı | Tüm gerçek POST'lar; tamamlanmadan faz 5–6 hazır sayılamaz |
| D3 | scan request_id varsayılanları/409, duplicate'in güncel barrier + eski karar/zamanı, clear `{}` ve added bayrağının işlem yönü anlamı teyit ediliyor mu? | Python ekibi uç bazında örnek/test; API ekibi dokümantasyon | Mutasyon istemcisi ve kullanıcı sonuç metinleri |
| D4 | State'in zaman/sıra ve tutarlılık garantileri ne? Revision/snapshot timestamp yok; clear farklı sekmedeki yeni grant'e bağlanmış değil. | Python ekibi sınırları teyit eder; daha güçlü koşullu işlem gereksinimi ayrı öneri | V1'de fiziksel güvenlik iddiasını engeller; tek istemci kilidinin sınırları belgelenmeden kabul yok |

D4 için yeni version/If-Match endpoint'i varmış gibi davranılmaz. Mevcut simülasyon
kullanımı, dialog açarken son durum okuma ve tek istemci kilidiyle sınırlıdır;
başka sekme/cihaz yarışı frontend tarafından çözüldü diye sunulmaz. Güçlü atomik
snapshot/koşullu mutasyon gerekirse Python ekibinin ayrı sözleşme kararı gerekir.

## 10. Küçük ve incelenebilir uygulama fazları

Her faz birleştirmeden önce ilgili kontrolleri ve kalan bağımlılıkları raporlar.
Faz içeriği büyürse API istemcisi ve sunum işi ayrı PR'lara bölünür; sekiz fazı
tek Codex görevine toplama. Aşağıdaki testler gelecekteki kabul koşullarıdır.

### Hazırlık kapısı — geliştirme öncesi kararlar

- **Amaç/alan:** bu planın ekip incelemesi, D1–D4 koordinasyonu; kaynak değişikliği yok.
- **Çıktı/kabul:** faz 1 için açık uygulama yetkisi, araç sürümü seçme kapsamı;
  D1–D4 sahip/kanıt listesi. Backend kaynaklarına yetki verilmiş sayılmaz.
- **Doğrulama/risk/sınır:** kabul edilen/askıda kararlar ayrılır; eksik Origin
  onayı iskeleti engellemez ama gerçek mutasyon kapısını kapatır. Mimari yeniden tasarlanmaz.

### Faz 1 — iskelet ve araç zinciri

- **Amaç/alan:** web/ package/lock/config, `src/app/layout.tsx`, `page.tsx`,
  `globals.css` ve gerekli ignore; başka klasör yok.
- **Bağımlılık:** açık uygulama yetkisi; desteklenen Node LTS, Next/React/TS/Tailwind
  uyumu kontrol edilip sürümler kaydedilir. Tek npm lockfile; yeni runtime UI kütüphanesi yok.
- **Çıktı:** strict TS, ESLint, build/dev/start/typecheck/lint script'leri,
  küçük Türkçe “dashboard henüz uygulanmadı” başlangıç sayfası ve sistem fontu.
  Boş sayfayı tekrar eden unit test yazılmaz; test araçları ilk anlamlı ihtiyaçta eklenir.
- **Kabul/test:** temiz kurulumdan typecheck/lint/build geçer; Next loopback'te
  açılır, build Python olmadan çalışır. Legacy üç dosyanın diff'i sıfır, Python
  demosu çalışabilir kalır. `.next`, node_modules, test DB'si izlenmez.
- **Risk/sınır:** scaffold dosya ezmesi, Node uyumsuzluğu; dashboard, rewrite,
  gerçek API isteği ve backend değişikliği bu ilk fazın dışında.

### Faz 2 — tokenlar ve görsel kabuk

- **Amaç/alan:** globals.css, AppShell/Sidebar/PageHeader, ortak Button/Card,
  page kompozisyonu; yalnız ilgili frontend dosyaları.
- **Bağımlılık/çıktı:** faz 1; onaylı token eşlemesi, full-bleed, anchor hedefleri,
  mobil menü ve durum yer tutucuları. Örnek veri kullanılıyorsa açıkça sentetik.
- **Kabul/test:** hiçbir dev panel yok, bütün navigasyon hedefleri mevcut;
  dört hedef genişlikte görsel kanıt; menü/anchor/odak için gerekli RTL testleri
  Vitest/jsdom ile bu fazda eklenir, yalnız markup'ı tekrar eden test yazılmaz.
- **Risk/sınır:** Tailwind varsayılan breakpoint/radius sapması; veri hazırmış
  gibi sayı/bariyer gösterme yok. Gerçek API ve mutasyon yok.

### Faz 3 — API istemcisi ve salt okuma Overview

- **Amaç/alan:** lib/api, use-dashboard, selectors, durum/metric/son kayıt
  bileşenleri, gerektiğinde error.tsx; next.config.ts salt transport ayarı,
  gerçek GET/bağlantı testi için Playwright yapılandırması.
- **Bağımlılık:** D1; ayrı süreçler için onaylı yerel bağlantı düzeni. İlk GET
  deneyi yapılır; başarılı GET, POST Origin kapısı geçti demek değildir.
- **Çıktı/kabul:** health/state DTO guard'ları, son iyi snapshot ve ayrı health
  durumu, N/A/list count; bilinmeyen/eski/hata/boş ayrımı; API olmadan build.
- **Test:** client status/JSON/schema testleri, N=0/1/50 selectors, unknown enum,
  sıra dışı GET yanıtı ve hata sonrası stale; fixture ve gerçek GET kanıtı ayrı.
- **Risk/sınır:** eksik schema veya proxy header davranışı; D1 yoksa fixture
  geliştirme açık etiketlenir, gerçek veri entegrasyonu tamamlandı denmez. POST yok.

### Faz 4 — kayıtlar, dağılım ve yerel filtre

- **Amaç/alan:** AccessAttempts, DecisionDistribution, selectors ve testleri.
- **Bağımlılık/çıktı:** faz 3; ilk 10/tüm yüklüler görünümü, yerel plaka/karar
  filtresi, dört adetli erişilebilir CSS grafik; grafik kütüphanesi yok.
- **Kabul/test:** X/N doğru, filtre üst metrikleri değiştirmez; dört adet N'ye
  eşit, N=0 oran bölmesi yok; 50 kayıt tam DB diye sunulmaz. Uzun metin,
  mobil satır kartları ve gerçek tablo semantiği test edilir.
- **Risk/sınır:** sahte pagination/toplam/trend algısı; server filtreleri,
  tüm dönem raporu ve dışa aktarım yok.

### Faz 5 — sentetik gözlem ve sanal bariyer etkileşimleri

- **Amaç/alan:** ObservationForm, AreaClearConfirmation, Dialog, use-dashboard
  ve client POST parçaları; web/e2e proxy/scan/clear senaryoları.
- **Bağımlılık:** faz 3–4, D1/D2/D3 tamamlanmış; D4 sınırları kabul edilmiş.
- **Çıktı/kabul:** yeni gözlem/replay, manuel teyit, tek mutasyon kilidi, alan
  hataları, girdi/kimlik koruma. Duplicate sonrası kayıt/hareket artmaz;
  kapandıktan sonra replay yeniden açmaz; hiçbir iyimser bariyer hareketi yok.
- **Test:** gerçek tarayıcı POST Origin matrisi; izin→clear→replay, aynı id/farklı
  yük 409, açık bariyerde ret/hata; timeout/bağlantı kopması ve başarısız refresh.
- **Risk/sınır:** belirsiz POST veya birden çok sekme; clear için otomatik retry
  yok. Donanım/gerçek OCR, Python değişikliği ve güvenlik kontrolünü aşmak yok.

### Faz 6 — izinli plaka yönetimi

- **Amaç/alan:** AllowedPlates, Dialog ve add/remove client/testleri.
- **Bağımlılık/çıktı:** faz 5 transport/mutasyon kapısı, D1/D3; form, normalize
  sonuç gösterimi, silme hedef teyidi, başarı sonrası snapshot yenileme.
- **Kabul/test:** add-existing/remove-missing işlevi doğru metinle anlatılır,
  added bayrağı affected-row sanılmaz; duplicate submit engellenir, 400'de
  girdi korunur; remove sonrası liste/metric yeni snapshot ile güncellenir.
- **Risk/sınır:** başka sekmede liste değişimi; otomatik retry/optimistic liste
  yok. Kullanıcı/rol sistemi, toplu içe aktarma ve backend test değişikliği yok.

### Faz 7 — responsive, erişilebilirlik ve UX kabulü

- **Amaç/alan:** mevcut frontend bileşen/stil düzeltmeleri ve e2e testleri;
  yeni ürün kapsamı yok. Önceki fazlarda erişilebilirlik ertelenmiş sayılmaz.
- **Bağımlılık/çıktı:** faz 2–6; onaylı kırpımla kompozisyon karşılaştırması,
  metin/renk/odak/ekran okuyucu akışı, bütün veri ve hata durumlarının kanıtı.
- **Kabul/test:** 1440/1024/768/390 ekran görüntüleri, 320 reflow, %200 zoom,
  klavye, reduced-motion; kontrast hedefleri gerçek CSS üzerinde ölçülür.
- **Risk/sınır:** kırpımdan doğrulanmayan ölçü/fontu kaynak gerçeği sanmak;
  [tasarım README](../design/README.md) sınırı korunur. Tasarım değişikliği gerekirse
  ayrı inceleme; fiziksel sistem güvenliği onayı verilmez.

### Faz 8 — entegrasyon regresyonu ve teslim temizliği

- **Amaç/alan:** frontend e2e/fixture, tekrarlı veya kullanılmayan yeni frontend
  kodunun küçük temizliği; gerekiyorsa ayrıca yetkilendirilmiş README/CI işi.
- **Bağımlılık/çıktı:** faz 1–7 ve D1–D4 kanıtları; geçici SQLite DB ile tekrarlanır
  yerel senaryo, dev ve production build önizleme kanıtı, bilinen sınır raporu.
- **Kabul/test:** bütün frontend kapıları ve bölüm 11 güvenlik matrisi; mevcut
  Python/Rust CI sonuçları ayrıca incelenir. Kaynak değişmiyorsa testleri gereksiz
  tekrar etme; entegrasyon etkisi gerektirirse README Python kontrolleri çalıştırılır.
- **Risk/sınır:** CI'a frontend işi eklemek ayrı açık kapsam onayı ister; diğer
  ekip testlerini düzenleme yok. Legacy silme, FastAPI geçişi, deploy, merge ve
  yeni özellik yok. Eski demo sonraki kaldırma kararına kadar korunur.

## 11. Doğrulama stratejisi ve veri güvenilirliği

### Araçlar ve kalite kapıları

Minimum öneri: TypeScript/ESLint; unit ve istemci testleri için Vitest;
gerekli interaktif bileşenlerde React Testing Library + jsdom; gerçek tarayıcı/
görsel entegrasyonda Playwright. Bunlar yetkili fazlarda dev dependency olarak
eklenir; Redux/query/schema/chart/form/UI framework'ü gerektirmez. Ayrı axe
paketi başlangıçta zorunlu değil; gerekirse açık gerekçeyle değerlendirilir.

Gelecekte web/ içinde `npm run typecheck` (tsc --noEmit), `npm run lint`
(ESLint CLI), `npm run build` (next build), `npm run test` (vitest run) ve
`npm run test:e2e` (playwright test) tanımlanır. Next build lint yerine geçmez.
Temiz checkout'ta gereken Next üretilmiş tipler build/type generation ile
hazırlanır; henüz olmayan script'ler bugün çalışmış gibi raporlanmaz.
Frontend CI önerisi bu kapıları ayrı job'a taşımaktır; mevcut Python/Rust
workflow'u bu görevde değişmez ve frontend kontrolü var sanılmaz.

| Alan | Gelecekteki test / somut kabul |
|---|---|
| Types/lint/build | strict açık; gerekçesiz any yok; lint ayrı geçer; Python kapalıyken build başarılı |
| API client | Her altı uçta method/body/HTTP kodu/JSON/schema; 400/403/409/413/415, ağ hatası, bozuk JSON ve proxy HTML yanıtı; 200 decision=error HTTP başarısıyla karıştırılmaz |
| Component | Kart etiketleri, dört karar, modal odak/ESC/dönüş, filtre boşluğu, form alan hatası ve pending çift tık kilidi |
| Sınırlı metrik | N=0/1/50, allow sayısı, liste sayısı, dağılım toplamı; filtre üst özetin penceresini değiştirmez; pagination/toplam varsayılmaz |
| Idempotency | Aynı id/yük eşzamanlı tekrarında tek kayıt/hareket; aynı id/farklı yük 409; grant→clear→eski replay closed/none; mevcut Python test adları test_repeat_after_close_never_reopens/test_concurrent_duplicates_open_once referans alınır |
| Bariyer | Ret/unreadable/error yeni açma üretmez; açık bariyeri kapatmaz; clear manuel teyitli; UI fiziksel durum veya geçiş iddiası üretmez |
| Stale/race | Geç gelen GET mutasyon sonrası yeni snapshot'ı ezmez; hata son iyi veriyi stale gösterir, bilinmeyen enum mutasyonları kapatır; health arızası state başarısını silmez |
| Mutasyon belirsizliği | POST işlenip yanıt kaybolması; otomatik yeni scan kimliği yok, önceki yük korunur; clear/add/remove otomatik yeniden gönderilmez; başarılı POST + başarısız refresh ayrı mesaj |
| Proxy/Origin | Bölüm 8 deney matrisi; onaylı origin çalışır, foreign/yanlış port reddedilir; method/body/length/Origin ve status korunur; ayrı loopback süreçleri |
| Responsive/görsel | Sabit sentetik fixture ile 1440/1024/768/390 px; çevreleyen panel yok, kart oranı/boşluk sözleşmeye uygun. Grafik ve tablo mobilde okunur |
| Erişilebilirlik | 320px reflow, %200 zoom, menü/form/dialog klavye akışı, skip link, etiket/başlık sırası, renk+metin, kontrast ve reduced-motion |
| Gerçek entegrasyon | Yalnız geçici DB; GET ve altı uç akışı; Next build/start ile de dene; mock testi gerçek proxy/Origin kanıtı sayılmaz |

**Snapshot ve mutasyon düzeni:** ilk yüklemede health/state bağımsız sonuçlanır;
yalnız doğrulanmış state mutasyonları açabilir. Okuma sırası için request generation
ve AbortController kullanılır; eski generation yanıtı yok sayılır. Mutasyon
başlamadan önceki GET'ler geçersiz kılınır; bitince yeni GET ile uzlaşılır.
Snapshot ya son iyi veri + stale etiketi ya doğrulanmış yeni veri olarak gösterilir;
hatalı/eksik alanlar başarıya çevrilmez. Sabit polling/stream, tarayıcıda kalıcı
DB kopyası veya iyimser bariyer/liste güncellemesi önerilmez.

Yeni scan kimliği ve ham yük **göndermeden önce** session belleğine kaydedilir;
yanıt kaybında da aynı yük/kimlik kalır. Şu anki vanilla demo previous değerini
başarılı yanıttan sonra atar; bu eksikliği yeni arayüze kopyalama. Kullanıcının
açık “Aynı gözlemi tekrarla” eylemi dışında otomatik POST retry yok. Yeni gözlem
ayrı niyet ve yeni id demektir; 409'u yeni id üreterek gizleme. Sekme kapanırsa
session belleği kaybolur; belirsiz sonucu otomatik yeni gözlemle telafi etme.
Timeout/abort server işlemini iptal etti diye sunulmaz. Clear tekrarının başka
sekmedeki yeni grant'e denk gelmesi mümkündür; taze GET/teyit bunun atomik
güvencesi değildir. Sınır D4 kapsamında açık raporlanır.

Test fixture'ları yalnız sentetik plaka taşır; gerçek DB, fotoğraf, token veya
kişisel veri repository'ye/test artefact'larına eklenmez.
Erişim denemesi, doğrulanmış bir fiziksel araç girişi veya çıkışı değildir.
Bir `allow` kararı, aracın bariyerden fiziksel olarak geçtiğini kanıtlamaz.
Sanal bariyer durumu, fiziksel cihazdan alınmış telemetri değildir.

## 12. Riskler ve açık kararlar

| Risk / açık karar | V1 kararı veya gereken onay |
|---|---|
| D1/D2 henüz onaylanmadı | API schema teyidi ve yerel Origin politikası; frontend yetkisi Python kaynaklarına yayılmaz |
| Proxy değişmez garantisi yok | Seçilecek Next sürümünde gerçek tarayıcı/method/header/length deneyi kapısı; bu plan deney sonucu değildir |
| Node/paket/test aracı sürümleri | Faz 1'de desteklenen LTS ve uyumlu sürümler sabitlenir; dev dependency kapsamı ilk işte açıkça onaylanmalı |
| V1 navigasyon/araç seçimi | Tek route+anchor, native fetch/dialog ve küçük CSS grafik önerilerinin plan incelemesinde kabulü beklenir |
| Birden fazla istemci ve snapshot atomikliği | Revision garantisi yok; fiziksel güvenlik iddiası yok, güçlü garanti gereksinimi ayrı Python işi |
| Session kaybı / belirsiz POST | Scan id/yük gönderim öncesi bellekte; otomatik POST retry yok, kullanıcı girdisi korunur |
| Tarihsel CI kayıtları çelişkisi | README uzak CI geçti diyor; project-spec/raporlarda eski doğrulanmadı kayıtları var. Eski kanıtlar sessizce yazılmaz; yeni CI sonucu ayrı link/commit ile raporlanır |
| İki arayüzün geçici bakımı | Vanilla dosyalar korunur; kaldırma ve barındırma değişimi ayrıca onaylanır; faz 8'in gizli kapsamı olmaz |
| Sonraki fiziksel/üretim kullanım | Auth, gerçek OCR, donanım telemetrisi ve güvenli dağıtım bu V1 frontend planının dışında |

Bu plan için uygulamaya geçiş onayı henüz yoktur. Onay bekleyen başlıklar
kullanıcıya/alan sahiplerine inceleme girdisidir; bu belge onları uygulanmış
veya sessizce kabul edilmiş saymaz. Mevcut tasarım değerleri tekrar tasarlanmaz.

## 13. Önerilen ilk uygulama görevi

**İş:** “web/ içinde mevcut vanilla demoyu koruyarak minimal Next.js araç
zinciri kur.” Bu iş ancak plan incelemesi ve açık uygulama yetkisi sonrası açılır.

- **Kapsam:** yalnız faz 1 dosyaları; Next.js App Router, React, strict TS,
  Tailwind ve ESLint; uygun Node/paket sürümlerini
  seçip tek lockfile ile kaydet. React Compiler, ek UI/state/chart kütüphanesi yok.
- **Teslim:** loopback dev/start komutları, build/typecheck/lint script'leri;
  Türkçe, açıkça uygulanmamış dashboard başlangıç sayfası. Harici font/görsel yok.
- **Kabul:** temiz kurulumdan üç kalite komutu geçer; Python kapalıyken build;
  web/index.html, app.js ve style.css içerikleri byte düzeyinde aynı;
  kaynak/bağımlılık diff'i yalnız açık izinli frontend dosyalarında.
- **Kapsam dışı:** dashboard kabuğu ve kartları, API client/rewrite, gerçek veri,
  mutasyon, backend/API/design/CI değişikliği; commit/push/PR yetkisi iş
  talebinde ayrıca belirtilmedikçe verilmiş sayılmaz.

Planlama görevinin doğrulaması: kaynak/CI ve kanonik belgeler okunmuştur;
buradaki tarayıcı/uygulama testleri, paket kurulumları ve entegrasyon deneyleri
henüz yapılmamıştır. Bu dosya inceleme için bırakılır; uygulama başlatılmaz.
