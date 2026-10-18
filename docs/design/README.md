# Dashboard tasarım sözleşmesi

18 Ekim 2026. Bu dizin, yetkilendirilmiş frontend tasarım ve uygulama işleri için
bağlayıcı görsel kaynaktır. Belgeler hedef arayüzü tanımlar; mevcut vanilla demo
taşınmamıştır. Next.js kurulumu, sayfa uygulaması veya yeni API bu çalışma ile yapılmaz.

## Görsel temel ve kanıt sınırı

Birincil ve onaylı yön:
[Parkora — Dashboard Parking Management System](https://dribbble.com/shots/26532568-Parkora-Dashboard-Parking-Management-System),
Vektora UIUX / Vektora. Genel bir dashboard esini yerine bu kompozisyon temel alınır.

- **Kaynakta doğrulanan:** Dribbble başlığı, tasarımcı atfı ve yayımlanan altı renk.
- **Görsel olarak incelenen:** kullanıcının paylaştığı masaüstü kırpımı; solda dar
  ikon navigasyonu, üstte yatay arama, açık gri/lavanta zemin, kompakt bilgi
  hücreleri, yatay metrik kartları, geniş grafik ve dar yan kart ilişkisi.
- **Kullanıcı tarafından onaylanan uyarlama:** kesintisiz sayfa tuvali (full-bleed),
  çerçevesiz sidebar, bağımsız kartlar (floating-island), siyah hap biçimli ana aksiyon.
- **Doğrulanmayan:** özgün font, piksel ölçüleri, gölge parametreleri, tam sayfanın
  kırpım dışı bölümü, hover/odak davranışı ve tablet/mobil sürümler. Dribbble metin
  görünümü tam tasarım görselini sunmadı; erişilen görsel bağlantısı reklam varlığıydı.
  Ölçüler, durumlar ve responsive kurallar bu projenin önerilen tasarım değerleridir.

Kaynak görseldeki otomobil, logo, marka, işletim sistemi pencere düğmeleri ve
istatistikler ürüne taşınmaz. Üçüncü taraf görsel/font/logo indirilmez veya
repository'ye kopyalanmaz; atıf yeniden kullanım lisansı değildir.

## Tasarım ilkeleri ve durum

| Karar | Durum |
|---|---|
| Parkora kompozisyonuna sadakat; açık mod, full-bleed, çerçevesiz navigasyon ve bağımsız kartlar | Onaylı, zorunlu |
| Next.js + React + TypeScript + Tailwind CSS; web/ içinde frontend | ADR-09 ile onaylı hedef; uygulanmadı |
| Semantik tokenların sayısal değerleri, breakpoint'ler ve Overview yerleşimi | Bu belgelerde incelemeye sunulan uygulama önerisi; referanstan ölçülmedi |
| Fiziksel bariyer, gerçek OCR, global raporlama | Bu tasarımın uygulanmış işlevleri değil |

Tasarımın odağı erişim kararı ve sanal bariyerin anlaşılmasıdır. Bakış sırası:
mod/durum → gözlem aksiyonu → sınırlı veri özeti → dağılım ve son karar → kayıtlar.
Güvenlik açıklamaları görsel sadelik uğruna gizlenmez. Kart aralıkları ve içerik
hiyerarşisi Parkora'daki sakin yoğunluğu korur; kurgusal KPI alanlarıyla doldurulmaz.

**Yasak desenler:** tüm uygulamayı saran dev yuvarlak beyaz panel; sidebar ve
ana alanı içine alan ikinci kabuk; ağır gradient, cam/neon efektleri; rastgele
süslemeler; çoklu vurgu renkleri; tutarsız yarıçap; gereksiz animasyon; genel
bakışta sıkıştırılmış işletme tabloları. Doluluk, rezervasyon, gelir, gerçek
araç/giriş/çıkış sayısı ve ölçülmemiş başarı/gecikme istatistikleri eklenmez.

## Belge haritası ve sorumluluk

| Kaynak | Tek sorumluluk |
|---|---|
| [design-system.md](design-system.md) | Renk, tipografi, boşluk, köşe, efekt ve etkileşim tokenları |
| [layout-spec.md](layout-spec.md) | Tuval, navigasyon, grid ve responsive yerleşim |
| [component-spec.md](component-spec.md) | Yeniden kullanılabilir desenlerin durum, etkileşim ve erişilebilirlik davranışı |
| [pages/overview.md](pages/overview.md) | Sayfa hiyerarşisi, widget/veri eşlemesi ve kabul ölçütleri |
| [../api.md](../api.md) | Kanonik API sözleşmesi; tasarım belgeleri sözleşmeyi değiştirmez |
| [../decisions.md](../decisions.md) | Mimari/teknoloji kararları |
| [../../AGENTS.md](../../AGENTS.md), [../../CONTRIBUTING.md](../../CONTRIBUTING.md) | Mühendislik, sahiplik ve inceleme süreci |

Kaynak kod ve çalıştırılmış testler mevcut uygulamanın kanıtıdır. Tasarım metni
yeni işlevin hazır olduğu anlamına gelmez. Python/OCR/cihaz gereksinimleri alan
sahiplerine bağımlılık olarak aktarılır; frontend bu kuralları yeniden uygulamaz.

## Görsel kabul ve inceleme

Yetkilendirilmiş uygulama PR'ında 1440, 1024, 768 ve 390 CSS px genişliklerde
aynı sentetik veriyle ekran kanıtı hazırlanır; 320 px reflow ve %200 zoom da
kontrol edilir. Bunlar test hedefidir, referansın ölçüleri değildir.
Parkora kırpımıyla kompozisyon/hiyerarşi, bu şartnamelerle ürün davranışı karşılaştırılır.
Font veya piksel eşleşmesi iddia edilmez; varlık kopyalamadan yüksek görsel sadakat aranır.

İnceleme sırası: çevreleyen panel yokluğu → sidebar/header hizası → kart oranları
ve boşluk → tipografi/token kullanımı → veri etiketleri → durumlar → responsive
ve klavye erişimi. Yükleniyor, boş, filtre sonucu yok, hata, eski veri ve mutasyon
bekleme durumları gösterilir. Semantik renklerin gerçek zemindeki kontrastı ölçülür.
Frontend/API sözleşmesi ekibi görsel incelemeyi; API ihtiyacı varsa Python alan
sahibi sözleşme incelemesini yapar. Onaylı görsel yönden sapma gerekçesi ve karar
burada kayda alınmadan rastgele stil eklenmez; uygulama yetkisi ayrıca gerekir.
