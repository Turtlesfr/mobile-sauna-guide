import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const mount = document.getElementById('viewer3d');
const fallback = document.getElementById('viewer-fallback');
if (!mount) { /* nothing to do */ }

function fail(){ if (fallback) fallback.hidden = false; if (mount) mount.style.display = 'none'; }

try {
  // ---- procedural plank texture ----
  function plankTexture(base, grain, seam, vertical){
    const c = document.createElement('canvas'); c.width = 256; c.height = 256;
    const x = c.getContext('2d');
    x.fillStyle = base; x.fillRect(0,0,256,256);
    // grain noise
    for (let i=0;i<2600;i++){
      x.globalAlpha = Math.random()*0.06;
      x.fillStyle = Math.random()>0.5 ? grain : '#ffffff';
      const w = Math.random()*40+6;
      if (vertical) x.fillRect(Math.random()*256, Math.random()*256, 2, w);
      else x.fillRect(Math.random()*256, Math.random()*256, w, 2);
    }
    x.globalAlpha = 1;
    // plank seams
    x.strokeStyle = seam; x.lineWidth = 2;
    for (let p=0;p<=256;p+=32){
      x.beginPath();
      if (vertical){ x.moveTo(p,0); x.lineTo(p,256); } else { x.moveTo(0,p); x.lineTo(256,p); }
      x.stroke();
    }
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  }

  const extTex = plankTexture('#b07f4e','#6e4a28','#7a5532', true);
  extTex.repeat.set(2,2);
  const intTex = plankTexture('#d9c19a','#b89a6e','#c2a878', true);
  intTex.repeat.set(2,1);
  const roofTex = plankTexture('#3b3f44','#23262a','#2b2e33', false);

  const M = {
    ext:  new THREE.MeshStandardMaterial({ map:extTex, roughness:0.85 }),
    int:  new THREE.MeshStandardMaterial({ map:intTex, roughness:0.8 }),
    roof: new THREE.MeshStandardMaterial({ map:roofTex, roughness:0.6, metalness:0.3 }),
    metal:new THREE.MeshStandardMaterial({ color:0x2a2c30, roughness:0.5, metalness:0.7 }),
    tyre: new THREE.MeshStandardMaterial({ color:0x14151a, roughness:0.9 }),
    glass:new THREE.MeshStandardMaterial({ color:0x9fd0e6, roughness:0.1, metalness:0, transparent:true, opacity:0.32 }),
    stove:new THREE.MeshStandardMaterial({ color:0x17181b, roughness:0.6, metalness:0.4 }),
    stone:new THREE.MeshStandardMaterial({ color:0x55585e, roughness:0.95 }),
    door: new THREE.MeshStandardMaterial({ map:intTex, roughness:0.7 }),
  };

  // ---- scene ----
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  camera.position.set(4.4, 3.0, 4.8);

  const renderer = new THREE.WebGLRenderer({ antialias:true, alpha:true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio||1));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  mount.appendChild(renderer.domElement);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.minDistance = 2.2;
  controls.maxDistance = 12;
  controls.maxPolarAngle = Math.PI*0.49;
  controls.target.set(0, 1.35, 0);

  // ---- lights ----
  const hemi = new THREE.HemisphereLight(0xbfd6ff, 0x4a3a2c, 0.65);
  scene.add(hemi);
  const sun = new THREE.DirectionalLight(0xfff1d8, 1.25);
  sun.position.set(5, 8, 4); sun.castShadow = true;
  sun.shadow.mapSize.set(1024,1024);
  sun.shadow.camera.near = 1; sun.shadow.camera.far = 30;
  sun.shadow.camera.left=-6; sun.shadow.camera.right=6; sun.shadow.camera.top=6; sun.shadow.camera.bottom=-6;
  sun.shadow.bias = -0.0004;
  scene.add(sun);
  const ember = new THREE.PointLight(0xff7a1e, 0, 5, 2);
  ember.position.set(0.45, 1.15, -1.0);
  scene.add(ember);

  // ---- ground ----
  const ground = new THREE.Mesh(new THREE.CircleGeometry(16, 48),
    new THREE.MeshStandardMaterial({ color:0x2d2a25, roughness:1 }));
  ground.rotation.x = -Math.PI/2; ground.receiveShadow = true;
  scene.add(ground);

  // ---- helpers ----
  const sauna = new THREE.Group(); scene.add(sauna);
  function box(w,h,d,mat,x,y,z,opts){
    const m = new THREE.Mesh(new THREE.BoxGeometry(w,h,d), mat);
    m.position.set(x,y,z);
    m.castShadow = !(opts&&opts.noCast); m.receiveShadow = true;
    sauna.add(m); return m;
  }

  // dims (m)
  const W=1.7, L=3.0, H=2.0, deck=0.55, t=0.09;
  const x0=W/2, z0=L/2, yMid=deck+H/2; // 0.85, 1.5, 1.55

  // trailer
  box(W+0.16, 0.12, L+0.18, M.metal, 0, deck-0.06, 0);                 // deck
  const draw = box(0.12,0.10,0.9, M.metal, 0, deck-0.06, z0+0.5);      // drawbar
  box(0.18,0.10,0.18, M.metal, 0, deck-0.06, z0+0.95);                 // hitch
  for (const sx of [-1,1]){
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.30,0.30,0.18,22), M.tyre);
    wheel.rotation.z = Math.PI/2; wheel.position.set(sx*(x0+0.12), 0.30, 0);
    wheel.castShadow = true; sauna.add(wheel);
    box(0.5,0.06,0.7, M.metal, sx*(x0+0.05), deck+0.0, 0, {noCast:true}); // fender
  }

  // walls (named for cutaway)
  const walls = {};
  walls.back  = box(W, H, t, M.ext, 0, yMid, -z0);
  walls.left  = box(t, H, L, M.ext, -x0, yMid, 0);
  walls.right = box(t, H, L, M.ext,  x0, yMid, 0);
  walls.floor = box(W, t, L, M.int, 0, deck, 0);
  // front wall split around a door + window
  walls.frontL = box((W-0.8)/2, H, t, M.ext, -(0.8/2+ (W-0.8)/4), yMid,  z0);
  walls.frontR = box((W-0.8)/2, H, t, M.ext,  (0.8/2+ (W-0.8)/4), yMid,  z0);
  walls.frontTop = box(0.8, H-1.95, t, M.ext, 0, deck+1.95+ (H-1.95)/2, z0);
  walls.door  = box(0.74, 1.9, 0.05, M.door, 0, deck+0.95, z0+0.02);
  walls.glass = box(0.5, 1.0, 0.02, M.glass, 0, deck+1.2, z0+0.06);

  // shed roof (slanted) + chimney
  const roof = new THREE.Mesh(new THREE.BoxGeometry(W+0.5, 0.10, L+0.5), M.roof);
  roof.position.set(0, deck+H+0.16, -0.04); roof.rotation.x = THREE.MathUtils.degToRad(7);
  roof.castShadow = true; sauna.add(roof); walls.roof = roof;
  const chimney = new THREE.Mesh(new THREE.CylinderGeometry(0.075,0.075,0.9,16), M.metal);
  chimney.position.set(0.45, deck+H+0.5, -1.0); chimney.castShadow = true; sauna.add(chimney); walls.chimney = chimney;

  // interior: benches + stove + stones (always in scene, revealed in cutaway)
  box(0.55, t, L-0.3, M.int, -x0+0.32, deck+0.45, 0);   // lower bench (left)
  box(0.62, t, W-0.2, M.int, 0, deck+0.95, -z0+0.4);    // upper bench (back)  oriented along x
  const stove = box(0.42,0.62,0.42, M.stove, 0.45, deck+0.31, -1.0);
  // stones on stove
  const stoneGeo = new THREE.IcosahedronGeometry(0.06, 0);
  for (let i=0;i<14;i++){
    const s = new THREE.Mesh(stoneGeo, M.stone);
    s.position.set(0.45 + (Math.random()-0.5)*0.32, deck+0.64 + Math.random()*0.05, -1.0 + (Math.random()-0.5)*0.32);
    s.scale.setScalar(0.7+Math.random()*0.6); s.castShadow = true; sauna.add(s);
  }
  const flue = new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.06,1.4,14), M.metal);
  flue.position.set(0.45, deck+1.0, -1.0); sauna.add(flue);

  // ---- view modes ----
  const VIEWS = {
    exterior: { pos:new THREE.Vector3(4.4,3.0,4.8), tgt:new THREE.Vector3(0,1.35,0), ember:0, sun:1.25,
      show:['back','left','right','floor','frontL','frontR','frontTop','door','glass','roof','chimney'] },
    interior: { pos:new THREE.Vector3(3.3,2.7,3.5), tgt:new THREE.Vector3(0.05,0.95,-0.45), ember:3.2, sun:0.7,
      show:['back','left','floor','chimney'] },
  };
  const goal = { pos:VIEWS.exterior.pos.clone(), tgt:VIEWS.exterior.tgt.clone(), ember:0, sun:1.25 };
  let transitioning = false;

  function setView(name){
    const v = VIEWS[name]; if (!v) return;
    for (const k in walls) walls[k].visible = v.show.includes(k);
    goal.pos.copy(v.pos); goal.tgt.copy(v.tgt); goal.ember = v.ember; goal.sun = v.sun;
    transitioning = true;
    document.querySelectorAll('.vbtn[data-view]').forEach(b =>
      b.classList.toggle('active', b.dataset.view === name));
  }
  setView('exterior');

  // ---- UI ----
  document.querySelectorAll('.vbtn[data-view]').forEach(b =>
    b.addEventListener('click', () => setView(b.dataset.view)));
  const rotBtn = document.getElementById('vrotate');
  if (rotBtn) rotBtn.addEventListener('click', () => {
    controls.autoRotate = !controls.autoRotate;
    rotBtn.classList.toggle('active', controls.autoRotate);
  });
  controls.autoRotateSpeed = 1.1;

  // ---- resize ----
  function resize(){
    const w = mount.clientWidth, h = mount.clientHeight || 380;
    renderer.setSize(w, h, false);
    camera.aspect = w/Math.max(1,h); camera.updateProjectionMatrix();
  }
  new ResizeObserver(resize).observe(mount); resize();

  // ---- render loop (pause when offscreen) ----
  let visible = true;
  new IntersectionObserver(es => { visible = es[0].isIntersecting; })
    .observe(mount);

  function tick(){
    requestAnimationFrame(tick);
    if (!visible) return;
    if (transitioning){
      camera.position.lerp(goal.pos, 0.07);
      controls.target.lerp(goal.tgt, 0.07);
      if (camera.position.distanceTo(goal.pos) < 0.03) transitioning = false;
    }
    ember.intensity += (goal.ember - ember.intensity)*0.08;
    sun.intensity   += (goal.sun   - sun.intensity)*0.08;
    controls.update();
    renderer.render(scene, camera);
  }
  tick();
} catch (e){
  console.error('3D viewer failed:', e);
  fail();
}
