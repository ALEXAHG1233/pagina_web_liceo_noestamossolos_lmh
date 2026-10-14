// Fondo de la portada: un "océano" 3D de malla que se mueve con olas y
// unas cajas que flotan, todo en verde (colores del liceo) con cajas
// doradas. Hecho con three.js. Se pausa cuando la pestaña no se ve, va a
// unos 30 cuadros por segundo para no gastar batería, y si la persona
// pidió menos movimiento se dibuja una sola vez, quieto.
import * as THREE from "three";
import { RectAreaLightUniformsLib } from "three/addons/lights/RectAreaLightUniformsLib.js";

const lienzo = document.querySelector("[data-oceano]");

if (lienzo) {
  RectAreaLightUniformsLib.init();

  const COLORES = {
    fondo: 0x0d2415,     // verde muy oscuro
    rejilla: 0x1f4d2c,   // verde del liceo
    acento: 0x2e9b55,    // verde del océano y las luces
    cajas: 0xc9a227,     // dorado
  };
  const AJUSTES = {
    fov: 20, giro: 0.001, cajas: 5, dispersion: 5,
    tamano: 25, fragmentos: 25, amplitud: 0.2, velocidad: 0.05, opacidad: 0.85,
  };
  const sinMovimiento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const render = new THREE.WebGLRenderer({ canvas: lienzo, antialias: false, alpha: false });
  render.setPixelRatio(1);
  const escena = new THREE.Scene();
  escena.background = new THREE.Color(COLORES.fondo);
  escena.fog = new THREE.Fog(COLORES.fondo, 5, 20);
  const camara = new THREE.PerspectiveCamera(AJUSTES.fov, 1, 0.1, 100);
  camara.position.set(0, 2, 10);

  // Luces (igual que el original, con el verde como acento).
  escena.add(new THREE.HemisphereLight(0xd3ffd9, COLORES.acento, 2));
  const punto1 = new THREE.PointLight(COLORES.acento, 1);
  punto1.position.set(-5, -20, -20);
  escena.add(punto1);
  const rectangular = new THREE.RectAreaLight(COLORES.acento, 20, 3, 3);
  rectangular.position.set(2, 2, -20);
  escena.add(rectangular);
  const punto2 = new THREE.PointLight(COLORES.acento, 0.1);
  punto2.position.set(0, 2, -2);
  escena.add(punto2);

  const grupo = new THREE.Group();
  escena.add(grupo);
  const rejilla = new THREE.GridHelper(20, 20, COLORES.rejilla, COLORES.rejilla);
  rejilla.position.y = -1;
  grupo.add(rejilla);

  // Océano: un plano con muchos vértices; cada uno se mueve en círculos.
  const geometria = new THREE.PlaneGeometry(AJUSTES.tamano, AJUSTES.tamano, AJUSTES.fragmentos, AJUSTES.fragmentos);
  const posiciones = geometria.getAttribute("position");
  const olas = [];
  for (let i = 0; i < posiciones.count; i++) {
    olas.push({
      x: posiciones.getX(i), y: posiciones.getY(i), z: posiciones.getZ(i),
      ang: Math.PI * 2,
      amp: Math.random() * AJUSTES.amplitud,
      vel: 0.03 + Math.random() * AJUSTES.velocidad,
    });
  }
  const oceano = new THREE.Group();
  oceano.rotation.x = -Math.PI / 2;
  oceano.add(new THREE.Mesh(geometria, new THREE.MeshPhysicalMaterial({
    color: COLORES.acento, transparent: true, opacity: AJUSTES.opacidad,
  })));
  oceano.add(new THREE.Mesh(geometria, new THREE.MeshPhysicalMaterial({
    color: COLORES.acento, wireframe: true,
  })));
  grupo.add(oceano);

  // Cajas que flotan y se mecen.
  const cajas = [];
  const material = new THREE.MeshStandardMaterial({ color: COLORES.cajas });
  for (let i = 0; i < AJUSTES.cajas; i++) {
    const s = AJUSTES.dispersion;
    const caja = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), material);
    const ancho = Math.random();
    caja.position.set(-Math.random() * s + Math.random() * s, 0, -Math.random() * s + Math.random() * s);
    caja.scale.set(ancho, 0.5 + Math.random() * 2, ancho);
    caja.rotation.y = Math.random() * Math.PI * 2;
    caja.userData = { vel: 1 + Math.random() * 4, amp: 1 + Math.random() * 6, pos: Math.random() * 0.2 };
    grupo.add(caja);
    cajas.push(caja);
  }

  function medir() {
    const ancho = window.innerWidth, alto = window.innerHeight;
    render.setSize(ancho, alto, false);
    camara.aspect = ancho / alto;
    camara.updateProjectionMatrix();
  }

  const reloj = new THREE.Clock();
  function cuadro() {
    for (let i = 0; i < posiciones.count; i++) {
      const o = olas[i];
      posiciones.setX(i, o.x + Math.cos(o.ang) * o.amp);
      posiciones.setY(i, o.y + Math.sin(o.ang / 2) * o.amp);
      posiciones.setZ(i, o.z + Math.cos(o.ang / 3) * o.amp);
      o.ang += o.vel;
    }
    posiciones.needsUpdate = true;
    const t = reloj.getElapsedTime() * 3;
    cajas.forEach((c) => {
      const { vel, amp, pos } = c.userData;
      c.rotation.z = (Math.sin(t / vel) * amp * Math.PI) / 180;
      c.rotation.x = (Math.cos(t) * vel * Math.PI) / 180;
      c.position.y = Math.sin(t / vel) * pos;
    });
    grupo.rotation.y += AJUSTES.giro;
    camara.lookAt(0, 0, 0);
    rectangular.lookAt(0, 0, 0);
    render.render(escena, camara);
  }

  medir();
  window.addEventListener("resize", medir);

  if (sinMovimiento) {
    cuadro();
  } else {
    let anterior = 0;
    render.setAnimationLoop((ahora) => {
      if (document.hidden || ahora - anterior < 33) return;   // ~30 cuadros por segundo
      anterior = ahora;
      cuadro();
    });
  }
}
