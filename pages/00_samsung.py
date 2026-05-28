import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="FPS Aim Trainer",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .stApp { background: #0a0a0f; }
    #MainMenu, header, footer { visibility: hidden; }
    .block-container { padding: 0 !important; margin: 0 !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

HTML = r"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0a0a0f; overflow:hidden; font-family:'Courier New',monospace; }
  #c { display:block; width:100vw; height:100vh; }

  /* HUD */
  #hud {
    position:fixed; top:0; left:0; width:100%; height:100%;
    pointer-events:none; z-index:10;
  }

  /* 크로스헤어 */
  #crosshair {
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
    width:24px; height:24px;
  }
  .ch-h { position:absolute; top:50%; left:50%;
    width:10px; height:2px; background:#00ff88;
    box-shadow:0 0 4px #00ff88;
    transform:translate(-50%,-50%);
  }
  .ch-h.left  { transform:translate(calc(-50% - 6px),-50%); }
  .ch-h.right { transform:translate(calc(-50% + 6px),-50%); }
  .ch-v { position:absolute; top:50%; left:50%;
    width:2px; height:10px; background:#00ff88;
    box-shadow:0 0 4px #00ff88;
    transform:translate(-50%,-50%);
  }
  .ch-v.top    { transform:translate(-50%, calc(-50% - 6px)); }
  .ch-v.bottom { transform:translate(-50%, calc(-50% + 6px)); }

  /* 상단 정보 */
  #info-bar {
    position:absolute; top:16px; left:50%; transform:translateX(-50%);
    display:flex; gap:32px; align-items:center;
  }
  .info-block {
    background:rgba(0,0,0,0.55); border:1px solid rgba(0,255,136,0.25);
    padding:6px 18px; border-radius:4px; text-align:center;
  }
  .info-label { font-size:10px; color:#888; letter-spacing:2px; text-transform:uppercase; }
  .info-val   { font-size:22px; font-weight:700; color:#fff; }
  #timer-val  { color:#00ff88; }
  #score-val  { color:#fff; }
  #acc-val    { color:#f0c040; }

  /* 왼쪽 탄약 */
  #ammo-box {
    position:absolute; bottom:28px; right:40px;
    text-align:right;
  }
  #ammo-cur { font-size:42px; font-weight:700; color:#fff; line-height:1; }
  #ammo-max { font-size:18px; color:#666; }
  #ammo-label { font-size:10px; color:#888; letter-spacing:2px; }

  /* 킬피드 */
  #killfeed {
    position:absolute; top:70px; right:20px;
    display:flex; flex-direction:column; gap:4px;
    align-items:flex-end;
  }
  .kf-item {
    background:rgba(0,255,136,0.12); border-left:2px solid #00ff88;
    padding:3px 10px; font-size:12px; color:#00ff88;
    animation: kf-fade 2s forwards;
  }
  @keyframes kf-fade { 0%{opacity:1} 70%{opacity:1} 100%{opacity:0} }

  /* 히트마커 */
  #hitmarker {
    position:absolute; top:50%; left:50%;
    transform:translate(-50%,-50%);
    width:20px; height:20px; opacity:0;
    pointer-events:none;
  }
  .hm-line {
    position:absolute; background:#ff4444;
    box-shadow:0 0 4px #ff4444;
  }
  .hm-tl { width:6px;height:2px; top:3px; left:3px; transform:rotate(45deg); }
  .hm-tr { width:6px;height:2px; top:3px; right:3px; transform:rotate(-45deg); }
  .hm-bl { width:6px;height:2px; bottom:3px; left:3px; transform:rotate(-45deg); }
  .hm-br { width:6px;height:2px; bottom:3px; right:3px; transform:rotate(45deg); }

  /* 총기 흔들림 억제를 위한 wrapper */
  #gun-wrap {
    position:fixed; bottom:0; right:0;
    width:380px; height:260px;
    pointer-events:none; z-index:9;
    overflow:hidden;
  }
  #gun-svg { position:absolute; bottom:-10px; right:-10px; }

  /* 시작 오버레이 */
  #overlay {
    position:fixed; inset:0;
    background:rgba(0,0,0,0.88);
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    z-index:100; gap:16px;
  }
  #overlay h1 { font-size:52px; font-weight:700; color:#fff; letter-spacing:4px; }
  #overlay h1 span { color:#00ff88; }
  #overlay p  { font-size:14px; color:#888; letter-spacing:1px; }
  #start-btn {
    margin-top:12px; padding:14px 48px;
    background:transparent; border:2px solid #00ff88;
    color:#00ff88; font-size:16px; letter-spacing:3px;
    cursor:pointer; text-transform:uppercase;
    transition:all .2s;
  }
  #start-btn:hover { background:#00ff88; color:#000; }
  .key-hint { font-size:12px; color:#555; }

  /* 일시정지 / 결과 */
  #result-overlay {
    position:fixed; inset:0;
    background:rgba(0,0,0,0.85);
    display:none; flex-direction:column;
    align-items:center; justify-content:center;
    z-index:100; gap:20px;
  }
  #result-overlay h2 { font-size:36px; color:#fff; letter-spacing:3px; }
  .result-row { display:flex; gap:48px; }
  .result-block { text-align:center; }
  .result-block .rl { font-size:11px; color:#888; letter-spacing:2px; text-transform:uppercase; }
  .result-block .rv { font-size:32px; font-weight:700; color:#00ff88; }
  #restart-btn {
    padding:12px 40px; background:transparent;
    border:2px solid #00ff88; color:#00ff88;
    font-size:14px; letter-spacing:3px;
    cursor:pointer; text-transform:uppercase;
    transition:all .2s;
  }
  #restart-btn:hover { background:#00ff88; color:#000; }

  /* 마우스 잠금 안내 */
  #lock-hint {
    position:fixed; bottom:16px; left:50%; transform:translateX(-50%);
    background:rgba(0,0,0,0.7); border:1px solid #555;
    padding:6px 18px; font-size:12px; color:#888;
    border-radius:4px; display:none;
  }
