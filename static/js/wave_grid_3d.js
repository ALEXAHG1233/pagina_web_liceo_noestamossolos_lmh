// Fondo 3D de cubos con olas ("Wave Grid Background") para el panel de la
// psicóloga. Una cuadrícula de 40×40 cubos que suben y bajan como olas cuando
// pasa el mouse (y solos, con olas suaves, cuando el mouse está quieto).
// Hecho con Three.js: un shader mueve los cubos según el rastro del mouse, y
// un efecto final oscurece las orillas y separa un poco los colores.
// Pasado del componente de React "WaveGridBackground" a JavaScript normal.
//
// Si el navegador no puede con 3D (WebGL), se usa el fondo de olas en 2D
// (wave_grid.js). Quien pidió menos movimiento ve los cubos quietos.
import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const AJUSTES = {
  gridSize: 40,
  colorBase: "#1f4b2c",   // verde del liceo
  colorHigh: "#0055ff",   // azul en lo alto de la ola
  waveAmplitude: 0.4,
  waveSpeed: 6.0,
  waveFrequency: 1.2,
  waveWidth: 3.0,
  waveMaxHeight: 0.4,
  waveJitter: 0.2,
  autoAnimate: true,
  vignette: true,
};

const MAX_TRAIL = 128;
const quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

