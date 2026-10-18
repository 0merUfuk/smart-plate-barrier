# Tuval ve yerleşim sözleşmesi

Renk/boyut tokenları [design-system.md](design-system.md), içerik sırası
[pages/overview.md](pages/overview.md) içindedir. Bu dosyanın ölçüleri proje
önerisidir; Parkora'nın ölçülmüş geometrisi değildir.

## Zorunlu kompozisyon

Sayfanın tamamı tek, kesintisiz full-bleed tuvaldir. Sidebar ve main bu zeminde
yan yana durur. Kartlar bağımsız floating-island yüzeylerdir; kartların arasında
tuval görünür. Header yüzeysizdir; yalnızca arama gibi kontroller kendi yüzeyini taşır.

Tüm dashboard'u, navigasyonu ve header'ı saran beyaz kart, ekran boyu yuvarlatılmış
uygulama çerçevesi, ikinci arka plan paneli veya tüm kartların arkasına konan
büyük yüzey **yasaktır**. Referansın sunum kırpımındaki dış köşe/masaüstü pencere
işaretleri uygulama kabuğu olarak yorumlanmaz. Main bir grid yerleşim öğesidir,
ayrı dolgusu/gölgesi/kenarı olan panel değildir.

## Masaüstü önerisi: 1200 CSS px ve üzeri

- Sidebar solda 80px genişlikte, border/background kartı olmadan; üstte ürün
  ana sayfası bağlantısı, altında 48px hedeflere sahip ikon navigasyonu. Tam
  proje adı header'da küçük metin olarak yer alır, dar raya sıkıştırılmaz. Parkora'daki alt
  seviyede gruplanmış navigasyon hissi korunur; dikey konum için sabit piksel
  boşluk yığını yerine esnek boşluk kullanılır. Kısa ekranda bütün linkler erişilebilir kalır.
- İçerik solda sidebar sonrası 24px, sağda 32px boşlukla uzanır. Büyük monitörde
  en çok 1600px okunabilir içerik genişliği önerilir; fazla alan aynı tuvaldir,
  beyaz bir kutuya dönüşmez. Sidebar büyüyerek içerik oranını bozmaz.
- Header yaklaşık 72px içerik yüksekliğiyle içerik üst kenarındadır. Başlık,
  “Simülasyon” işareti, yerel kayıt araması ve yenileme kontrolü aynı hizalama
  sistemini kullanır. Arama en çok 560px; aksiyonlar taşarsa bir alt satıra geçer.
- Ana grid 12 eşit sütun, 16px aralık; bütün kartlarda `min-width: 0` davranışı
  gözetilir. Ana bölüm solda 8, yardımcı bölüm sağda 4 sütundur.
- Üst durum alanı 8 + 4, metrikler 4 + 4 + 4, alt analiz 8 + 4; kayıt tablosu
  tam 12 sütun. Satırlar arasında 24px vardır. Üstteki bilgi yoğunluğu küçük
  etiket/değer hücreleriyle sağlanır, gereksiz kahraman görseliyle değil.
- Metrik kart yüksekliği en az 144px önerilir; içerikle büyür. Analiz kartları
  yaklaşık 300px başlangıç yüksekliğini paylaşır. Sabit yükseklik metin/zoom'u kesemez.
- Başlıklar ve sayılar kart iç boşluğuna hizalanır; rastgele kart offset'leri,
  negatif margin ile yüzey bindirme veya kartları birbirine yapıştırma yapılmaz.

Sidebar sayfa kaydırmasına eşlik eden sticky bir navigasyon olabilir; viewport'a
sığmadığında kendi içinde kaydırılır. Header varsayılan akıştadır; içerik üstünü
kapatan sabit üst bar eklenmez. Z-index yalnızca açılır menü/dialog gibi gerçek
katmanlarda kullanılır; tooltip ve odak halkası kırpılmaz.

## Responsive geçişler

| Aralık | Navigasyon/header | İçerik |
|---|---|---|
| Desktop ≥1200px | Dar çerçevesiz ikon rayı; header yatay | 12 sütun ve 8:4 ilişki |
| Tablet 768–1199px | 64px ray; header iki satıra açılabilir, arama alt satırda | 8 sütun; durum/aksiyon 5:3, metrikler 4+4 ve üçüncü kart 8; analiz ve son karar ayrı tam satırlar |
| Mobile <768px | Ray kaldırılır; header'da menü düğmesi, erişilebilir açılır navigasyon | Tek sütun, kenarlar 16px; durum → aksiyon → metrikler → dağılım → son karar → kayıtlar |

Mobil menü gerçek bir açılır katmandır; kalıcı uygulama çerçevesi değildir.
Link metinleri görünür, kapatma düğmesi/ESC ve açan kontrole odak dönüşü vardır.
320px genişlikte de içerik sayfa yatay taşması üretmez. Mobilde metrikler
küçülüp üçe sıkıştırılmaz; tek sütunda daha kısa içerikle sunulur.

Breakpoints ekranın fiziksel cihaz sınıfını değil kullanılabilir CSS genişliğini
anlatır. %200 zoom aynı responsive kurallarla çalışır. İçeriğin kesildiği ara
genişlikler ayrıca denenir; yalnızca dört ekran görüntüsüyle kabul verilmez.

## Taşma ve okuma sırası

Görsel ve DOM okuma sırası aynıdır; CSS order ile klavye sırası ters çevrilmez.
Uzun reason/request_id metinleri kart içinde kırılır; tam değer ayrıntıda erişilir.
Tablo kendi etiketli yatay kaydırma bölgesine sahip olabilir; sayfanın tamamını
kaydırmaz. Diğer kartlar bu istisnayı kullanamaz. Mobilde tablo yerine aynı
verilerin başlıklı satır kartları önerilir; iki temsil aynı anda erişilebilirlik
ağacında yer almaz. Grafik açıklaması ve lejantı dikey akar, kırpılmaz.

Sidebar'da yalnızca gerçek hedefler görünür: Genel Bakış, Erişim Denemeleri,
İzinli Plakalar, Simülasyon. Ayrı sayfalar henüz olmadığı için ilk uygulama
tasarımında bunlar sayfa içi bölüm hedefleri olabilir; ölü link ve sahte kullanıcı/
ayar/ödeme alanları oluşturulmaz. Hedeflerin route kararı sonraki frontend planının işidir.