</style>
</head>
<body>

<canvas id="c"></canvas>

<!-- HUD -->
<div id="hud">
  <!-- 크로스헤어 -->
  <div id="crosshair">
    <div class="ch-h left"></div>
    <div class="ch-h right"></div>
    <div class="ch-v top"></div>
    <div class="ch-v bottom"></div>
  </div>

  <!-- 상단 정보바 -->
  <div id="info-bar">
    <div class="info-block">
      <div class="info-label">Score</div>
      <div class="info-val" id="score-val">0</div>
    </div>
    <div class="info-block">
      <div class="info-label">Time</div>
      <div class="info-val" id="timer-val">60</div>
    </div>
    <div class="info-block">
      <div class="info-label">Accuracy</div>
      <div class="info-val" id="acc-val">--%</div>
    </div>
  </div>

  <!-- 킬피드 -->
  <div id="killfeed"></div>

  <!-- 히트마커 -->
  <div id="hitmarker">
    <div class="hm-line hm-tl"></div>
    <div class="hm-line hm-tr"></div>
    <div class="hm-line hm-bl"></div>
    <div class="hm-line hm-br"></div>
  </div>

  <!-- 탄약 -->
  <div id="ammo-box">
    <div class="info-label" id="ammo-label">AMMO</div>
    <div><span id="ammo-cur">12</span> <span id="ammo-max">/ 12</span></div>
  </div>
</div>

