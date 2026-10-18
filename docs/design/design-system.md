# Görsel sistem ve tokenlar

Kapsam ve kaynak kanıtı: [README.md](README.md). Aşağıdaki sayısal eşlemeler
**önerilen proje değerleridir**; Parkora'dan ölçülmüş font, boyut veya efekt değildir.
Gelecekte Tailwind teması semantik CSS tokenlarına bağlanır; rastgele sayfa renkleri eklenmez.

## Doğrulanmış referans paleti

[Parkora Dribbble sayfasında](https://dribbble.com/shots/26532568-Parkora-Dashboard-Parking-Management-System)
yayımlanan renkler aynen: `#B7B1B4`, `#EFEFF1`, `#060606`, `#61625F`, `#AFC9EB`, `#2F49A3`.
Bunlar kaynak renkleridir; tümü metin, kontrol sınırı veya semantik durum rengi olmaya uygun varsayılmaz.

## Önerilen semantik renkler

| CSS token | Değer | Kullanım |
|---|---|---|
| --canvas | #EFEFF1 | Tüm sayfanın tek arka planı |
| --canvas-tint | #ECE8F3 | Üst/sağ tuvalde isteğe bağlı çok hafif lavanta tonu; panel değil |
| --surface | #FFFFFF | Bağımsız kartlar ve dialog |
| --surface-muted | #F7F7F8 | Küçük bilgi hücreleri, arama ve ikincil zemin |
| --text-primary | #060606 | Başlık, değer ve gövde |
| --text-secondary | #61625F | Etiket, yardımcı metin |
| --text-disabled | #B7B1B4 | Yalnızca devre dışı içerik; normal açıklama değil |
| --accent | #2F49A3 | Aktif navigasyon, veri vurgusu ve odak |
| --accent-soft | #AFC9EB | Grafik dolgu; küçük metin veya tek başına sınır değil |
| --border-subtle | #E3E3E7 | Dekoratif ayırıcı; kontrol sınırı yerine geçmez |
| --border-control | #767672 | Girdi/ikincil kontrol sınırı |
| --action-primary / --on-primary | #060606 / #FFFFFF | Siyah ana aksiyon ve yazısı |
| --status-allow / --status-allow-bg | #166534 / #F0FDF4 | İzin kararı; fiziksel geçiş değil |
| --status-deny / --status-deny-bg | #991B1B / #FEF2F2 | Ret veya yıkıcı aksiyon |
| --status-unreadable / --status-unreadable-bg | #854D0E / #FEFCE8 | Okunamadı |
| --status-error / --status-error-bg | #6B21A8 / #FAF5FF | Gözlem işleme hatası |
| --status-neutral / --status-neutral-bg | #61625F / #F7F7F8 | Kapalı, bilgi yok veya bilinmiyor; ayrı metinlerle |

Durum renkleri kaynak paletten alınmış iddiası taşımaz; maviyle yarışan dekoratif
aksanlar olarak kullanılmaz. Sanal açık bariyer “güvenli geçiş” yeşiliyle sunulmaz:
mavi vurgu ve “Açık — alan boşluğu bekleniyor” metni kullanılır.
Kırmızı ret, mor hata ve sarı okunamadı yalnızca ilgili veri işaretlerinde görünür.

Normal metin en az 4.5:1, büyük metin ve anlamlı grafik/kontrol sınırları en az
3:1 kontrast hedefler. Uygulamada gerçek bileşim ölçülmeden erişilebilirlik geçti
denmez. Açık mavi dolguya koyu mavi işaret/etiket eşlik eder; dekoratif düşük
kontrastlı çizgiler bilgi taşımaz. Renk her durumda metin ve gerektiğinde ikonla desteklenir.

## Tipografi

Font önerisi `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`;
özgün Parkora fontu doğrulanmadı. Harici font indirme zorunluluğu yoktur.

| Rol / token | Boyut / satır yüksekliği / ağırlık |
|---|---|
| --type-page-title | 28px / 36px / 600; mobil 24px / 32px |
| --type-section-title | 20px / 28px / 600 |
| --type-metric | 36px / 44px / 600; mobil 30px / 38px |
| --type-body | 16px / 24px / 400 |
| --type-label | 14px / 20px / 400; kontrol etiketinde 500 |
| --type-caption | 12px / 18px / 400; kritik güvenlik açıklaması body/label kullanır |

Bir sayfada tek h1; kart başlıkları mantıklı h2/h3 sırasındadır. Metriklerde
tabular rakamlar, Türkçe gösterimde `tr-TR` biçimi kullanılır. Plaka ve kimlik
okunabilirliği korunur; satır kesme metnin tam haline erişimi engellemez.

## Boşluk, köşe ve efektler

| Grup | Öneri ve kural |
|---|---|
| Boşluk | --space-1…8: 4, 8, 12, 16, 24, 32, 48, 64px; ara değer gerekçelendirilir |
| Kart içi / grid arası | Masaüstü 24 / 16px; tablet 20 / 16px; mobil 16 / 12px |
| Köşe | --radius-control: 12px; --radius-card: 24px; --radius-pill: 999px |
| Büyük kapsayıcı | Tuvale veya tüm uygulama çevresine radius/gölge verilmez |
| Kart gölgesi | --shadow-card: 0 2px 12px rgb(6 6 6 / 0.03); zorunlu değil |
| Kart kenarı | Varsayılan yok; komşu yüzey ayrımı gerekiyorsa 1px border-subtle |
| Dialog gölgesi | --shadow-overlay: 0 12px 40px rgb(6 6 6 / 0.12); yalnızca katmanlı yüzey |
| Odak | 2px accent çizgi, 2px dış boşluk; kırpılmaz, hover'a bağımlı değil |

Kartlar büyük gölge ve kalın çizgilerle çerçevelenmez. Tuval tercihen düz renktir;
lavanta kullanılırsa düşük etkili lokal ton olarak kalır, ağır gradient yapılmaz.

## Buton, ikon ve hareket

| Varyant | Görünüm ve durum |
|---|---|
| Primary | Siyah hap, beyaz yazı; bir bölümde tek baskın aksiyon; hover #242424 |
| Secondary | Beyaz/muted yüzey, koyu metin ve control sınırı; hover muted |
| Tertiary | Yüzeysiz metin/ikon; hover muted, odak halkası korunur |
| Destructive | Açık ret zemini, koyu ret metni, açık “Sil” etiketi; genel ana aksiyon değil |
| Pending/disabled | Pending'de yazı sabit + durum metni, yeniden gönderim engelli; disabled gerekçesi görünür |

Kontrol yüksekliği önerisi 44px; ikon 20px, kompakt navigasyon ikonu 22px,
navigasyon hedefi 48px. Daire ikon butonları ve hap metin butonları bilinçli
varyantlardır. Tıklama alanı en az 44×44 CSS px; ikon-only kontrolün erişilebilir adı gerekir.
Tek tutarlı çizgisel ikon ailesi kullanılır; paket seçimi henüz yapılmadı.
Unicode/emoji karışımı, marka logosu kopyalama ve dekoratif otomobil kullanılmaz.

Hareket önerisi: renk/opacity geçişleri 120–160ms ease-out. Sayfa açılışında
kart uçuşu, sürekli nabız veya sahte canlı grafik yoktur. Reduced-motion
tercihinde gereksiz geçiş ve skeleton hareketi kaldırılır. Bariyer durumu ikon
ve metinle anlatılır; animasyon fiziksel hareket kanıtı değildir.
