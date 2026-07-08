/**
 * Sanskrit Proof Engine — Zoomable canvas
 * Black bg, gold Sanskrit, silver Lean. Scroll to zoom, drag to pan.
 */

const canvas = document.getElementById('canvas');
const container = document.getElementById('container');

let scale = 1;
let translateX = 0;
let translateY = 0;
let isDragging = false;
let lastX = 0;
let lastY = 0;

// Pan
container.addEventListener('mousedown', (e) => {
  if (e.target.closest('.node')) return;
  isDragging = true;
  lastX = e.clientX;
  lastY = e.clientY;
});

container.addEventListener('mousemove', (e) => {
  if (!isDragging) return;
  translateX += e.clientX - lastX;
  translateY += e.clientY - lastY;
  lastX = e.clientX;
  lastY = e.clientY;
  applyTransform();
});

container.addEventListener('mouseup', () => { isDragging = false; });
container.addEventListener('mouseleave', () => { isDragging = false; });

// Zoom (scroll wheel)
container.addEventListener('wheel', (e) => {
  e.preventDefault();
  const factor = e.deltaY > 0 ? 0.9 : 1.1;
  const newScale = Math.max(0.1, Math.min(5, scale * factor));
  const rect = container.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;
  const wx = (mx - translateX) / scale;
  const wy = (my - translateY) / scale;
  scale = newScale;
  translateX = mx - wx * scale;
  translateY = my - wy * scale;
  applyTransform();
  updateZoomClass();
}, { passive: false });

function applyTransform() {
  canvas.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
}

function updateZoomClass() {
  canvas.classList.remove('zoom-far', 'zoom-mid', 'zoom-close');
  if (scale < 0.3) canvas.classList.add('zoom-far');
  else if (scale < 0.8) canvas.classList.add('zoom-mid');
  else canvas.classList.add('zoom-close');
}

// Load and render — prefer export.json (from report_graph.py) if present
async function load() {
  let res = await fetch('data/export.json');
  if (!res.ok) res = await fetch('data/sample.json');
  const data = await res.json();
  render(data);
}

function render(data) {
  const bridgeIds = new Set();
  (data.bridges || []).forEach(b => {
    bridgeIds.add(b.node_a);
    bridgeIds.add(b.node_b);
  });

  const edges = data.edges || [];
  const nodes = data.nodes || [];

  // Edges (SVG)
  let svg = '<svg class="edges" style="position:absolute;inset:0;overflow:visible;pointer-events:none">';
  edges.forEach(({ from: fid, to: tid }) => {
    const n1 = nodes.find(n => n.id === fid);
    const n2 = nodes.find(n => n.id === tid);
    if (!n1 || !n2) return;
    const isBridge = bridgeIds.has(fid) && bridgeIds.has(tid);
    const x1 = n1.x + 180;
    const y1 = n1.y + 50;
    const x2 = n2.x + 180;
    const y2 = n2.y + 50;
    svg += `<line class="edge ${isBridge ? 'bridge' : ''}" x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}"/>`;
  });
  svg += '</svg>';
  canvas.innerHTML = svg;

  // Nodes
  nodes.forEach(n => {
    const el = document.createElement('div');
    el.className = `node ${bridgeIds.has(n.id) ? 'bridge-node' : ''}`;
    el.style.left = n.x + 'px';
    el.style.top = n.y + 'px';
    el.dataset.id = n.id;
    el.innerHTML = `
      <span class="tradition">${n.tradition || ''}</span>
      <span class="status ${n.status}">${n.status}</span>
      <div class="sanskrit">${escapeHtml(n.sanskrit || n.statement)}</div>
      <div class="lean">${escapeHtml(n.lean_type || '')}</div>
    `;
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      canvas.querySelectorAll('.node.selected').forEach(n => n.classList.remove('selected'));
      el.classList.add('selected');
    });
    canvas.appendChild(el);
  });

  updateZoomClass();
}

function escapeHtml(s) {
  if (!s) return '';
  const div = document.createElement('div');
  div.textContent = s;
  return div.innerHTML;
}

// Center on load (root ~4800,4800)
function center() {
  const rect = container.getBoundingClientRect();
  const cx = 4800, cy = 4800;
  scale = 0.7;
  translateX = rect.width / 2 - cx * scale;
  translateY = rect.height / 2 - cy * scale;
  applyTransform();
  updateZoomClass();
}

load().then(() => {
  center();
});