<!-- 권총 SVG -->
<div id="gun-wrap">
  <svg id="gun-svg" width="360" height="240" viewBox="0 0 360 240" xmlns="http://www.w3.org/2000/svg">
    <!-- 슬라이드 (상단) -->
    <rect x="80" y="60" width="200" height="38" rx="5" fill="#222" stroke="#444" stroke-width="1.5"/>
    <!-- 슬라이드 세레이션 -->
    <line x1="240" y1="62" x2="240" y2="96" stroke="#555" stroke-width="1.2"/>
    <line x1="248" y1="62" x2="248" y2="96" stroke="#555" stroke-width="1.2"/>
    <line x1="256" y1="62" x2="256" y2="96" stroke="#555" stroke-width="1.2"/>
    <line x1="264" y1="62" x2="264" y2="96" stroke="#555" stroke-width="1.2"/>
    <!-- 배럴 -->
    <rect x="60" y="70" width="22" height="18" rx="3" fill="#1a1a1a" stroke="#555" stroke-width="1"/>
    <circle cx="62" cy="79" r="6" fill="#111" stroke="#666" stroke-width="1"/>
    <!-- 총구 플래시 숨김 초기 -->
    <g id="muzzle-flash" opacity="0">
      <polygon points="55,79 40,72 35,79 40,86" fill="#ffcc00"/>
      <polygon points="50,79 32,68 28,79 32,90" fill="#ff8800" opacity="0.7"/>
    </g>
    <!-- 그립 -->
    <path d="M200,96 L210,96 L225,180 L200,180 L185,160 L195,96 Z" fill="#1e1e1e" stroke="#444" stroke-width="1.2"/>
    <!-- 그립 텍스처 -->
    <line x1="195" y1="110" x2="210" y2="110" stroke="#333" stroke-width="1"/>
    <line x1="196" y1="120" x2="211" y2="120" stroke="#333" stroke-width="1"/>
    <line x1="197" y1="130" x2="212" y2="130" stroke="#333" stroke-width="1"/>
    <line x1="198" y1="140" x2="213" y2="140" stroke="#333" stroke-width="1"/>
    <line x1="199" y1="150" x2="214" y2="150" stroke="#333" stroke-width="1"/>
    <!-- 트리거 가드 -->
    <path d="M195,96 Q190,130 200,140 L210,140 Q215,130 210,96" fill="none" stroke="#555" stroke-width="1.5"/>
    <!-- 트리거 -->
    <line x1="200" y1="110" x2="207" y2="125" stroke="#888" stroke-width="2.5" stroke-linecap="round"/>
    <!-- 슬라이드 위 사이트 -->
    <rect x="100" y="57" width="10" height="5" rx="1" fill="#555"/>
    <rect x="240" y="57" width="14" height="5" rx="1" fill="#555"/>
    <!-- 매거진 -->
    <rect x="196" y="178" width="18" height="38" rx="3" fill="#1a1a1a" stroke="#444" stroke-width="1"/>
    <!-- 핸드 (간략한) -->
    <path d="M205,160 Q260,155 280,170 L285,180 Q265,185 215,178 Z" fill="#c8a882" stroke="#a08060" stroke-width="1"/>
    <path d="M215,178 Q265,185 280,195 L275,205 Q240,200 210,192 Z" fill="#c0a07a"/>
  </svg>
</div>

<!-- 시작 오버레이 -->
<div id="overlay">
  <h1>AIM <span>TRAINER</span></h1>
  <p>60초 안에 최대한 많은 타겟을 제거하세요</p>
  <button id="start-btn" onclick="startGame()">START</button>
  <div class="key-hint">클릭 → 마우스 잠금 &nbsp;|&nbsp; ESC → 해제 &nbsp;|&nbsp; R → 재장전</div>
</div>

<!-- 결과 오버레이 -->
<div id="result-overlay">
  <h2>ROUND COMPLETE</h2>
  <div class="result-row">
    <div class="result-block"><div class="rl">Score</div><div class="rv" id="r-score">0</div></div>
    <div class="result-block"><div class="rl">Hits</div><div class="rv" id="r-hits">0</div></div>
    <div class="result-block"><div class="rl">Accuracy</div><div class="rv" id="r-acc">0%</div></div>
    <div class="result-block"><div class="rl">Best Streak</div><div class="rv" id="r-streak">0</div></div>
  </div>
  <button id="restart-btn" onclick="restartGame()">PLAY AGAIN</button>
</div>

<div id="lock-hint">클릭하면 마우스 잠금 (포인터 컨트롤 활성화)</div>

<!-- Three.js -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
// ─────────────────────────────────────────────
//  SCENE SETUP
// ─────────────────────────────────────────────
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x1a1a2e);
scene.fog = new THREE.Fog(0x1a1a2e, 20, 80);

const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 200);
camera.position.set(0, 1.7, 0);

function resize() {
  renderer.setSize(window.innerWidth, window.innerHeight);
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
}
resize();
window.addEventListener('resize', resize);

