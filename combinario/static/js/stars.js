const canvas = document.getElementById("stars-canvas");
const ctx = canvas.getContext("2d");
const COUNT = 80;
const MAX_DIST = 120;
const MAX_DIST_SQ = MAX_DIST * MAX_DIST;
const SPEED = 0.2;
const FADE_SPEED = 0.012;

let W, H, dpr;
function resize() {
  dpr = window.devicePixelRatio || 1;
  W = canvas.clientWidth;
  H = canvas.clientHeight;
  canvas.width = W * dpr;
  canvas.height = H * dpr;
  ctx.scale(dpr, dpr);
}

const px = new Float32Array(COUNT);
const py = new Float32Array(COUNT);
const vx = new Float32Array(COUNT);
const vy = new Float32Array(COUNT);
const alpha = new Float32Array(COUNT);
const dalpha = new Float32Array(COUNT);

function rand(min, max) {
  return min + Math.random() * (max - min);
}

function init() {
  resize();
  for (let i = 0; i < COUNT; i++) {
    px[i] = rand(0, W);
    py[i] = rand(0, H);
    const angle = rand(0, Math.PI * 2);
    vx[i] = Math.cos(angle) * SPEED;
    vy[i] = Math.sin(angle) * SPEED;
    alpha[i] = rand(0.2, 1);
    dalpha[i] = rand(-FADE_SPEED, FADE_SPEED);
  }
}

function tick() {
  ctx.clearRect(0, 0, W, H);

  for (let i = 0; i < COUNT; i++) {
    px[i] += vx[i];
    py[i] += vy[i];
    if (px[i] < 0) px[i] += W;
    else if (px[i] > W) px[i] -= W;
    if (py[i] < 0) py[i] += H;
    else if (py[i] > H) py[i] -= H;
    alpha[i] += dalpha[i];
    if (alpha[i] <= 0.05) {
      alpha[i] = 0.05;
      dalpha[i] = FADE_SPEED * rand(0.5, 1.5);
    } else if (alpha[i] >= 1) {
      alpha[i] = 1;
      dalpha[i] = -FADE_SPEED * rand(0.5, 1.5);
    }
  }

  for (let i = 0; i < COUNT - 1; i++) {
    for (let j = i + 1; j < COUNT; j++) {
      const dx = px[j] - px[i];
      const dy = py[j] - py[i];
      const distSq = dx * dx + dy * dy;
      if (distSq < MAX_DIST_SQ) {
        const t = 1 - distSq / MAX_DIST_SQ;
        const a = t * t * Math.min(alpha[i], alpha[j]);
        ctx.strokeStyle = `rgba(180,200,255,${a * 0.6})`;
        ctx.lineWidth = t * 1.2;
        ctx.beginPath();
        ctx.moveTo(px[i], py[i]);
        ctx.lineTo(px[j], py[j]);
        ctx.stroke();
      }
    }
  }

  for (let i = 0; i < COUNT; i++) {
    const r = 1.5 + alpha[i];
    ctx.beginPath();
    ctx.arc(px[i], py[i], r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(210,225,255,${alpha[i]})`;
    ctx.fill();
  }

  requestAnimationFrame(tick);
}

window.addEventListener("resize", () => {
  init();
});
init();
tick();
