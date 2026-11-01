/*
 * Akıllı Plaka Bariyer Sistemi - ESP32-CAM Firmware
 *
 * Hedef Kart: AI-Thinker ESP32-CAM (OV2640 Kamera Modülü)
 * Görev:
 * 1. OV2640 kamerasından JPEG yakalama.
 * 2. Yerel Wi-Fi üzerinden PC'deki FastAPI sunucusuna kimlik doğrulamalı istek gönderme:
 *    POST /api/device/v1/observations (image/jpeg)
 * 3. Sunucu kararını (allow, deny, unreadable, error) işleme.
 * 4. LED göstergeleri ve durum yönetimi:
 *    - Yeşil LED: İzin verildi (allow)
 *    - Kırmızı LED: Ret / Okunamadı / Hata
 * 5. Servo bariyer kontrolü (güvenlik doğrulamasından sonra).
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ==================== KULLANICI AYARLARI ====================
const char* WIFI_SSID     = "WIFI_ADINIZ";
const char* WIFI_PASSWORD = "WIFI_PAROLANIZ";

// PC'nin yerel ağ IP adresi (örn. 192.168.1.50)
const char* SERVER_HOST   = "http://192.168.1.50:8000";
const char* AUTH_TOKEN    = "smart-barrier-device-key-2026";
const char* DEVICE_ID     = "esp32-barrier-01";

// ==================== AI-THINKER PIN TANIMLARI ====================
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// Durum LED Pinleri (Örnek boş pinler: GPIO 12 ve GPIO 13)
// Not: Dahili flaş LED GPIO 4'tedir; test için kullanılabilir.
#define PIN_LED_GREEN     12
#define PIN_LED_RED       13
#define PIN_INTERNAL_LED  33 // ESP32-CAM dahili küçük kırmızı LED (ters mantık: LOW = Açık)

// ==================== OTURUM VE İSTEK DURUMU ====================
String session_id = "";
uint32_t request_seq = 0;

void setupCamera() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // PSRAM kontrolü ve çözünürlük seçimi
  if (psramFound()) {
    config.frame_size   = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 12; // 0-63 (düşük sayı = yüksek kalite)
    config.fb_count     = 2;
  } else {
    config.frame_size   = FRAMESIZE_SVGA; // 800x600 veya CIF
    config.jpeg_quality = 15;
    config.fb_count     = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[HATA] Kamera baslatilamadi! Kod: 0x%x\n", err);
    while (true) {
      digitalWrite(PIN_INTERNAL_LED, LOW);
      delay(100);
      digitalWrite(PIN_INTERNAL_LED, HIGH);
      delay(100);
    }
  }
  Serial.println("[OK] Kamera basariyla baslatildi.");
}

void setupWiFi() {
  Serial.printf("[WIFI] Baglaniyor: %s\n", WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WIFI] Baglandi! IP Adresi: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[UYARI] Wi-Fi baglantisi kurulamadi. Dongude tekrar denenecek.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n==========================================");
  Serial.println("  Akilli Plaka Bariyer - ESP32-CAM Basliyor ");
  Serial.println("==========================================");

  pinMode(PIN_INTERNAL_LED, OUTPUT);
  digitalWrite(PIN_INTERNAL_LED, HIGH); // Söndür

  // Rastgele oturum kimliği üret (açılış bazlı)
  randomSeed(micros());
  session_id = "sess-" + String(micros(), HEX) + "-" + String(random(1000, 9999));
  Serial.printf("[SISTEM] Acilis Oturum Kimligi: %s\n", session_id.c_str());

  setupCamera();
  setupWiFi();
}

void captureAndEvaluate() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HATA] Wi-Fi bagli degil, istek gonderilemez.");
    setupWiFi();
    return;
  }

  request_seq++;
  String request_id = "req-" + String(request_seq);

  Serial.printf("\n--- Gözlem Baslatiliyor: %s ---\n", request_id.c_str());
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[HATA] Kare yakalanamadi (framebuffer bos)!");
    return;
  }

  Serial.printf("[KAMERA] Kare alindi: %u bayt, cozunurluk: %ux%u\n", fb->len, fb->width, fb->height);

  HTTPClient http;
  String url = String(SERVER_HOST) + "/api/device/v1/observations";
  http.begin(url);
  http.setTimeout(10000); // 10 saniye zaman aşımı

  // Kimlik ve üstveri başlıkları
  http.addHeader("Content-Type", "image/jpeg");
  http.addHeader("Authorization", String("Bearer ") + AUTH_TOKEN);
  http.addHeader("X-Device-Id", DEVICE_ID);
  http.addHeader("X-Session-Id", session_id);
  http.addHeader("X-Request-Id", request_id);

  int httpCode = http.POST(fb->buf, fb->len);
  esp_camera_fb_return(fb); // Kare belleğini hemen serbest bırak

  if (httpCode > 0) {
    String response = http.getString();
    Serial.printf("[SUNUCU] Yanit Kodu: %d\n", httpCode);
    Serial.printf("[SUNUCU] Govde: %s\n", response.c_str());

    if (httpCode == 200) {
      if (response.indexOf("\"decision\":\"allow\"") > 0) {
        Serial.println(">>> [KARAR] IZIN VERILDI (ALLOW)! Bariyer acilabilir.");
        // Dahili LED ile görsel bildirim (kısa yakma)
        digitalWrite(PIN_INTERNAL_LED, LOW);
        delay(1500);
        digitalWrite(PIN_INTERNAL_LED, HIGH);
      } else if (response.indexOf("\"decision\":\"deny\"") > 0) {
        Serial.println(">>> [KARAR] RET (DENY)! Plaka listede yok. Bariyer kapali kalir.");
      } else {
        Serial.println(">>> [KARAR] OKUNAMADI / HATA! Bariyer kapali kalir.");
      }
    } else {
      Serial.printf("[UYARI] Beklenmeyen HTTP kodu: %d\n", httpCode);
    }
  } else {
    Serial.printf("[HATA] HTTP baglanti hatasi: %s\n", http.errorToString(httpCode).c_str());
  }
  http.end();
}

void loop() {
  // Test dongusu: Her 15 saniyede bir ornek yakalama gerceklestirir.
  // Gercek montajda yaklasma sensoru tetikleyecektir.
  Serial.println("\nYeni gozlem icin 15 saniye bekleniyor (veya Serial'dan 'c' gonderin)...");
  for (int i = 0; i < 15; i++) {
    if (Serial.available()) {
      char c = Serial.read();
      if (c == 'c' || c == 'C') {
        captureAndEvaluate();
        return;
      }
    }
    delay(1000);
  }
  captureAndEvaluate();
}