// ─────────────────────────────────────────────
//  LIGHTING
// ─────────────────────────────────────────────
const ambient = new THREE.AmbientLight(0x404060, 0.6);
scene.add(ambient);

const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(10, 20, 10);
dirLight.castShadow = true;
dirLight.shadow.mapSize.set(1024, 1024);
scene.add(dirLight);

// 포인트 라이트 (훈련장 느낌)
[[-10,4,0],[10,4,0],[0,4,-15],[0,4,-30]].forEach(([x,y,z]) => {
  const pl = new THREE.PointLight(0x6699ff, 0.5, 25);
  pl.position.set(x, y, z);
  scene.add(pl);
});

// ─────────────────────────────────────────────
//  ENVIRONMENT (훈련장)
// ─────────────────────────────────────────────

// 바닥
const floorGeo = new THREE.PlaneGeometry(40, 80);
const floorMat = new THREE.MeshLambertMaterial({ color: 0x1a1a1a });
const floor = new THREE.Mesh(floorGeo, floorMat);
floor.rotation.x = -Math.PI / 2;
floor.position.z = -20;
floor.receiveShadow = true;
scene.add(floor);

// 바닥 그리드
const grid = new THREE.GridHelper(80, 40, 0x333355, 0x222244);
grid.position.z = -20;
scene.add(grid);

// 천장
const ceilGeo = new THREE.PlaneGeometry(40, 80);
const ceilMat = new THREE.MeshLambertMaterial({ color: 0x111122, side: THREE.DoubleSide });
const ceil = new THREE.Mesh(ceilGeo, ceilMat);
ceil.rotation.x = Math.PI / 2;
ceil.position.set(0, 5, -20);
scene.add(ceil);

// 벽들
function makeWall(w, h, color, x, y, z, ry=0) {
  const m = new THREE.Mesh(
    new THREE.PlaneGeometry(w, h),
    new THREE.MeshLambertMaterial({ color, side: THREE.DoubleSide })
  );
  m.position.set(x, y, z);
  m.rotation.y = ry;
  scene.add(m);
}
makeWall(40, 5, 0x111133, 0, 2.5, -60);           // 뒷벽
makeWall(80, 5, 0x111133, -20, 2.5, -20, Math.PI/2); // 왼벽
makeWall(80, 5, 0x111133,  20, 2.5, -20, Math.PI/2); // 오른벽

// 형광등 느낌 라이트 패널
function makeLightPanel(x, z) {
  const geo = new THREE.PlaneGeometry(3, 0.3);
  const mat = new THREE.MeshBasicMaterial({ color: 0x8899ff, side: THREE.DoubleSide });
  const m = new THREE.Mesh(geo, mat);
  m.rotation.x = Math.PI / 2;
  m.position.set(x, 4.9, z);
  scene.add(m);
}
[-8, 0, 8].forEach(x => [-5, -20, -35, -50].forEach(z => makeLightPanel(x, z)));

// 장식용 벽면 마크
function makeWallMark(x, z) {
  const geo = new THREE.PlaneGeometry(1.5, 1.5);
  const mat = new THREE.MeshBasicMaterial({ color: 0x223344 });
  const m = new THREE.Mesh(geo, mat);
  m.position.set(x, 2.5, z);
  scene.add(m);
}
[-15, 15].forEach(x => [-10, -25, -40].forEach(z => makeWallMark(x, z + 0.1)));

// ─────────────────────────────────────────────
//  TARGETS
// ─────────────────────────────────────────────
const COLORS = {
  normal: 0xee3333,
  hit:    0xff8800,
  head:   0xffdd00,
};

