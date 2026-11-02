"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/controls/OrbitControls.js";
import { API_CONFIG, type BarrierPosition, type DecisionType } from "../lib/api-config";
import { Icon } from "./icon";

function isJSDOM(): boolean {
  return typeof navigator !== "undefined" && navigator.userAgent.includes("jsdom");
}

function createTextTexture(text: string, bgColor: string, textColor: string) {
  if (typeof document === "undefined" || isJSDOM()) return null;
  try {
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext("2d");
    if (!ctx) return null;
    ctx.fillStyle = bgColor;
    ctx.fillRect(0, 0, 512, 128);
    ctx.fillStyle = textColor;
    ctx.font = "bold 60px system-ui, -apple-system, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(text, 256, 64);
    const texture = new THREE.CanvasTexture(canvas);
    texture.needsUpdate = true;
    return texture;
  } catch {
    return null;
  }
}

export function Barrier3DModel() {
  const containerRef = useRef<HTMLDivElement>(null);
  const controlsRef = useRef<OrbitControls | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);

  // Bariyer ve sistem durumları
  const [barrierState, setBarrierState] = useState<BarrierPosition>("closed");
  const [decision, setDecision] = useState<DecisionType>("idle");
  const [plateText, setPlateText] = useState<string | null>("34 DMO 01");
  const [confidence, setConfidence] = useState<number | null>(0.98);
  const [apiConnected, setApiConnected] = useState<boolean>(false);
  const [isManualOverride, setIsManualOverride] = useState<boolean>(false);
  const [lastEventTime, setLastEventTime] = useState<string>("Henüz hareket yok");

  // Three.js dinamik referansları
  const armPivotRef = useRef<THREE.Group | null>(null);
  const redLightRef = useRef<THREE.Mesh | null>(null);
  const greenLightRef = useRef<THREE.Mesh | null>(null);
  const redPointLightRef = useRef<THREE.PointLight | null>(null);
  const greenPointLightRef = useRef<THREE.PointLight | null>(null);
  const isDenyShakingRef = useRef<boolean>(false);

  // Hedef açı (0 = kapalı, 90 derece = açık)
  const targetAngleRef = useRef<number>(0);

  // Açı güncellemesi (Z ekseni etrafında 0° yatay kapalı, -90° yukarı açık)
  useEffect(() => {
    if (barrierState === "open" || barrierState === "opening") {
      targetAngleRef.current = -Math.PI / 2; // -90° (Dikey Yukarı Açık)
    } else {
      targetAngleRef.current = 0; // 0° (Yatay Kapalı)
    }
    isDenyShakingRef.current = decision === "deny";
  }, [barrierState, decision]);

  // Işık güncellemesi
  useEffect(() => {
    const isGreen = barrierState === "open" || barrierState === "opening" || decision === "allow";
    const isRed = !isGreen || decision === "deny";

    if (redLightRef.current && redLightRef.current.material instanceof THREE.MeshStandardMaterial) {
      redLightRef.current.material.emissive.setHex(isRed ? 0xff2222 : 0x220000);
      redLightRef.current.material.emissiveIntensity = isRed ? 2.5 : 0.1;
    }
    if (redPointLightRef.current) {
      redPointLightRef.current.intensity = isRed ? 2.0 : 0.0;
    }

    if (greenLightRef.current && greenLightRef.current.material instanceof THREE.MeshStandardMaterial) {
      greenLightRef.current.material.emissive.setHex(isGreen ? 0x22ff44 : 0x002200);
      greenLightRef.current.material.emissiveIntensity = isGreen ? 2.8 : 0.1;
    }
    if (greenPointLightRef.current) {
      greenPointLightRef.current.intensity = isGreen ? 2.5 : 0.0;
    }
  }, [barrierState, decision]);

  // FastAPI yoklama (Polling) döngüsü
  useEffect(() => {
    let active = true;

    async function checkApi() {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);
        const res = await fetch(API_CONFIG.STATE_ENDPOINT, {
          signal: controller.signal,
          headers: { Authorization: `Bearer ${API_CONFIG.AUTH_TOKEN}` },
        });
        clearTimeout(timeoutId);

        if (!active) return;
        if (res.ok) {
          const data = await res.json();
          setApiConnected(true);
          if (!isManualOverride) {
            if (data.plate_text) setPlateText(data.plate_text);
            if (data.confidence !== undefined) setConfidence(data.confidence);
            if (data.decision) setDecision(data.decision);
            if (data.barrier_state === "open" || data.barrier_state === "opening") {
              setBarrierState("open");
            } else if (data.barrier_state === "closed") {
              setBarrierState("closed");
            }
            setLastEventTime(new Date().toLocaleTimeString("tr-TR"));
          }
        } else {
          setApiConnected(false);
        }
      } catch {
        if (active) setApiConnected(false);
      }
    }

    checkApi();
    const interval = setInterval(checkApi, API_CONFIG.POLL_INTERVAL_MS);
    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [isManualOverride]);

  // Three.js Sahnesi Kurulumu
  useEffect(() => {
    const container = containerRef.current;
    if (!container || typeof window === "undefined" || isJSDOM()) return;

    // WebGL destek denetimi
    try {
      const testCanvas = document.createElement("canvas");
      const gl = testCanvas.getContext("webgl") || testCanvas.getContext("experimental-webgl");
      if (!gl) return;
    } catch {
      return;
    }

    const width = container.clientWidth || 800;
    const height = 480;

    // Sahne, Kamera, Renderer
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf1f3f5);

    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    camera.position.set(15, 12, 15);
    camera.lookAt(0, 1.2, 0);
    cameraRef.current = camera;

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.maxPolarAngle = Math.PI / 2.05; // Zeminin altına inmeyi engelle
    controls.minDistance = 6;
    controls.maxDistance = 35;
    controls.target.set(0, 1.2, 0);
    controlsRef.current = controls;

    // Işıklandırma
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const sunLight = new THREE.DirectionalLight(0xffffff, 1.1);
    sunLight.position.set(16, 24, 12);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 1024;
    sunLight.shadow.mapSize.height = 1024;
    sunLight.shadow.camera.near = 0.5;
    sunLight.shadow.camera.far = 50;
    sunLight.shadow.camera.left = -12;
    sunLight.shadow.camera.right = 12;
    sunLight.shadow.camera.top = 12;
    sunLight.shadow.camera.bottom = -12;
    scene.add(sunLight);

    const fillLight = new THREE.DirectionalLight(0xdbeafe, 0.4);
    fillLight.position.set(-14, 10, -10);
    scene.add(fillLight);

    // ==========================================
    // 1. ZEMİN VE YOL (Screenshot 2026-11-01 223629)
    // ==========================================
    // Asfalt Yol
    const roadGeo = new THREE.PlaneGeometry(28, 28);
    const roadMat = new THREE.MeshStandardMaterial({ color: 0x33373b, roughness: 0.8 });
    const road = new THREE.Mesh(roadGeo, roadMat);
    road.rotation.x = -Math.PI / 2;
    road.receiveShadow = true;
    scene.add(road);

    // Yol Beyaz Şerit Çizgileri (Kesik Çizgiler)
    for (let z = -10; z <= 10; z += 3.2) {
      const dashGeo = new THREE.PlaneGeometry(0.2, 1.6);
      const dashMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const dash = new THREE.Mesh(dashGeo, dashMat);
      dash.rotation.x = -Math.PI / 2;
      dash.position.set(-3.2, 0.02, z);
      scene.add(dash);
    }

    // Yol Yön Oku (Beyaz İleri Oku)
    const arrowStemGeo = new THREE.PlaneGeometry(0.35, 1.4);
    const whiteMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const arrowStem = new THREE.Mesh(arrowStemGeo, whiteMat);
    arrowStem.rotation.x = -Math.PI / 2;
    arrowStem.position.set(-1.8, 0.02, 3.5);
    scene.add(arrowStem);

    const arrowHeadGeo = new THREE.BufferGeometry();
    const vertices = new Float32Array([
      -0.5, 0.02, 2.8,
       0.5, 0.02, 2.8,
       0.0, 0.02, 2.0
    ]);
    arrowHeadGeo.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    const arrowHead = new THREE.Mesh(arrowHeadGeo, whiteMat);
    scene.add(arrowHead);

    // Otopark "P" Alanı
    const pStem = new THREE.Mesh(new THREE.PlaneGeometry(0.25, 1.2), whiteMat);
    pStem.rotation.x = -Math.PI / 2;
    pStem.position.set(4.5, 0.02, -5.5);
    scene.add(pStem);
    const pLoop = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.6), whiteMat);
    pLoop.rotation.x = -Math.PI / 2;
    pLoop.position.set(4.8, 0.02, -5.8);
    scene.add(pLoop);

    // ==========================================
    // 2. REFÜJ / KALDIRIM PLATFORMU
    // ==========================================
    const sidewalkGroup = new THREE.Group();

    // Beton Zemin
    const curbBaseGeo = new THREE.BoxGeometry(4.6, 0.22, 10.5);
    const curbBaseMat = new THREE.MeshStandardMaterial({ color: 0xdde2e7, roughness: 0.5 });
    const curbBase = new THREE.Mesh(curbBaseGeo, curbBaseMat);
    curbBase.position.set(2.4, 0.11, 0);
    curbBase.receiveShadow = true;
    sidewalkGroup.add(curbBase);

    // Yeşil Çim Alanı
    const lawnGeo = new THREE.BoxGeometry(3.6, 0.05, 4.2);
    const lawnMat = new THREE.MeshStandardMaterial({ color: 0x38a169, roughness: 0.6 });
    const lawn = new THREE.Mesh(lawnGeo, lawnMat);
    lawn.position.set(2.4, 0.23, 2.8);
    sidewalkGroup.add(lawn);

    // Siyah-Beyaz Bordür Taşları (Yol Kenarı)
    for (let i = 0; i < 18; i++) {
      const isBlack = i % 2 === 0;
      const stoneGeo = new THREE.BoxGeometry(0.2, 0.24, 0.55);
      const stoneMat = new THREE.MeshStandardMaterial({ color: isBlack ? 0x1a202c : 0xf8fafc, roughness: 0.4 });
      const stone = new THREE.Mesh(stoneGeo, stoneMat);
      stone.position.set(0.05, 0.12, -4.9 + i * 0.58);
      sidewalkGroup.add(stone);
    }
    scene.add(sidewalkGroup);

    // ==========================================
    // 3. GÜVENLİK KULÜBESİ (Kırmızı Tabelalı)
    // ==========================================
    const cabinGroup = new THREE.Group();

    // Beyaz Kulübe Gövdesi
    const cabinBodyGeo = new THREE.BoxGeometry(2.4, 2.2, 2.2);
    const cabinBodyMat = new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.3 });
    const cabinBody = new THREE.Mesh(cabinBodyGeo, cabinBodyMat);
    cabinBody.position.set(2.4, 1.3, -2.4);
    cabinBody.castShadow = true;
    cabinBody.receiveShadow = true;
    cabinGroup.add(cabinBody);

    // Çatı (Koyu Gri)
    const cabinRoofGeo = new THREE.BoxGeometry(2.6, 0.15, 2.4);
    const cabinRoofMat = new THREE.MeshStandardMaterial({ color: 0x2d3748, roughness: 0.4 });
    const cabinRoof = new THREE.Mesh(cabinRoofGeo, cabinRoofMat);
    cabinRoof.position.set(2.4, 2.45, -2.4);
    cabinRoof.castShadow = true;
    cabinGroup.add(cabinRoof);

    // Cam Pencereler
    const windowMat = new THREE.MeshStandardMaterial({ color: 0x93c5fd, roughness: 0.1, transparent: true, opacity: 0.7 });
    const frontWindow = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 0.8), windowMat);
    frontWindow.position.set(1.19, 1.5, -2.4);
    frontWindow.rotation.y = -Math.PI / 2;
    cabinGroup.add(frontWindow);

    // "GÜVENLİK" Kırmızı Tabelası
    const signTex = createTextTexture("GÜVENLİK", "#dc2626", "#ffffff");
    const signMat = signTex
      ? new THREE.MeshBasicMaterial({ map: signTex })
      : new THREE.MeshStandardMaterial({ color: 0xdc2626 });
    const signGeo = new THREE.BoxGeometry(0.08, 0.45, 1.6);
    const signMesh = new THREE.Mesh(signGeo, signMat);
    signMesh.position.set(1.15, 2.65, -2.4);
    cabinGroup.add(signMesh);

    scene.add(cabinGroup);

    // ==========================================
    // 4. BARİYER KABİNİ VE HAREKETLİ KOL
    // ==========================================
    const barrierStandGroup = new THREE.Group();

    // Beyaz Bariyer Kabini
    const standBodyGeo = new THREE.BoxGeometry(1.1, 1.8, 1.0);
    const standBodyMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 });
    const standBody = new THREE.Mesh(standBodyGeo, standBodyMat);
    standBody.position.set(0.65, 1.1, -0.6);
    standBody.castShadow = true;
    barrierStandGroup.add(standBody);

    // Kabin Üst Kapağı
    const standCapGeo = new THREE.BoxGeometry(1.18, 0.15, 1.08);
    const standCapMat = new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.4 });
    const standCap = new THREE.Mesh(standCapGeo, standCapMat);
    standCap.position.set(0.65, 2.05, -0.6);
    barrierStandGroup.add(standCap);

    // Kabin Yanı Siyah Havalandırma / Port
    const sidePortGeo = new THREE.CylinderGeometry(0.22, 0.22, 0.08, 16);
    const blackMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.6 });
    const sidePort = new THREE.Mesh(sidePortGeo, blackMat);
    sidePort.rotation.z = Math.PI / 2;
    sidePort.position.set(0.08, 0.8, -0.6);
    barrierStandGroup.add(sidePort);

    // Sarı-Siyah Uyarı Çizgileri
    const hazardGeo = new THREE.BoxGeometry(0.02, 0.35, 0.6);
    const hazardMat = new THREE.MeshStandardMaterial({ color: 0xeab308, roughness: 0.4 });
    const hazard = new THREE.Mesh(hazardGeo, hazardMat);
    hazard.position.set(0.09, 1.4, -0.6);
    barrierStandGroup.add(hazard);

    scene.add(barrierStandGroup);

    // ==========================================
    // HAREKETLİ BARİYER KOLU (KIRMIZI-BEYAZ ŞERİTLİ)
    // ==========================================
    const armPivot = new THREE.Group();
    armPivot.position.set(0.1, 1.7, -0.6); // Dönen mil ekseni

    // Döner Mil Bağlantısı (Beyaz Silindir)
    const pivotPinGeo = new THREE.CylinderGeometry(0.14, 0.14, 0.24, 16);
    const pivotPin = new THREE.Mesh(pivotPinGeo, standBodyMat);
    pivotPin.rotation.x = Math.PI / 2;
    armPivot.add(pivotPin);

    // Kol Gövdesi (Kırmızı ve Beyaz Ardışık 8 Parça)
    const armLength = 5.6;
    const segmentCount = 8;
    const segLen = armLength / segmentCount;

    for (let s = 0; s < segmentCount; s++) {
      const isRed = s % 2 === 0;
      const segGeo = new THREE.CylinderGeometry(0.065, 0.065, segLen, 12);
      const segMat = new THREE.MeshStandardMaterial({
        color: isRed ? 0xef4444 : 0xffffff,
        roughness: 0.3
      });
      const seg = new THREE.Mesh(segGeo, segMat);
      // Kol X ekseni yönünde sola doğru uzanır
      seg.rotation.z = Math.PI / 2;
      seg.position.set(-(s * segLen + segLen / 2), 0, 0);
      seg.castShadow = true;
      armPivot.add(seg);
    }

    // Uç Yuvarlak Kırmızı Başlık
    const tipGeo = new THREE.SphereGeometry(0.08, 12, 12);
    const tipMat = new THREE.MeshStandardMaterial({ color: 0xef4444 });
    const tip = new THREE.Mesh(tipGeo, tipMat);
    tip.position.set(-armLength, 0, 0);
    armPivot.add(tip);

    armPivotRef.current = armPivot;
    scene.add(armPivot);

    // ==========================================
    // 5. YOLUN KARŞISINDAKİ SARI DESTEK ÇATALI
    // ==========================================
    const supportGroup = new THREE.Group();
    supportGroup.position.set(-5.6, 0, -0.6);

    const supportBaseGeo = new THREE.BoxGeometry(0.65, 0.1, 0.65);
    const yellowMat = new THREE.MeshStandardMaterial({ color: 0xeab308, roughness: 0.4 });
    const supportBase = new THREE.Mesh(supportBaseGeo, yellowMat);
    supportBase.position.y = 0.05;
    supportGroup.add(supportBase);

    const supportPoleGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.5, 12);
    const supportPole = new THREE.Mesh(supportPoleGeo, blackMat);
    supportPole.position.y = 0.8;
    supportGroup.add(supportPole);

    // U-Çatal (Kolun Oturduğu Yuva)
    const forkGeo = new THREE.BoxGeometry(0.3, 0.25, 0.35);
    const fork = new THREE.Mesh(forkGeo, yellowMat);
    fork.position.y = 1.6;
    supportGroup.add(fork);

    scene.add(supportGroup);

    // ==========================================
    // 6. AKILLI TOTEM (ESP32-CAM + TRAFİK IŞIĞI + HC-SR04)
    // ==========================================
    const totemGroup = new THREE.Group();
    totemGroup.position.set(1.4, 0, 0.9);

    // Beyaz Totem Gövdesi
    const totemBodyGeo = new THREE.BoxGeometry(1.2, 2.6, 1.2);
    const totemBody = new THREE.Mesh(totemBodyGeo, standBodyMat);
    totemBody.position.y = 1.5;
    totemBody.castShadow = true;
    totemGroup.add(totemBody);

    // Totem Üst Başlığı (Koyu Gri Eğimli Şapka)
    const totemRoofGeo = new THREE.BoxGeometry(1.3, 0.18, 1.3);
    const totemRoof = new THREE.Mesh(totemRoofGeo, standCapMat);
    totemRoof.position.y = 2.85;
    totemGroup.add(totemRoof);

    // Kamera Modülü (OV2640 Lens - Öne ve Aşağı Açılı)
    const camGeo = new THREE.CylinderGeometry(0.18, 0.14, 0.4, 16);
    const cam = new THREE.Mesh(camGeo, blackMat);
    cam.rotation.x = -Math.PI / 3;
    cam.position.set(0, 2.6, 0.65);
    totemGroup.add(cam);

    // Trafik Lambası Paneli (Siyah Kutu)
    const lightBoxGeo = new THREE.BoxGeometry(0.35, 0.85, 0.08);
    const lightBox = new THREE.Mesh(lightBoxGeo, blackMat);
    lightBox.position.set(0, 1.6, 0.62);
    totemGroup.add(lightBox);

    // Kırmızı LED (Üst Işık)
    const redLightMat = new THREE.MeshStandardMaterial({
      color: 0xff0000,
      emissive: 0xff2222,
      emissiveIntensity: 2.5,
      roughness: 0.2
    });
    const redLight = new THREE.Mesh(new THREE.SphereGeometry(0.11, 14, 14), redLightMat);
    redLight.position.set(0, 1.82, 0.66);
    totemGroup.add(redLight);
    redLightRef.current = redLight;

    const redPoint = new THREE.PointLight(0xff2222, 2.0, 3.5);
    redPoint.position.set(0, 1.82, 0.8);
    totemGroup.add(redPoint);
    redPointLightRef.current = redPoint;

    // Yeşil LED (Alt Işık)
    const greenLightMat = new THREE.MeshStandardMaterial({
      color: 0x00ff00,
      emissive: 0x002200,
      emissiveIntensity: 0.1,
      roughness: 0.2
    });
    const greenLight = new THREE.Mesh(new THREE.SphereGeometry(0.11, 14, 14), greenLightMat);
    greenLight.position.set(0, 1.42, 0.66);
    totemGroup.add(greenLight);
    greenLightRef.current = greenLight;

    const greenPoint = new THREE.PointLight(0x22ff44, 0.0, 3.5);
    greenPoint.position.set(0, 1.42, 0.8);
    totemGroup.add(greenPoint);
    greenPointLightRef.current = greenPoint;

    // HC-SR04 Ultrasonik Sensör Gözleri (Metalik İki Silindir)
    const sensorMetalMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.85, roughness: 0.2 });
    for (const offset of [-0.24, 0.24]) {
      const eye = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.16, 0.16, 16), sensorMetalMat);
      eye.rotation.x = Math.PI / 2;
      eye.position.set(offset, 0.45, 0.65);
      totemGroup.add(eye);
      // Sensör ızgara merkezi
      const innerMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.12, 0.17, 16), blackMat);
      innerMesh.rotation.x = Math.PI / 2;
      innerMesh.position.set(offset, 0.45, 0.65);
      totemGroup.add(innerMesh);
    }

    scene.add(totemGroup);

    // Totem Arkası Beyaz Ekipman Kabini
    const equipGeo = new THREE.BoxGeometry(1.6, 1.1, 2.2);
    const equip = new THREE.Mesh(equipGeo, standBodyMat);
    equip.position.set(3.0, 0.75, 1.0);
    equip.castShadow = true;
    scene.add(equip);

    // ==========================================
    // ANİMASYON DÖNGÜSÜ
    // ==========================================
    let animationFrameId: number;
    const clock = new THREE.Clock();

    function animate() {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Bariyer Açısı Yumuşak İnterpolasyon (Lerp - Z ekseninde yukarı dikey hareket)
      if (armPivotRef.current) {
        const currentRot = armPivotRef.current.rotation.z;
        let targetRot = targetAngleRef.current;

        // Ret durumunda küçük titreme efekti
        if (isDenyShakingRef.current) {
          targetRot = Math.sin(elapsedTime * 35) * 0.04;
        }

        armPivotRef.current.rotation.z = THREE.MathUtils.lerp(currentRot, targetRot, 0.08);
      }

      controls.update();
      renderer.render(scene, camera);
    }

    animate();

    // Boyut Değişimi Dinleyicisi
    function handleResize() {
      if (!container) return;
      const newWidth = container.clientWidth;
      camera.aspect = newWidth / height;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, height);
    }

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      cancelAnimationFrame(animationFrameId);
      controls.dispose();
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  // İnteraktif Test Aksiyonları
  const handleTestAllow = useCallback(() => {
    setIsManualOverride(true);
    setPlateText("34 DMO 01");
    setConfidence(0.98);
    setDecision("allow");
    setBarrierState("open");
    setLastEventTime(new Date().toLocaleTimeString("tr-TR") + " (Test İzin)");
  }, []);

  const handleTestDeny = useCallback(() => {
    setIsManualOverride(true);
    setPlateText("34 XYZ 99");
    setConfidence(0.93);
    setDecision("deny");
    setBarrierState("closed");
    setLastEventTime(new Date().toLocaleTimeString("tr-TR") + " (Test Ret)");
  }, []);

  const handleTestClose = useCallback(() => {
    setIsManualOverride(true);
    setBarrierState("closed");
    setDecision("idle");
    setLastEventTime(new Date().toLocaleTimeString("tr-TR") + " (Bariyer Kapandı)");
  }, []);

  const handleResetCamera = useCallback(() => {
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(15, 12, 15);
      controlsRef.current.target.set(0, 1.2, 0);
      controlsRef.current.update();
    }
  }, []);

  const handleSyncWithApi = useCallback(() => {
    setIsManualOverride(false);
  }, []);

  return (
    <div className="model3d-wrapper">
      {/* 3D Görsel Üst Bilgi Rozetleri (HUD) */}
      <div className="model3d-hud">
        <div className="hud-pill">
          <span className={`status-dot ${barrierState === "open" ? "dot-open" : "dot-closed"}`} />
          <strong>Bariyer:</strong> {barrierState === "open" ? "AÇIK (90°)" : "KAPALI (0°)"}
        </div>

        <div className="hud-pill">
          <strong>Plaka:</strong> {plateText ?? "Okunuyor..."}
          {confidence && <span className="hud-sub"> (%{Math.round(confidence * 100)})</span>}
        </div>

        <div className={`hud-pill ${decision === "allow" ? "hud-allow" : decision === "deny" ? "hud-deny" : ""}`}>
          <strong>Karar:</strong>{" "}
          {decision === "allow" ? "İZİN VERİLDİ" : decision === "deny" ? "ERİŞİM REDDİ" : "BEKLEMEDE"}
        </div>

        <div className={`hud-pill api-status-pill ${apiConnected ? "api-live" : "api-waiting"}`}>
          <Icon name="link" />
          <span>{apiConnected ? "FastAPI Bağlı (Canlı)" : "API Bekleniyor · Simülasyon Aktif"}</span>
        </div>
      </div>

      {/* Three.js Tuval Alanı */}
      <div ref={containerRef} className="model3d-canvas-container" aria-label="3D Bariyer Maketi Görünümü" />

      {/* Alt Kontrol ve Bilgi Çubuğu */}
      <div className="model3d-control-bar">
        <div className="action-buttons">
          <button type="button" className="test-btn btn-allow" onClick={handleTestAllow}>
            Test: İzin Verildi (Aç)
          </button>
          <button type="button" className="test-btn btn-deny" onClick={handleTestDeny}>
            Test: Erişim Reddi (Kapalı)
          </button>
          <button type="button" className="test-btn btn-close" onClick={handleTestClose}>
            Test: Alan Boşaldı (Kapat)
          </button>
        </div>

        <div className="tool-buttons">
          <button type="button" className="tool-btn" onClick={handleResetCamera} title="Kamera Açısını Sıfırla">
            Kamerayı Sıfırla
          </button>
          {isManualOverride && (
            <button type="button" className="tool-btn btn-sync" onClick={handleSyncWithApi} title="Canlı API verilerini dinlemeye geri dön">
              Canlı API&apos;ye Dön
            </button>
          )}
        </div>
      </div>

      <div className="model3d-endpoint-note">
        <span className="text-secondary text-caption">
          <strong>API Entegrasyon Ucu:</strong> <code>{API_CONFIG.STATE_ENDPOINT}</code> · Fare ile sürükleyerek maketi 360° inceleyebilirsiniz.
        </span>
        <span className="text-secondary text-caption">
          Son Olay: {lastEventTime}
        </span>
      </div>
    </div>
  );
}
