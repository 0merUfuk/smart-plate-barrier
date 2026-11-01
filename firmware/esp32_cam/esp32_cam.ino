/*
 * Akıllı Plaka Bariyer Sistemi - ESP32-CAM Tam Entegre Firmware
 *
 * Hedef Kart: AI-Thinker ESP32-CAM (OV2640 Kamera Modülü)
 * Fonksiyonlar:
 * 1. OV2640 kamerasından JPEG yakalama.
 * 2. Yerel Wi-Fi üzerinden PC'deki FastAPI sunucusuna kimlik doğrulamalı istek:
 *    POST /api/device/v1/observations (image/jpeg)
 * 3. HC-SR04 Ultrasonik Sensör ile araç yaklaşma (< 20 cm) ve geçiş tamamlama tespiti.
 * 4. SG90 Servo motor ile bariyer kolu kontrolü (0° Kapalı, 90° Açık).
 * 5. Durum LED'leri (Yeşil: İzin verildi, Kırmızı: Ret/Hata).
 * 6. Bariyer hareket telemetrisi: POST /api/device/v1/events
 */

#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ==================== KULLANICI / AĞ AYARLARI ====================
const char* WIFI_SSID     = "WIFI_ADINIZ";
const char* WIFI_PASSWORD = "WIFI_PAROLANIZ";

// PC'nin yerel ağ IP adresi (örn. 192.168.1.50)
const char* SERVER_HOST   = "http://192.168.1.50:8000";
const char* AUTH_TOKEN    = "smart-barrier-device-key-2026";
const char* DEVICE_ID     = "esp32-barrier-01";

// ==================== AI-THINKER KAMERA PİNLERİ ====================
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

// ==================== HARİCİ BİLEŞEN PİNLERİ ====================
#define PIN_SERVO         14 // SG90 Servo PWM sinyal pini
#define PIN_TRIG          15 // HC-SR04 Ultrasonik Tetikleme (Trig)
#define PIN_ECHO          13 // HC-SR04 Ultrasonik Yankı (Echo - 1k/2k direnç bölücü ile!)
#define PIN_LED_GREEN     12 // Yeşil Durum LED'i (Anot - 220Ω ile)
#define PIN_LED_RED        2 // Kırmızı Durum LED'i (Anot - 220Ω ile)
#define PIN_INTERNAL_LED  33 // Dahili küçük kırmızı LED (Ters mantık: LOW = Açık)

// ==================== OTURUM VE İSTEK DURUMU ====================
String session_id = "";
uint32_t request_seq = 0;
bool is_barrier_open = false;

// ==================== YARDIMCI FONKSİYONLAR ====================

// Kütüphanesiz, kararlı yazılımsal PWM ile servo açısı ayarla (0° - 90°)
void setServoAngle(int angle) {
  int pulse_us = map(angle, 0, 90, 550, 2400);
  for (int i = 0; i < 25; i++) {
    digitalWrite(PIN_SERVO, HIGH);
    delayMicroseconds(pulse_us);
    digitalWrite(PIN_SERVO, LOW);
    delayMicroseconds(20000 - pulse_us);
  }
}

// HC-SR04 ultrasonik mesafe okuma (cm cinsinden)
float readDistanceCM() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duration = pulseIn(PIN_ECHO, HIGH, 30000); // 30ms zaman aşımı (~500 cm)
  if (duration == 0) return 999.0; // Engel yok veya zaman aşımı
  return (duration * 0.0343) / 2.0;
}