class Target {
  constructor() {
    this.group = new THREE.Group();
    this.alive = true;
    this.headshot = false;

    // 몸통
    const bodyGeo = new THREE.CylinderGeometry(0.28, 0.28, 1.2, 16);
    const bodyMat = new THREE.MeshLambertMaterial({ color: COLORS.normal });
    this.body = new THREE.Mesh(bodyGeo, bodyMat);
    this.body.position.y = 0.6;
    this.body.castShadow = true;
    this.group.add(this.body);

    // 머리
    const headGeo = new THREE.SphereGeometry(0.22, 16, 16);
    const headMat = new THREE.MeshLambertMaterial({ color: COLORS.normal });
    this.head = new THREE.Mesh(headGeo, headMat);
    this.head.position.y = 1.5;
    this.head.castShadow = true;
    this.group.add(this.head);

    // 타겟 원형 마크 (머리 앞)
    const markGeo = new THREE.CircleGeometry(0.18, 16);
    const markMat = new THREE.MeshBasicMaterial({ color: 0xffffff, opacity:0.8, transparent:true });
    this.mark = new THREE.Mesh(markGeo, markMat);
    this.mark.position.set(0, 1.5, 0.23);
    this.group.add(this.mark);

    // 중심 점
    const dotGeo = new THREE.CircleGeometry(0.05, 8);
    const dotMat = new THREE.MeshBasicMaterial({ color: 0xff0000 });
    const dot = new THREE.Mesh(dotGeo, dotMat);
    dot.position.set(0, 1.5, 0.232);
    this.group.add(dot);

    this.spawn();
  }

  spawn() {
    const x = (Math.random() - 0.5) * 28;
    const z = -8 - Math.random() * 40;
    const y = 0;
    this.group.position.set(x, y, z);
    this.alive = true;
    this.body.material.color.setHex(COLORS.normal);
    this.head.material.color.setHex(COLORS.normal);
    this.group.visible = true;

    // 거리에 따른 크기
    const dist = Math.abs(z);
    const scale = Math.max(0.7, 1.2 - dist * 0.01);
    this.group.scale.setScalar(scale);

    // 이동 여부 (랜덤)
    this.moving = Math.random() > 0.5;
    this.moveSpeed = (Math.random() * 0.015 + 0.005) * (Math.random() > 0.5 ? 1 : -1);
    this.moveRange = Math.random() * 4 + 1;
    this.moveOrigin = x;
    this.moveT = Math.random() * Math.PI * 2;
  }

  update(dt) {
    if (!this.alive) return;
    if (this.moving) {
      this.moveT += this.moveSpeed * 60 * dt;
      this.group.position.x = this.moveOrigin + Math.sin(this.moveT) * this.moveRange;
    }
  }

  die(isHead) {
    this.alive = false;
    this.headshot = isHead;
    this.group.visible = false;
  }
}

const targets = [];
const MAX_TARGETS = 8;

function spawnTargets(n) {
  for (let i = 0; i < n; i++) {
    const t = new Target();
    scene.add(t.group);
    targets.push(t);
  }
}

function respawnDead() {
  targets.forEach(t => {
    if (!t.alive) t.spawn();
  });
}

// ─────────────────────────────────────────────
//  RAYCASTER (for all meshes in targets)
// ─────────────────────────────────────────────
const raycaster = new THREE.Raycaster();
const CENTER = new THREE.Vector2(0, 0);

// ─────────────────────────────────────────────
//  GAME STATE
// ─────────────────────────────────────────────
let gameActive = false;
let score = 0;
let hits = 0;
let shots = 0;
let streak = 0;
let bestStreak = 0;
let timeLeft = 60;
let lastTime = 0;
let timerInterval = null;

const MAX_AMMO = 12;
let ammo = MAX_AMMO;
let reloading = false;

// ─────────────────────────────────────────────
//  MOUSE LOOK  (Pointer Lock + 드래그 폴백)
// ─────────────────────────────────────────────
let yaw = 0, pitch = 0;
const PITCH_LIMIT = Math.PI / 3;
const SENSITIVITY = 0.002;

let pointerLocked = false;
let dragActive = false;
let lastDragX = 0, lastDragY = 0;

// Pointer Lock
canvas.addEventListener('click', () => {
  if (!gameActive) return;
  canvas.requestPointerLock();
});

document.addEventListener('pointerlockchange', () => {
  pointerLocked = document.pointerLockElement === canvas;
  document.getElementById('lock-hint').style.display = pointerLocked ? 'none' : 'block';
});

document.addEventListener('mousemove', (e) => {
  if (!gameActive) return;
  let dx = 0, dy = 0;
  if (pointerLocked) {
    dx = e.movementX;
    dy = e.movementY;
  } else if (dragActive) {
    dx = e.clientX - lastDragX;
    dy = e.clientY - lastDragY;
    lastDragX = e.clientX;
    lastDragY = e.clientY;
  }
  yaw   -= dx * SENSITIVITY;
  pitch -= dy * SENSITIVITY;
  pitch  = Math.max(-PITCH_LIMIT, Math.min(PITCH_LIMIT, pitch));
});

