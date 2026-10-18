# Codex çalışma kuralları

## Proje ve kapsam

- Resmî ve kalıcı kod kaynağı: https://github.com/0merUfuk/smart-plate-barrier.
- Başlamadan origin, dal, HEAD, çalışma ağacı ve geçerli AGENTS.md dosyalarını
  kontrol et. Kimlik yanlışsa dur. Yetkili mevcut çalışmaya devam edilebilir;
  beklenmeyen değişiklikleri ezme, etkilenen kapsamı netleştir.
- Yalnızca açıkça yetkilendirilmiş kapsamda çalış. Commit, push ve merge için
  açık yetki gerekir. Git/PR, inceleme ve ekip koordinasyonu süreçleri
  [CONTRIBUTING.md](CONTRIBUTING.md) içindedir.

## Mimari ve teknoloji

- backend/, web/, firmware/, hardware/, experiments/, tests/ ve docs/ korunur.
  Genel mimariyi değiştirme; yeni monorepo düzeni, mikroservis veya ek backend ekleme.
- Mevcut demo Python standart HTTP sunucusu, SQLite ve vanilla HTML/CSS/JavaScript
  kullanır. FastAPI planlanan Python API framework'üdür; henüz uygulanmamıştır.
- Onaylı frontend hedefi web/ içinde Next.js + React + TypeScript + Tailwind CSS'tir.
  Geçiş ilke olarak onaylı, henüz uygulanmamıştır. Açıkça yetkilendirilmiş geçiş
  veya özellik görevinde web/ değiştirilebilir ve onaylı frontend bağımlılıkları
  eklenebilir; yetki olmadan geçiş başlatma veya onaysız teknoloji ekleme.
- OCR hedefi OpenCV + EasyOCR; Rust öncelikli firmware adayı, donanım
  uygulanabilirliğine bağlı C++ alternatiftir. ESP32-CAM, sensör ve servo
  entegrasyonu planlıdır. Kararlar [docs/decisions.md](docs/decisions.md) içindedir.
- Next.js frontend katmanıdır: Route Handlers/API Routes ile iş API'si kopyalama;
  doğrudan veritabanına bağlanma, OCR, cihaz kontrolü veya bariyer yetkilendirmesi yapma.

## Sahiplik ve API

- Frontend ve API sözleşmesi ekibi frontend geliştirme ve sözleşme tasarımından
  sorumludur. Python/backend uygulama ekibi Python kaynakları/testleri, FastAPI,
  SQLite kalıcılığı ve iş mantığını; OCR ve görüntü işleme ekibi OCR'ı;
  firmware ve donanım alan sahipleri cihaz ve fiziksel entegrasyonu üstlenir.
  Başka alanın kaynaklarını açık kapsam onayı olmadan değiştirme.
- Frontend özelliği öncesi kanonik [docs/api.md](docs/api.md) sözleşmesini incele.
  Uygulanmış/planlı/eksik ayrımını kanıtla; yeni ihtiyacı CONTRIBUTING.md'deki
  öneri ve alan sahibi incelemesi sürecine taşı. Sözleşme tasarımı Python
  değişikliği yetkisi vermez; doğrulanmamış API'yi hazır sayma.
- Kalıcılık, request_id tekilleştirmesi ve bariyer güvenlik kuralları korunur:
  tekrar yeni kayıt/hareket üretmez, kapanma sonrası eski istek açmaz;
  aynı kimlikle farklı veri çakışmadır. Ret/hata yeni açma veya açık bariyerde
  kapanma üretmez; kapanma alan boşluğu doğrulaması gerektirir. UI bu kuralları atlayamaz.

## Frontend kalitesi

- TypeScript strict tip denetimi kullan; `any` için belgelenmiş gerekçe gerekir.
  API sınırında veriyi doğrula; ortak tipleri gerektiğinde tanımla.
- Özellik sahipliğini açık tut; UI, API istemcisi ve yeniden kullanılabilir mantığı
  ayır. Odaklı küçük bileşenler, açıklayıcı adlar ve basit durum yönetimi kullan.
  Gerçek tekrar varsa ortaklaştır; erken soyutlama ve gereksiz bağımlılık ekleme.
- Next.js/React kurallarını, Tailwind tasarım tokenlarını ve tutarlı stilleri izle.
  Yükleniyor, hata, boş ve başarı durumlarını işle; erişilebilirlik, klavye
  kullanımı ve duyarlı yerleşimi kabul ölçütü say.

## Güvenlik, belge ve doğrulama

- Demo yalnızca loopback içindir; üretim kimlik doğrulaması yoktur. İnternete açma
  veya fiziksel bariyere bağlama. Manuel boşluk düğmesi sensör doğrulaması,
  erişim kararı gerçekleşmiş geçiş, sentetik test gerçek OCR/donanım kanıtı değildir.
- Özel veri ve sırları repository'ye ekleme; CONTRIBUTING.md'deki veri/bağımlılık
  kurallarına uy. Kanonik belge haritası ve doğrulama adımları da oradadır.
- İlgili kaynak, test ve belgeleri incele; hedef ile uygulamayı ayır. Çelişkileri
  bildir, ekip kararlarını veya eski kanıtları sessizce ezme. Türkçe belge dilini koru.
- Değişikliğe uygun kontrolleri çalıştır; staged, unstaged ve izlenmeyen dosyaları
  ayrı incele. Çalıştırmadığın testi geçmiş gösterme; engeli etkisiyle raporla.

## Teslim raporu

Türkçe ve kısa raporla: tamamlanan kapsam, değişen dosyalar, yapılan doğrulama ve
sonuçları, açık sorun/bağımlılıklar ve önerilen sonraki adım. Görev talebi farklı
bir rapor yapısı belirtiyorsa onu izle.
