/**
 * Sanskrit Proof Engine — 3D proof sculptures
 * Structure from nested logic; Abhinavagupta-inspired palette.
 * Each proof tree = unique organic form.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Palette (Abhinavagupta: cosmos, amber, moonlight)
const COLORS = {
  cosmos: 0x050508,
  sanskrit: 0xd4af64,   // honey / petal-gold
  lean: 0xa8b4c0,       // silver-mist
  proved: 0x4a7c59,     // inner glow green
  hollow: 0x8b7355,     // dormant amber
  partial: 0x5a6b7a,    // cool blue-grey
  edge: 0x1a1a1e,
  bridge: 0xd4af64,
};

const STATUS_COLOR = {
  PROVED: COLORS.proved,
  HOLLOW: COLORS.hollow,
  PARTIAL: COLORS.partial,
  UNPROVED: 0x6a6a70,
  OUTSIDE_FORMAL: 0x7a6a8a,
  REFUTED: 0x8a4a4a,
  PLACEHOLDER: 0x5a5a60,
};

// Build 3D tree from proof graph
function buildProofTree(nodes, edges, scene) {
  const byId = Object.fromEntries(nodes.map(n => [n.id, { ...n, children: [] }]));
  let root = null;
  for (const n of nodes) {
    const node = byId[n.id];
    if (n.parent_id == null) root = node;
    else if (byId[n.parent_id]) byId[n.parent_id].children.push(node);
  }
  if (!root) root = nodes[0] ? byId[nodes[0].id] : null;
  if (!root) return null;

  const bridgeIds = new Set();
  (window.__bridges || []).forEach(b => { bridgeIds.add(b.node_a); bridgeIds.add(b.node_b); });

  const group = new THREE.Group();
  const materialCache = {};

  function getMaterial(status, isBridge) {
    const key = `${status}-${isBridge}`;
    if (!materialCache[key]) {
      const base = STATUS_COLOR[status] ?? COLORS.lean;
      const c = new THREE.Color(isBridge ? COLORS.bridge : base);
      materialCache[key] = new THREE.MeshStandardMaterial({
        color: c,
        emissive: c,
        emissiveIntensity: status === 'PROVED' ? 0.15 : 0.05,
        metalness: 0.3,
        roughness: 0.7,
      });
    }
    return materialCache[key];
  }

  function addBranch(parentPos, childPos, radius) {
    const dir = new THREE.Vector3().subVectors(childPos, parentPos);
    const len = dir.length();
    if (len < 0.01) return;
    const geom = new THREE.CylinderGeometry(radius * 0.5, radius, len, 8);
    const mesh = new THREE.Mesh(geom, new THREE.MeshStandardMaterial({
      color: COLORS.edge,
      roughness: 0.85,
      metalness: 0.1,
    }));
    mesh.position.copy(parentPos).add(childPos).multiplyScalar(0.5);
    mesh.lookAt(childPos);
    mesh.rotateX(Math.PI / 2);
    group.add(mesh);
  }

  function addNode(pos, status, isBridge) {
    const r = 0.12;
    const geom = new THREE.SphereGeometry(r, 12, 10);
    const mat = getMaterial(status, isBridge);
    const mesh = new THREE.Mesh(geom, mat);
    mesh.position.copy(pos);
    mesh.userData = { type: 'node' };
    group.add(mesh);
  }

  function grow(node, pos, dir, depth, parentRadius) {
    addNode(pos, node.status, bridgeIds.has(node.id));
    const n = node.children.length;
    const r = Math.max(0.04, parentRadius * 0.7);
    const branchLen = 0.8 + 0.3 / (depth + 1);
    const spread = 0.6;

    node.children.forEach((child, i) => {
      const angle = (i / Math.max(1, n - 1) - 0.5) * spread * Math.PI;
      const up = new THREE.Vector3(0, 1, 0);
      const childDir = dir.clone().applyAxisAngle(up, angle).multiplyScalar(branchLen);
      const childPos = pos.clone().add(childDir);
      addBranch(pos, childPos, r);
      grow(child, childPos, childDir.normalize(), depth + 1, r);
    });
  }

  const rootPos = new THREE.Vector3(0, 0, 0);
  const rootDir = new THREE.Vector3(0, 1, 0);
  grow(root, rootPos, rootDir, 0, 0.15);

  return group;
}

async function main() {
  const data = await fetch('data/sample.json').then(r => r.json());
  window.__bridges = data.bridges || [];

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(COLORS.cosmos);
  scene.fog = new THREE.FogExp2(COLORS.cosmos, 0.08);

  const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(2, 2, 2);

  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio));
  document.getElementById('canvas').appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.minDistance = 0.5;
  controls.maxDistance = 15;

  // Ambient + subtle key
  scene.add(new THREE.AmbientLight(0x202020, 0.6));
  const key = new THREE.DirectionalLight(0xd4af64, 0.4);
  key.position.set(2, 4, 2);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xa8b4c0, 0.2);
  fill.position.set(-2, 1, -2);
  scene.add(fill);

  const tree = buildProofTree(data.nodes || [], data.edges || [], scene);
  if (tree) scene.add(tree);

  function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });
}

main();