// 드래그 폴백
canvas.addEventListener('mousedown', (e) => {
  if (!gameActive || pointerLocked) return;
  if (e.button === 0) {
    dragActive = true;
    lastDragX = e.clientX;
    lastDragY = e.clientY;
  }
});
window.addEventListener('mouseup', () => { dragActive = false; });

// 터치 지원
let touchLastX = 0, touchLastY = 0;
canvas.addEventListener('touchstart', e => {
  e.preventDefault();
  touchLastX = e.touches[0].clientX;
  touchLastY = e.touches[0].clientY;
});
canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  if (!gameActive) return;
  const dx = e.touches[0].clientX - touchLastX;
  const dy = e.touches[0].clientY - touchLastY;
  touchLastX = e.touches[0].clientX;
  touchLastY = e.touches[0].clientY;
  yaw   -= dx * SENSITIVITY * 0.8;
  pitch -= dy * SENSITIVITY * 0.8;
  pitch = Math.max(-PITCH_LIMIT, Math.min(PITCH_LIMIT, pitch));
}, { passive: false });

// ─────────────────────────────────────────────
//  SHOOTING
// ─────────────────────────────────────────────
let gunRecoilY = 0;
let gunRecoilX = 0;
let flashTimer = 0;
const muzzleFlash = document.getElementById('muzzle-flash');
const hitmarker   = document.getElementById('hitmarker');

function showHitmarker() {
  hitmarker.style.opacity = '1';
  setTimeout(() => { hitmarker.style.opacity = '0'; }, 120);
}

function showMuzzleFlash() {
  flashTimer = 0.08;
}

function addKillfeed(text) {
  const kf = document.getElementById('killfeed');
  const el = document.createElement('div');
  el.className = 'kf-item';
  el.textContent = text;
  kf.appendChild(el);
  setTimeout(() => el.remove(), 2200);
}

function shoot() {
  if (!gameActive || reloading || ammo <= 0) return;

  ammo--;
  shots++;
  updateAmmoHUD();

  showMuzzleFlash();
  gunRecoilY = 0.06;
  gunRecoilX = (Math.random() - 0.5) * 0.03;

  raycaster.setFromCamera(CENTER, camera);

  // 모든 타겟 메시 수집
  const meshes = [];
  const meshToTarget = new Map();
  targets.forEach(t => {
    if (!t.alive) return;
    [t.body, t.head].forEach(m => {
      meshes.push(m);
      meshToTarget.set(m, { target: t, isHead: m === t.head });
    });
  });

  const hits_arr = raycaster.intersectObjects(meshes);
  if (hits_arr.length > 0) {
    const { target, isHead } = meshToTarget.get(hits_arr[0].object);
    if (target && target.alive) {
      target.die(isHead);
      hits++;
      streak++;
      if (streak > bestStreak) bestStreak = streak;

      const pts = isHead ? 150 : 100;
      const bonus = Math.max(0, streak - 1) * 25;
      score += pts + bonus;

      showHitmarker();
      updateHUD();

      const label = isHead
        ? `💀 HEADSHOT +${pts + bonus}`
        : `✓ HIT +${pts + bonus}`;
      addKillfeed(label);

      // 잠깐 후 리스폰
      setTimeout(() => { if(gameActive) target.spawn(); }, 800 + Math.random() * 400);
    }
  } else {
    streak = 0;
  }

  if (ammo === 0) {
    setTimeout(reload, 300);
  }
}

function reload() {
  if (reloading || ammo === MAX_AMMO) return;
  reloading = true;
  const ammoEl = document.getElementById('ammo-cur');
  ammoEl.style.color = '#f0c040';
  setTimeout(() => {
    ammo = MAX_AMMO;
    reloading = false;
    ammoEl.style.color = '#fff';
    updateAmmoHUD();
  }, 1500);
}