// Sunucuya telemetri olayı bildirme (POST /api/device/v1/events)
void sendDeviceEvent(const String& event_type, const String& barrier_state) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  String url = String(SERVER_HOST) + "/api/device/v1/events";
  http.begin(url);
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", String("Bearer ") + AUTH_TOKEN);

  String payload = "{\"device_id\":\"" + String(DEVICE_ID) +
                   "\",\"session_id\":\"" + session_id +
                   "\",\"event_id\":\"evt-" + String(micros(), HEX) +
                   "\",\"event_type\":\"" + event_type +
                   "\",\"barrier_state\":\"" + barrier_state + "\"}";

  int code = http.POST(payload);
  Serial.printf("[TELEMETRI] Olay: %s, Durum: %s, HTTP Kodu: %d\n", event_type.c_str(), barrier_state.c_str(), code);
  http.end();
}

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

  if (psramFound()) {
    config.frame_size   = FRAMESIZE_VGA; // 640x480
    config.jpeg_quality = 12; // 0-63
    config.fb_count     = 2;
  } else {
    config.frame_size   = FRAMESIZE_CIF; // 400x296 (PSRAM yokken güvenli)
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

  // Pin modları
  pinMode(PIN_SERVO, OUTPUT);
  digitalWrite(PIN_SERVO, LOW);

  pinMode(PIN_TRIG, OUTPUT);
  digitalWrite(PIN_TRIG, LOW);
  pinMode(PIN_ECHO, INPUT);

  pinMode(PIN_LED_GREEN, OUTPUT);
  digitalWrite(PIN_LED_GREEN, LOW);
  pinMode(PIN_LED_RED, OUTPUT);
  digitalWrite(PIN_LED_RED, LOW);

  pinMode(PIN_INTERNAL_LED, OUTPUT);
  digitalWrite(PIN_INTERNAL_LED, HIGH); // Dahili LED söndür

  // Bariyer kolunu başlangıçta güvenli kapalı (0°) pozisyona al
  setServoAngle(0);
  is_barrier_open = false;

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

  Serial.printf("\n--- Gozlem Baslatiliyor: %s ---\n", request_id.c_str());
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[HATA] Kare yakalanamadi (framebuffer bos)!");
    return;
  }

  Serial.printf("[KAMERA] Kare alindi: %u bayt, cozunurluk: %ux%u\n", fb->len, fb->width, fb->height);

  HTTPClient http;
  String url = String(SERVER_HOST) + "/api/device/v1/observations";
  http.begin(url);
  http.setTimeout(10000);

  http.addHeader("Content-Type", "image/jpeg");
  http.addHeader("Authorization", String("Bearer ") + AUTH_TOKEN);
  http.addHeader("X-Device-Id", DEVICE_ID);
  http.addHeader("X-Session-Id", session_id);
  http.addHeader("X-Request-Id", request_id);

  int httpCode = http.POST(fb->buf, fb->len);
  esp_camera_fb_return(fb); // Kare belleğini hemen serbest bırak

  if (httpCode > 0) {
    String response = http.getString();
    Serial.printf("[SUNUCU] HTTP Kodu: %d\n", httpCode);
    Serial.printf("[SUNUCU] Yanit: %s\n", response.c_str());

    if (httpCode == 200) {
      if (response.indexOf("\"decision\":\"allow\"") > 0) {
        Serial.println(">>> [KARAR] IZIN VERILDI (ALLOW)! Bariyer aciliyor...");

        // Yeşil LED aç, Kırmızı LED kapa
        digitalWrite(PIN_LED_GREEN, HIGH);
        digitalWrite(PIN_LED_RED, LOW);
        digitalWrite(PIN_INTERNAL_LED, LOW); // Dahili LED yak

        // Servoyu 90 dereceye kaldır (Bariyeri Aç)
        setServoAngle(90);
        is_barrier_open = true;
        sendDeviceEvent("barrier_opened", "open_waiting_clear");

        // Aracın geçişini bekle (Sensörün önü boşalana kadar bekle)
        Serial.println("[BEKLEME] Aracin gecisi bekleniyor (alan bosalmasi)...");
        unsigned long clear_start = 0;
        while (true) {
          float dist = readDistanceCM();
          if (dist > 25.0) { // Araç uzaklaştı (> 25 cm)
            if (clear_start == 0) clear_start = millis();
            if (millis() - clear_start > 2000) { // 2 saniye boyunca alan boşsa
              Serial.println("[GECIS] Alan bosaldi. Bariyer kapatiliyor...");
              break;
            }
          } else {
            clear_start = 0; // Araç hala bariyere yakın
          }
          delay(200);
        }

        // Bariyeri kapat (0 dereceye indir)
        setServoAngle(0);
        is_barrier_open = false;
        digitalWrite(PIN_LED_GREEN, LOW);
        digitalWrite(PIN_INTERNAL_LED, HIGH);
        sendDeviceEvent("barrier_closed", "closed");
        Serial.println("[KAPANDI] Bariyer kapandi. Sistem hazir.");

      } else if (response.indexOf("\"decision\":\"deny\"") > 0) {
        Serial.println(">>> [KARAR] RET (DENY)! Plaka listede yok. Bariyer kapali kalir.");
        digitalWrite(PIN_LED_RED, HIGH);
        digitalWrite(PIN_LED_GREEN, LOW);
        sendDeviceEvent("access_denied", "closed");
        delay(3000);
        digitalWrite(PIN_LED_RED, LOW);
      } else {
        Serial.println(">>> [KARAR] OKUNAMADI / HATA! Bariyer kapali kalir.");
        digitalWrite(PIN_LED_RED, HIGH);
        digitalWrite(PIN_LED_GREEN, LOW);
        sendDeviceEvent("unreadable_observation", "closed");
        delay(3000);
        digitalWrite(PIN_LED_RED, LOW);
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
  // 1. Manuel seri port tetikleme kontrolü (Test kolaylığı için 'c' veya 'C')
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'c' || c == 'C') {
      captureAndEvaluate();
      return;
    }
  }

  // 2. Ultrasonik sensör ile otomatik araç algılama
  if (!is_barrier_open) {
    float dist = readDistanceCM();
    if (dist > 1.0 && dist < 20.0) { // Araç 20 cm'den yakına geldiğinde
      Serial.printf("\n[SENSOR] Arac algilandi! Mesafe: %.1f cm. Plaka okuma tetikleniyor...\n", dist);
      captureAndEvaluate();
      delay(3000); // Mükerrer peş peşe tetiklemeyi önlemek için kısa bekleme
    }
  }

  delay(200);
}
