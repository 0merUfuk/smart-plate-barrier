# Gömülü yazılım

Rust öncelikli adaydır. `rust/` bağımlılıksız, `no_std` bir durum geçiş çekirdeğidir.
ESP32 firmware değildir, karta flashlanamaz. Kamera, Wi-Fi, HTTP, GPIO ve servo
sürücüleri henüz bağlanmamıştır. Bu çalışma ortamında Rust araç zinciri yoktur;
derleme ve üç Rust testi burada çalıştırılmamıştır. CI iş akışı bu testleri çalıştırır.

Yerel Rust kuruluysa: `cargo test --manifest-path firmware/rust/Cargo.toml`.

Donanım doğrulandıktan sonra en fazla bir iş günlük Rust + ESP-IDF denemesi:
JPEG çek, PC'ye gönder, sensör oku, servo PWM üret, aynı anda bellek ve beslemeyi izle.
Engel kalırsa aynı API ve durum modeliyle C++ + ESP-IDF/Arduino'ya geç.
Kameranın C sürücüsünü Rust'tan sarmalamak ek entegrasyon gerektirebilir.

Fiziksel kapanma, alan boşluğunu doğrulayan sensör ve gömülü zamanlama tasarımıyla
kontrol edilmelidir. Sunucunun allow yanıtı süresiz açma komutu değildir.
Tekrar veya geç yanıtı reddetmek için cihaz tarafında request_id, süre sınırı ve
işlem tekilleştirme tasarlanmalıdır. Bu mekanizmalar henüz firmware'e uygulanmadı.
