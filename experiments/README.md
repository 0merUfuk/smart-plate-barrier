# Deneyler

`python -m experiments.evaluate_decisions` sekiz sentetik karar senaryosunu çalıştırır.
Sonuçlar OCR doğruluğu, saha güvenilirliği veya gerçek ağ zaman aşımı ölçümü değildir.
`network_timeout` yalnızca bir hata girdisidir; ağdaki paketi geciktirmez.

## Gerçek görüntü deney planı

- İzinli veya sentetik plaka görüntülerini topla. Kaynak, izin ve lisansını kaydet.
- `sample_id,plate_text,session_id,lighting,angle,distance,split` alanlarını etiketle.
- Aynı çekim oturumu ve aynı fiziksel plakayı ayar ve test kümelerine dağıtma.
- Ham görüntü ve OpenCV ön işlemeyi aynı sabit test kümesinde karşılaştır.
- Tam plaka eşleşmesi, karakter hata oranı, yanlış kabul, yanlış ret ve p50/p95 gecikme ölç.
- Güven eşiğini ayar kümesinde seç. Test kümesine göre tekrar ayarlama yapma.
- Eşik 0.85 bu sürümde öneridir. OCR güven skoru olasılık garantisi değildir.

Gerçek veri, OCR modeli, model ağırlıkları ve sonuçlar henüz bulunmuyor.
Özel görüntüleri `data/private/` altında tut; public repository'ye ekleme.
