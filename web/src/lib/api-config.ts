/**
 * Akıllı Plaka Bariyer Sistemi - API Entegrasyon Yapılandırması
 *
 * FastAPI backend bağlandığında sadece bu uç noktaların adresleri
 * ve yoklama (polling) ayarları güncellenecektir.
 */

export const API_CONFIG = {
  // FastAPI sunucu temel adresi
  BASE_URL: "http://127.0.0.1:8000",

  // 1. Sistem ve bariyer durum ucu (Son plaka, karar, bariyer pozisyonu ve telemetri)
  // GET http://127.0.0.1:8000/api/state
  STATE_ENDPOINT: "http://127.0.0.1:8000/api/state",

  // 2. ESP32 kamera gözlem ucu (Kare yakalama ve OCR kararı)
  // POST http://127.0.0.1:8000/api/device/v1/observations
  OBSERVATIONS_ENDPOINT: "http://127.0.0.1:8000/api/device/v1/observations",

  // 3. Bariyer telemetri ve hareket olayları ucu (barrier_opened, barrier_closed, access_denied)
  // POST http://127.0.0.1:8000/api/device/v1/events
  EVENTS_ENDPOINT: "http://127.0.0.1:8000/api/device/v1/events",

  // Otomatik durum yoklama (polling) sıklığı (milisaniye)
  POLL_INTERVAL_MS: 1500,

  // Cihaz ve dashboard yetkilendirme Bearer token'ı
  AUTH_TOKEN: "smart-barrier-device-key-2026",
};

export type BarrierPosition = "closed" | "opening" | "open" | "closing";
export type DecisionType = "allow" | "deny" | "unreadable" | "idle";

export interface BarrierLiveData {
  barrierState: BarrierPosition;
  decision: DecisionType;
  plateText: string | null;
  confidence: number | null;
  latencyMs?: number;
  lastEvent?: string;
  source: "api" | "simulation";
  apiConnected: boolean;
  lastUpdated?: string;
}