const VIGNETTE_RGB_SHIFT_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    shiftAmount: { value: 0.005 },
    vignetteRadius: { value: 0.3 },
    vignetteSoftness: { value: 0.3 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float shiftAmount;
    uniform float vignetteRadius;
    uniform float vignetteSoftness;
    varying vec2 vUv;

    void main() {
      vec2 center = vec2(0.5);
      float dist = distance(vUv, center);
      float horzQuadrant = sign(vUv.x - center.x);
      float vertQuadrant = sign(vUv.y - center.y);

      float vignetteFactor = smoothstep(vignetteRadius, vignetteRadius + vignetteSoftness, dist);
      float currentShift = shiftAmount * vignetteFactor;

      float r = texture2D(tDiffuse, vUv + vec2(currentShift * horzQuadrant, currentShift * vertQuadrant)).r;
      float g = texture2D(tDiffuse, vUv).g;
      float b = texture2D(tDiffuse, vUv - vec2(currentShift * horzQuadrant, currentShift * vertQuadrant)).b;

      float darken = 1.0 - vignetteFactor * 0.5;
      gl_FragColor = vec4(vec3(r, g, b) * darken, 1.0);
    }
  `,
};

// Mete el movimiento de las olas en el shader de los cubos. Se usa en el
// material visible y en el de sombras, para que las sombras sigan a los cubos.
function overrideVertexShader(vertexShader) {
  return vertexShader
    .replace(
      "#include <common>",
      /* glsl */ `#include <common>
      varying float vHeight;
      attribute vec2 aOffset;
      uniform sampler2D uTrailTexture;
      uniform int       uTrailCount;
      uniform float     uWaveSpeed;
      uniform float     uWaveFreq;
      uniform float     uWaveWidth;
      uniform float     uFadeTime;
      uniform float     uAmplitude;
      uniform float     uJitter;
      uniform float     uMaxHeight;

      vec2 hash2( vec2 p ) {
        p = vec2( dot( p, vec2( 127.1, 311.7 ) ), dot( p, vec2( 269.5, 183.3 ) ) );
        return fract( sin( p ) * 43758.5453123 ) - 0.5;
      }`,
    )
    .replace(
      "#include <begin_vertex>",
      /* glsl */ `#include <begin_vertex>

      vHeight = 0.0;

      if ( position.y > 0.0 ) {
        vec2 jitter  = hash2( aOffset ) * uJitter;
        vec2 worldXZ = aOffset + jitter;
        float waveHeight  = 0.0;
        float totalWeight = 0.0;

        for ( int i = 0; i < 128; i++ ) {
          if ( i >= uTrailCount ) break;
          vec4 td = texture2D( uTrailTexture, vec2( ( float(i) + 0.5 ) / 128.0, 0.5 ) );
          float dist      = length( worldXZ - td.rg );
          float wavefront = uWaveSpeed * td.b;
          float relDist   = dist - wavefront;

          float window = exp( -( relDist * relDist ) / ( uWaveWidth * uWaveWidth ) );
          float fade   = exp( -td.b / uFadeTime );
          float atten  = 1.0 / ( 1.0 + dist * 0.1 );
          float weight = fade * window * atten * td.a;

          waveHeight  += weight * cos( uWaveFreq * relDist );
          totalWeight += weight;
        }

        waveHeight /= max( totalWeight, 1.0 );

        float displacement = clamp( waveHeight * uAmplitude, -uMaxHeight, uMaxHeight );
        transformed.y += displacement;
        vHeight = displacement;
      }`,
    );
}

function crearFondo() {
  const p = AJUSTES;
  const canvas = document.createElement("canvas");
  canvas.className = "fondo-ondas fondo-cubos";
  canvas.setAttribute("aria-hidden", "true");
  document.body.prepend(canvas);

  const cubeWidth = 0.8;
  const cubeHeight = 3;
  const gap = 0.01;
  const bounds = p.gridSize * (cubeWidth + gap);

  const getSize = () => ({
    width: window.innerWidth || 1,
    height: window.innerHeight || 1,
    pixelRatio: Math.min(window.devicePixelRatio, 2),
  });
  let size = getSize();

  // Escena
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(p.colorBase).multiplyScalar(0.5);

  // Cámara que gira un poquito con el mouse
  const alphaRange = Math.PI * 0.03;
  const betaRange = Math.PI * 0.05;
  const mouse = new THREE.Vector2(0, 0);
  const lerpedMouse = new THREE.Vector2(0, 0);

  const camera = new THREE.PerspectiveCamera(40, size.width / size.height, 0.1, 500);
  let cameraRadius = 12;
  const fitCamera = () => {
    const verticalHalfFov = THREE.MathUtils.degToRad(camera.fov) / 2;
    const horizontalHalfFov = Math.atan(Math.tan(verticalHalfFov) * camera.aspect);
    const halfBounds = bounds / 2;
    // Es un fondo: los cubos cubren toda la pantalla, sin franjas vacías a los lados
    cameraRadius = Math.min(
      halfBounds / Math.tan(verticalHalfFov),
      halfBounds / Math.tan(horizontalHalfFov),
    ) * 0.9 + cubeHeight * 0.5;
  };
  const positionCamera = (mx, my) => {
    const alpha = my * alphaRange;
    const beta = mx * betaRange;
    camera.position.set(
      -cameraRadius * Math.cos(alpha) * Math.sin(beta),
      cameraRadius * Math.cos(alpha) * Math.cos(beta),
      cameraRadius * Math.sin(alpha),
    );
    camera.up.set(0, 0, -1);
    camera.lookAt(0, 0, 0);
  };
  fitCamera();
  positionCamera(0, 0);
  scene.add(camera);

  // Luces
  scene.add(new THREE.AmbientLight("#ffffff", 0.5));
  const keyLight = new THREE.DirectionalLight("#ffffff", 4.0);
  keyLight.position.set(-20, 10, 6);
  keyLight.castShadow = true;
  keyLight.shadow.mapSize.set(1024, 1024);
  keyLight.shadow.radius = 6;
  keyLight.shadow.camera.near = 0.1;
  keyLight.shadow.camera.far = 60;
  keyLight.shadow.camera.left = -22;
  keyLight.shadow.camera.right = 22;
  keyLight.shadow.camera.top = 22;
  keyLight.shadow.camera.bottom = -22;
  keyLight.shadow.bias = 0.0001;
  scene.add(keyLight);
  const fillLight = new THREE.DirectionalLight("#ffffff", 1.0);
  fillLight.position.set(10, 5, -3);
  scene.add(fillLight);

  // Rastro del mouse (de donde salen las olas)
  const trailData = new Float32Array(MAX_TRAIL * 4);
  const trailTexture = new THREE.DataTexture(trailData, MAX_TRAIL, 1, THREE.RGBAFormat, THREE.FloatType);
  trailTexture.needsUpdate = true;

  const trailUniforms = {
    uTrailTexture: { value: trailTexture },
    uTrailCount: { value: 0 },
    uFadeTime: { value: 2.0 },
    uWaveSpeed: { value: p.waveSpeed },
    uWaveFreq: { value: p.waveFrequency },
    uWaveWidth: { value: p.waveWidth },
    uAmplitude: { value: p.waveAmplitude },
    uJitter: { value: p.waveJitter },
    uMaxHeight: { value: p.waveMaxHeight },
  };
  const colorUniforms = {
    uColorBase: { value: new THREE.Color(p.colorBase) },
    uColorHigh: { value: new THREE.Color(p.colorHigh) },
  };

  const trail = [];
  let lastPoint = null;
  let timeSinceLastMove = 0;
  let randomPointTimer = 0;
  let placingRandom = true;
  const fadeTime = 2.0;
  const trailSpacing = 0.1;

  const rayPlane = new THREE.Mesh(
    new THREE.PlaneGeometry(bounds, bounds),
    new THREE.MeshBasicMaterial({ side: THREE.DoubleSide, visible: false }),
  );
  rayPlane.rotation.x = -Math.PI / 2;
  rayPlane.updateMatrixWorld(true);

  const raycaster = new THREE.Raycaster();
  const pointerNDC = new THREE.Vector2();
  // El fondo no recibe clics (va detrás del panel): se escucha el mouse en toda la ventana
  window.addEventListener("pointermove", (e) => {
    pointerNDC.set((e.clientX / size.width) * 2 - 1, -(e.clientY / size.height) * 2 + 1);
    mouse.copy(pointerNDC);
    raycaster.setFromCamera(pointerNDC, camera);
    const hits = raycaster.intersectObject(rayPlane);
    if (hits.length === 0) return;
    const { x, z } = hits[0].point;
    let distDelta = 0;
    if (lastPoint) {
      const dx = x - lastPoint.x;
      const dz = z - lastPoint.z;
      distDelta = Math.sqrt(dx * dx + dz * dz);
      if (distDelta < trailSpacing) return;
    }
    if (trail.length >= MAX_TRAIL) trail.shift();
    trail.push({ x, z, age: 0, distDelta });
    lastPoint = { x, z };
    timeSinceLastMove = 0;
    placingRandom = false;
    randomPointTimer = 0;
  }, { passive: true });
  document.addEventListener("pointerleave", () => { mouse.set(0, 0); lastPoint = null; });

  const addRandomPoint = () => {
    const x = (Math.random() * 0.5 - 0.25) * bounds;
    const z = (Math.random() * 0.5 - 0.25) * bounds;
    if (trail.length >= MAX_TRAIL) trail.shift();
    trail.push({ x, z, age: 0, distDelta: 0.8 + Math.random() * 0.2 });
  };

  const updateTrail = (delta) => {
    const expiry = fadeTime * 4;
    for (let i = trail.length - 1; i >= 0; i--) {
      trail[i].age += delta;
      if (trail[i].age > expiry) trail.splice(i, 1);
    }
    timeSinceLastMove += delta;
    if (timeSinceLastMove >= 3.0 && !placingRandom && p.autoAnimate) {
      placingRandom = true;
      randomPointTimer = 0;
    }
    if (placingRandom && p.autoAnimate) {
      randomPointTimer += delta;
      if (randomPointTimer >= 1.5) {
        addRandomPoint();
        randomPointTimer = 0;
      }
    }
    const count = Math.min(trail.length, MAX_TRAIL);
    if (count > 0 || trailUniforms.uTrailCount.value > 0) {
      for (let i = 0; i < count; i++) {
        const ti = i * 4;
        trailData[ti] = trail[i].x;
        trailData[ti + 1] = trail[i].z;
        trailData[ti + 2] = trail[i].age;
        trailData[ti + 3] = trail[i].distDelta;
      }
      trailTexture.needsUpdate = true;
      trailUniforms.uTrailCount.value = count;
    }
  };

  // Cuadrícula de cubos (todos de una vez, con el shader de olas)
  const count = p.gridSize * p.gridSize;
  const geometry = new THREE.BoxGeometry(cubeWidth, cubeHeight, cubeWidth);
  const offsetAttribute = new THREE.InstancedBufferAttribute(new Float32Array(count * 2), 2);
  geometry.setAttribute("aOffset", offsetAttribute);

  const material = new THREE.MeshPhongMaterial({ color: 0xffffff });
  material.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, trailUniforms, colorUniforms);
    shader.vertexShader = overrideVertexShader(shader.vertexShader);
    shader.fragmentShader = shader.fragmentShader
      .replace(
        "#include <common>",
        `#include <common>
        varying float vHeight;
        uniform vec3  uColorBase;
        uniform vec3  uColorHigh;
        uniform float uMaxHeight;`,
      )
      .replace(
        "#include <color_fragment>",
        `#include <color_fragment>
        float t = clamp( vHeight / uMaxHeight, 0.0, 1.0 );
        diffuseColor.rgb = mix( uColorBase, uColorHigh, t );`,
      );
  };
  const depthMaterial = new THREE.MeshDepthMaterial();
  depthMaterial.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, trailUniforms);
    shader.vertexShader = overrideVertexShader(shader.vertexShader);
  };

  const instancedMesh = new THREE.InstancedMesh(geometry, material, count);
  instancedMesh.customDepthMaterial = depthMaterial;
  instancedMesh.castShadow = true;
  instancedMesh.receiveShadow = true;
  scene.add(instancedMesh);

  const dummy = new THREE.Object3D();
  const spacing = cubeWidth + gap;
  const offset = ((p.gridSize - 1) * spacing) / 2;
  for (let i = 0; i < p.gridSize; i++) {
    for (let j = 0; j < p.gridSize; j++) {
      const index = i * p.gridSize + j;
      const x = i * spacing - offset;
      const z = j * spacing - offset;
      dummy.position.set(x, 0, z);
      dummy.updateMatrix();
      instancedMesh.setMatrixAt(index, dummy.matrix);
      offsetAttribute.setXY(index, x, z);
    }
  }
  instancedMesh.instanceMatrix.needsUpdate = true;
  offsetAttribute.needsUpdate = true;

  // Dibujo y efecto final
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.95;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.setClearColor("#808080");
  renderer.setSize(size.width, size.height, false);
  renderer.setPixelRatio(size.pixelRatio);

  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  if (p.vignette) composer.addPass(new ShaderPass(VIGNETTE_RGB_SHIFT_SHADER));
  composer.addPass(new OutputPass());
  composer.setSize(size.width, size.height);
  composer.setPixelRatio(size.pixelRatio);

  window.addEventListener("resize", () => {
    size = getSize();
    camera.aspect = size.width / size.height;
    camera.updateProjectionMatrix();
    fitCamera();
    positionCamera(lerpedMouse.x, lerpedMouse.y);
    renderer.setSize(size.width, size.height, false);
    renderer.setPixelRatio(size.pixelRatio);
    composer.setSize(size.width, size.height);
    composer.setPixelRatio(size.pixelRatio);
    if (quieto) composer.render();
  });

  const clock = new THREE.Clock();
  const cuadro = () => {
    const delta = Math.min(clock.getDelta(), 0.1);
    updateTrail(delta);
    lerpedMouse.x += (mouse.x - lerpedMouse.x) * 0.04;
    lerpedMouse.y += (mouse.y - lerpedMouse.y) * 0.04;
    positionCamera(lerpedMouse.x, lerpedMouse.y);
    composer.render();
  };

  if (quieto) {
    composer.render();
    return;
  }
  renderer.setAnimationLoop(cuadro);
  // Se pausa cuando la pestaña no se está viendo
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) renderer.setAnimationLoop(null);
    else { clock.getDelta(); renderer.setAnimationLoop(cuadro); }
  });
}

function hayWebGL() {
  try {
    const c = document.createElement("canvas");
    return !!(c.getContext("webgl2") || c.getContext("webgl"));
  } catch (e) {
    return false;
  }
}

function usarFondo2D() {
  const s = document.createElement("script");
  s.src = "/static/js/wave_grid.js";
  document.body.appendChild(s);
}

try {
  if (hayWebGL()) crearFondo();
  else usarFondo2D();
} catch (e) {
  document.querySelector(".fondo-cubos")?.remove();
  usarFondo2D();
}