// 클릭 / 터치로 발사
canvas.addEventListener('mousedown', e => {
  if (e.button === 0 && gameActive && pointerLocked) shoot();
});
canvas.addEventListener('touchend', e => {
  e.preventDefault();
  if (gameActive) shoot();
}, { passive: false });
document.addEventListener('keydown', e => {
  if (e.code === 'KeyR' && gameActive) reload();
});

// ─────────────────────────────────────────────
//  HUD UPDATE
// ─────────────────────────────────────────────
function updateHUD() {
  document.getElementById('score-val').textContent = score;
  const acc = shots > 0 ? Math.round((hits / shots) * 100) : '--';
  document.getElementById('acc-val').textContent = acc + (shots > 0 ? '%' : '--');
}

function updateAmmoHUD() {
  document.getElementById('ammo-cur').textContent = ammo;
}

function updateTimer() {
  document.getElementById('timer-val').textContent = timeLeft;
  if (timeLeft <= 10) {
    document.getElementById('timer-val').style.color = '#ff4444';
  }
}

// ─────────────────────────────────────────────
//  GAME FLOW
// ─────────────────────────────────────────────
function startGame() {
  document.getElementById('overlay').style.display = 'none';
  document.getElementById('result-overlay').style.display = 'none';
  document.getElementById('lock-hint').style.display = 'block';

  // 리셋
  score = 0; hits = 0; shots = 0;
  streak = 0; bestStreak = 0;
  timeLeft = 60;
  ammo = MAX_AMMO; reloading = false;
  yaw = 0; pitch = 0;
  gameActive = true;

  document.getElementById('timer-val').style.color = '#00ff88';
  updateHUD();
  updateAmmoHUD();
  updateTimer();

  // 타겟 스폰
  targets.forEach(t => { scene.remove(t.group); });
  targets.length = 0;
  spawnTargets(MAX_TARGETS);

  // 타이머
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timeLeft--;
    updateTimer();
    if (timeLeft <= 0) endGame();
  }, 1000);
}

function endGame() {
  gameActive = false;
  clearInterval(timerInterval);
  if (document.pointerLockElement) document.exitPointerLock();

  const acc = shots > 0 ? Math.round((hits / shots) * 100) : 0;
  document.getElementById('r-score').textContent  = score;
  document.getElementById('r-hits').textContent   = hits;
  document.getElementById('r-acc').textContent    = acc + '%';
  document.getElementById('r-streak').textContent = bestStreak;

  const res = document.getElementById('result-overlay');
  res.style.display = 'flex';
}

function restartGame() {
  startGame();
}

// ─────────────────────────────────────────────
//  GUN BOB ANIMATION
// ─────────────────────────────────────────────
let gunBobT = 0;
const gunWrap = document.getElementById('gun-wrap');

// ─────────────────────────────────────────────
//  RENDER LOOP
// ─────────────────────────────────────────────
let prevTime = performance.now();

function animate() {
  requestAnimationFrame(animate);
  const now = performance.now();
  const dt  = Math.min((now - prevTime) / 1000, 0.05);
  prevTime  = now;

  if (gameActive) {
    // 카메라 회전
    camera.rotation.order = 'YXZ';
    camera.rotation.y = yaw;
    camera.rotation.x = pitch;

    // 타겟 업데이트
    targets.forEach(t => t.update(dt));

    // 총 리코일 감쇠
    gunRecoilY *= 0.75;
    gunRecoilX *= 0.75;

    // 총기 bob
    gunBobT += dt * 3;
    const bobX =  Math.sin(gunBobT) * 3;
    const bobY = -Math.abs(Math.sin(gunBobT * 2)) * 2;
    const recoilPx = -gunRecoilY * 300;
    gunWrap.style.transform =
      `translate(${bobX + gunRecoilX * 200}px, ${bobY + recoilPx}px)`;

    // 머즐 플래시
    if (flashTimer > 0) {
      flashTimer -= dt;
      muzzleFlash.setAttribute('opacity', flashTimer > 0 ? '1' : '0');
    } else {
      muzzleFlash.setAttribute('opacity', '0');
    }
  }

  renderer.render(scene, camera);
}

animate();
</script>
</body>
</html>
"""

components.html(HTML, height=750, scrolling=False)
