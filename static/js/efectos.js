// Efectos visuales del perfil gamer (estilo A + C): reveal al pulsar, texto letra a letra, confeti y
// sonidos sincronizados con las animaciones CSS. Usa SFX de sonido.js (cargado antes). No llama a ninguna web.

// ¿Ha pedido el sistema "reducir movimiento"? Entonces nada de confeti ni texto letra a letra
const calma = matchMedia("(prefers-reduced-motion: reduce)").matches;
const espera = ms => new Promise(r => setTimeout(r, ms));  // pausa para usar con "await"

// ===================== Confeti (dibujado en un <canvas>) =====================
const lienzo = document.getElementById("confeti");  // lienzo transparente que cubre la pantalla
const pincel = lienzo.getContext("2d");  // "pincel" 2D para dibujar en el lienzo
let particulas = [];  // papelitos en el aire
let confetiAnimando = false;  // ¿está ya en marcha el bucle de dibujo?

function confeti(x, y, n = 80) {  // lanza n papelitos desde el punto (x, y) de la pantalla
    if (calma) return;
    lienzo.width = innerWidth;  // el lienzo mide lo mismo que la ventana
    lienzo.height = innerHeight;
    const colores = ["#00f0ff", "#ff2bd6", "#39ff14", "#ffe600", "#ff8c00", "#b388ff"];  // los de los dueños
    for (let i = 0; i < n; i++) {
        const ang = Math.random() * Math.PI * 2, vel = 3 + Math.random() * 7;  // dirección y fuerza al azar
        particulas.push({
            x, y,  // posición
            vx: Math.cos(ang) * vel, vy: Math.sin(ang) * vel - 5,  // velocidad (el -5 los lanza hacia arriba)
            t: 4 + Math.random() * 6,  // tamaño
            r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4,  // giro y velocidad de giro
            c: colores[i % colores.length],  // color (% = resto: va rotando la lista)
        });
    }
    if (!confetiAnimando) {
        confetiAnimando = true;
        requestAnimationFrame(pasoConfeti);  // pide al navegador dibujar en el próximo fotograma
    }
}

function pasoConfeti() {  // un fotograma: mueve y dibuja todos los papelitos
    pincel.clearRect(0, 0, lienzo.width, lienzo.height);  // borra el fotograma anterior
    particulas = particulas.filter(p => p.y < lienzo.height + 20);  // olvida los que ya cayeron
    for (const p of particulas) {
        p.vy += 0.25;  // gravedad
        p.vx *= 0.99;  // rozamiento con el aire
        p.x += p.vx;
        p.y += p.vy;
        p.r += p.vr;
        pincel.save();  // guarda la posición del pincel...
        pincel.translate(p.x, p.y);  // ...lo lleva al papelito...
        pincel.rotate(p.r);  // ...lo gira...
        pincel.fillStyle = p.c;
        pincel.fillRect(-p.t / 2, -p.t / 2, p.t, p.t);  // ...dibuja un cuadrado...
        pincel.restore();  // ...y vuelve a como estaba
    }
    if (particulas.length) requestAnimationFrame(pasoConfeti);  // quedan papelitos: siguiente fotograma
    else confetiAnimando = false;  // ya no queda ninguno: paramos
}

// ===================== Texto letra a letra ("máquina de escribir") =====================
const frases = document.querySelectorAll(".logro-frase");  // la frase de cada perfil
if (!calma) {
    frases.forEach(p => {
        p.dataset.texto = p.textContent.trim();  // guarda la frase completa en data-texto
        p.textContent = "";  // y la vacía: se escribirá cuando el logro termine de entrar
    });
}

async function escribir(el) {  // "async": puede hacer pausas (await) sin bloquear la página
    // "vuelta" numera cada escritura; si empieza otra (repetición), la anterior se retira
    const vuelta = String(Number(el.dataset.vuelta || 0) + 1);
    el.dataset.vuelta = vuelta;
    el.textContent = "";
    const texto = el.dataset.texto;
    for (let i = 0; i < texto.length; i++) {
        if (el.dataset.vuelta !== vuelta) return;  // otra vuelta en marcha: esta se cancela
        el.append(texto[i]);  // añade una letra como texto (nunca como HTML)
        if (i % 2 === 0 && texto[i] !== " ") SFX.voz();  // "voz": un blip cada dos letras
        await espera(35);
    }
}

// ===================== Sonidos y efectos sincronizados con el CSS =====================
// animationstart / animationend: el navegador avisa al empezar o acabar cada animación CSS.
// Los eventos "suben" (burbujean) hasta document, así que basta un solo oyente para toda la página.
document.addEventListener("animationstart", e => {
    if (e.animationName === "bloque-llena") {  // se enciende un bloque de una barra de vida
        const n = [...e.target.parentNode.children].indexOf(e.target);  // su posición (0-9)
        SFX.blip(n);  // cada bloque suena más agudo que el anterior
    }
});

document.addEventListener("animationend", e => {
    if (e.animationName === "sello-cae") SFX.golpe();  // el sello INDIE toca el cuadro
    if (e.animationName === "logro-entra") {  // el logro ha terminado de entrar
        SFX.fanfarria();
        const r = e.target.getBoundingClientRect();  // posición del logro en la pantalla
        if (r.top < innerHeight) confeti(r.left + r.width / 2, r.top + 20);  // solo si se ve
        const frase = e.target.querySelector(".logro-frase");
        if (frase && frase.dataset.texto) escribir(frase);  // empieza la máquina de escribir
    }
});

// ===================== Reveal manual del perfil =====================
// Cada botón "DESCUBRIR PERFIL GAMER" muestra el bloque oculto que tiene justo detrás.
// Al hacerse visible, sus animaciones CSS arrancan y, con ellas, los sonidos y el confeti de arriba.
document.querySelectorAll(".btn-revelar").forEach(boton => {
    boton.addEventListener("click", () => {
        boton.nextElementSibling.hidden = false;  // nextElementSibling = el elemento siguiente (.perfil-oculto)
        boton.hidden = true;  // el botón ya no hace falta
        setTimeout(() => referencia("stand"), 1400);  // JoJo: has visto un Stand (cuando ya ha crecido)
    });
});

// ===================== Efectos bizarros (paso 3.6d) =====================
// Texto que sube y se desvanece en el punto (x, y) de la pantalla, p. ej. "+1 PATO"
function flotante(texto, x, y, clase = "") {  // clase: estilo extra opcional (p. ej. "ora")
    const el = document.createElement("div");
    el.className = `flotante fijo ${clase}`;  // "fijo": no tiembla con el terremoto
    el.textContent = texto;
    el.style.left = x + "px";
    el.style.top = y + "px";
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1200);  // se borra cuando acaba su animación
}

// Reinicia una animación CSS aunque ya se hubiera hecho (quitar clase, forzar recálculo, poner clase)
function reanimar(el, clase) {
    el.classList.remove(clase);
    void el.offsetWidth;  // truco: obliga al navegador a "darse cuenta" de que la clase ya no está
    el.classList.add(clase);
}

// --- Terremoto: al revelar el perfil de alguien con más de 1.000 h (data-terremoto en la tarjeta) ---
function terremoto() {
    if (calma) return;
    SFX.terremoto();
    // Tiembla todo lo que cuelga de <body> menos lo fijo (botones de la esquina, confeti, avisos, pato)
    document.querySelectorAll("body > :not(.fijo)").forEach(el => reanimar(el, "temblor"));
}
document.querySelectorAll(".stats[data-terremoto] .btn-revelar").forEach(boton => {
    boton.addEventListener("click", () => setTimeout(terremoto, 800));  // justo después de entrar el logro
});

// --- Pile of Shame vergonzoso: las letras del % se caen con trombón y vuelven a los 3 s ---
document.querySelectorAll(".verguenza").forEach(boton => {
    const original = boton.textContent;  // guardamos el texto para devolverlo luego
    boton.addEventListener("click", async () => {
        if (calma || boton.dataset.cayendo) return;  // ya se está cayendo: ignoramos el clic
        boton.dataset.cayendo = "1";
        SFX.trombon();
        boton.textContent = "";
        for (const letra of original) {  // una <span> por letra para que cada una caiga por su cuenta
            const s = document.createElement("span");
            s.textContent = letra === " " ? "\u00a0" : letra;  // \u00a0 = espacio que no desaparece
            boton.appendChild(s);
        }
        await espera(900);  // un momento de vergüenza antes de caer
        for (const s of boton.children) {
            s.style.setProperty("--giro", (Math.random() * 120 - 60) + "deg");  // giro al azar entre -60 y 60
            s.style.animationDelay = Math.random() * 1.2 + "s";  // cada letra cae cuando quiere
            s.classList.add("cae");
        }
        await espera(3000);
        boton.textContent = original;  // vuelven las letras
        delete boton.dataset.cayendo;
    });
});

// --- Pato errante: cruza la pantalla a intervalos aleatorios; 5 toques = logro ---
let toquesPato = 0;  // toques a patos en esta visita
function soltarPato() {
    const pato = document.createElement("div");
    pato.className = "pato fijo";
    const cuerpo = document.createElement("span");
    cuerpo.textContent = "🦆";
    pato.appendChild(cuerpo);
    pato.addEventListener("click", e => {
        toquesPato++;
        SFX.cuac();
        flotante(`+1 PATO (${toquesPato})`, e.clientX, e.clientY - 30);  // clientX/Y: dónde se hizo clic
        reanimar(pato, "salta");
        if (toquesPato === 5) desbloquear("patos");
    });
    document.body.appendChild(pato);
    setTimeout(() => pato.remove(), 10500);  // tras cruzar (10 s), fuera
    // El siguiente, dentro de 60-120 s
    setTimeout(soltarPato, (60 + Math.random() * 60) * 1000);
}
if (!calma) setTimeout(soltarPato, (20 + Math.random() * 40) * 1000);  // el primero, entre 20 y 60 s

// --- Título glitch: al pasar el ratón (con sonido) y de vez en cuando (mudo) ---
const titulo = document.querySelector("h1.glitch");
function glitch(ms, conSonido) {
    titulo.classList.add("activo");
    if (conSonido) SFX.glitch();
    setTimeout(() => titulo.classList.remove("activo"), ms);
}
titulo.addEventListener("mouseenter", () => glitch(500, true));
if (!calma) setInterval(() => { if (Math.random() < 0.35) glitch(250, false); }, 6000);  // 35 % cada 6 s

// ===================== Efectos bizarros (paso 3.6e) =====================
// --- Modo caos: SOLO manual (botón "NO PULSAR" o código Konami). 7 s de colores, bamboleo y trance ---
let enCaos = false;  // evita que se active dos veces a la vez
function caos() {
    if (calma || enCaos) return;
    enCaos = true;
    SFX.glitch();
    SFX.trance(4);  // 4 compases a 136 BPM = unos 7 s
    const victimas = document.querySelectorAll("body > :not(.fijo)");  // todo menos lo fijo
    victimas.forEach(el => el.classList.add("caos"));
    setTimeout(() => {
        victimas.forEach(el => el.classList.remove("caos"));
        enCaos = false;
    }, 7000);  // lo que dura la música
}
document.getElementById("btn-caos").addEventListener("click", caos);

// Código Konami: ↑ ↑ ↓ ↓ ← → ← → B A (e.key da el nombre de la tecla pulsada)
const KONAMI = ["arrowup", "arrowup", "arrowdown", "arrowdown", "arrowleft", "arrowright", "arrowleft", "arrowright", "b", "a"];
let progresoKonami = 0;  // cuántas teclas seguidas acertadas
addEventListener("keydown", e => {
    // Si acierta la siguiente tecla, avanza; si falla, vuelve a 0
    progresoKonami = e.key.toLowerCase() === KONAMI[progresoKonami] ? progresoKonami + 1 : 0;
    if (progresoKonami === KONAMI.length) {
        progresoKonami = 0;
        caos();
        desbloquear("konami");
    }
});

// --- Pantallazo azul: al pulsar las horas de tu juego más jugado (si pasa de 500 h) ---
const pistaBsod = document.querySelector(".bsod-pista");  // null si no hay
if (pistaBsod) pistaBsod.addEventListener("click", async () => {
    SFX.error();
    const pantalla = document.createElement("div");
    pantalla.className = "bsod fijo";
    pantalla.tabIndex = -1;  // permite darle el foco (para cerrarlo con Escape)
    // Líneas del pantallazo: [clase, texto]; todo con textContent (el nombre del juego viene de Steam)
    const lineas = [
        ["cara", ":("],
        ["", `Tu PC ha detectado demasiadas horas en ${pistaBsod.dataset.juego} y necesita reiniciarse.`],
        ["pct", "Recopilando información de la vergüenza: 0 %"],
        ["fin", ""],
        // toString(16): las horas en hexadecimal (base 16), como los códigos de error de verdad
        ["codigo", `Código de detención: TOCA_CESPED_0x${Number(pistaBsod.dataset.horas).toString(16).toUpperCase()}`],
    ];
    for (const [clase, texto] of lineas) {  // [clase, texto] "desempaqueta" cada par
        const p = document.createElement("p");
        if (clase) p.className = clase;
        p.textContent = texto;
        pantalla.appendChild(p);
    }
    document.body.appendChild(pantalla);
    pantalla.focus();
    for (let pct = 0; pct <= 100; pct += 4) {  // el % sube hasta 100
        pantalla.querySelector(".pct").textContent = `Recopilando información de la vergüenza: ${pct} %`;
        if (!calma) await espera(90);
    }
    pantalla.querySelector(".fin").textContent = "Es broma. Haz clic para volver.";
    pantalla.addEventListener("click", () => pantalla.remove());
    pantalla.addEventListener("keydown", e => { if (e.key === "Escape") pantalla.remove(); });
});

// --- Salvapantallas DVD: tras 60 s sin tocar nada; cualquier gesto lo cierra ---
let dvdActivo = false;
let dvdInicio = 0;  // cuándo empezó (para ignorar el gesto que lo provoca)
let reposo = null;  // temporizador de inactividad
function salvapantallas() {
    if (dvdActivo || calma) return;
    dvdActivo = true;
    dvdInicio = performance.now();  // milisegundos desde que se abrió la página
    const fondo = document.createElement("div");
    fondo.className = "salvapantallas fijo";
    const logo = document.createElement("div");
    logo.className = "dvd fijo";
    logo.textContent = "STEAM OPTIMIZER";
    document.body.append(fondo, logo);
    const colores = ["#00f0ff", "#ff2bd6", "#39ff14", "#ffe600", "#ff8c00", "#b388ff"];
    let x = 50, y = 50, vx = 2.2, vy = 1.8, ci = 0;  // posición, velocidad e índice de color
    function paso() {  // un fotograma de movimiento
        if (!dvdActivo) { fondo.remove(); logo.remove(); return; }  // cerrado: limpiamos y paramos
        const maxX = innerWidth - logo.offsetWidth, maxY = innerHeight - logo.offsetHeight;  // límites
        x += vx;
        y += vy;
        let choques = 0;  // paredes tocadas en este fotograma (2 = esquina)
        if (x <= 0 || x >= maxX) { vx = -vx; x = Math.max(0, Math.min(x, maxX)); choques++; }  // rebota en los lados
        if (y <= 0 || y >= maxY) { vy = -vy; y = Math.max(0, Math.min(y, maxY)); choques++; }  // rebota arriba/abajo
        if (choques) {
            ci = (ci + 1) % colores.length;  // siguiente color
            logo.style.color = colores[ci];
            SFX.blip(choques * 4);
        }
        if (choques === 2) {  // ¡esquina perfecta!
            confeti(x, y);
            flotante("¡¡ESQUINA!!", x, y);
            SFX.fanfarria();
            desbloquear("esquina");
        }
        logo.style.left = x + "px";
        logo.style.top = y + "px";
        requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
}
function despertar() {  // cualquier gesto: cierra el DVD (tras 0,8 s de gracia) y reinicia la cuenta
    if (dvdActivo && performance.now() - dvdInicio > 800) dvdActivo = false;
    clearTimeout(reposo);
    reposo = setTimeout(salvapantallas, 60000);  // 60 s
}
// passive: true avisa al navegador de que no bloqueamos el scroll (va más fluido)
["mousemove", "keydown", "scroll", "click", "touchstart"].forEach(ev => addEventListener(ev, despertar, { passive: true }));
despertar();  // empieza la cuenta al cargar

// --- Presentador cascarrabias: cada clic le enfada más; al final perdona y da el logro ---
const RESPUESTAS = [  // [cara, frase]
    ["😐", "¿Sí?"], ["😐", "Dime."], ["😑", "Eh."], ["😒", "Que ya."], ["😡", "¡DEJA DE TOCARME!"],
    ["😤", "Yare yare daze..."], ["🙄", "Me doy la vuelta."], ["🙃", "Hala. Contento."], ["🙃", "No te hablo."],
    ["🙃", "Se lo voy a decir a tu mamá."], ["🤫", "Psst... escribe za warudo (o the world). Yo no te he dicho nada."],
    ["🙂", "Vale, te perdono."],
];
const cascarrabias = document.getElementById("cascarrabias");  // null si no hay juego sorpresa
let toquesCascarrabias = 0;
if (cascarrabias) cascarrabias.addEventListener("click", () => {
    const [cara, frase] = RESPUESTAS[toquesCascarrabias];
    cascarrabias.querySelector(".cara").textContent = cara;
    cascarrabias.querySelector(".bocadillo").textContent = frase;
    if (toquesCascarrabias === 4) {  // el enfado gordo: sonido de error y temblor
        SFX.error();
        if (!calma) reanimar(cascarrabias, "temblor");
    } else {
        SFX.blip(toquesCascarrabias);
    }
    if (toquesCascarrabias === 5) {  // "Yare yare daze...": referencia a JoJo
        clip("yare", () => decir("やれやれだぜ", "Yare yare daze"));
        referencia("yare");
    }
    cascarrabias.classList.toggle("boca-abajo", toquesCascarrabias >= 7 && toquesCascarrabias < 10);  // toggle(clase, sí/no)
    if (toquesCascarrabias === RESPUESTAS.length - 1) desbloquear("compulsivo");  // llegó al perdón
    toquesCascarrabias = (toquesCascarrabias + 1) % RESPUESTAS.length;  // y vuelta a empezar
});

// ===================== Referencias a JoJo (paso 3.6f) =====================
// Cada referencia encontrada se apunta; con las 7 se desbloquea el logro "¿Eso es una JoJo referencia??"
const REFERENCIAS_JOJO = 7;  // stand, menacing, tbc, zawarudo, ora, dio, yare
const jojoVistas = new Set();
function referencia(id) {
    jojoVistas.add(id);
    if (jojoVistas.size === REFERENCIAS_JOJO) desbloquear("jojo");
}

// --- ゴゴゴゴ ("menacing"): flotan alrededor de la tarjeta con más horas al revelar su perfil ---
const SITIOS_GO = [["left", "8%"], ["right", "20%"], ["left", "45%"], ["right", "58%"], ["left", "80%"], ["right", "92%"]];
document.querySelectorAll(".stats[data-menacing] .btn-revelar").forEach(boton => {
    boton.addEventListener("click", () => setTimeout(() => {
        const tarjeta = boton.closest(".stats");  // closest: el antepasado más cercano que cumple el selector
        tarjeta.classList.add("menacing");
        SITIOS_GO.forEach(([lado, alto], i) => {  // [lado, alto] desempaqueta cada par
            const go = document.createElement("span");
            go.className = "gogogo";
            go.textContent = "ゴ";
            go.setAttribute("aria-hidden", "true");  // los lectores de pantalla lo ignoran
            go.style[lado] = "-0.7rem";  // a caballo del borde izquierdo o derecho
            go.style.top = alto;
            go.style.animationDelay = i * 0.3 + "s";  // cada una a su ritmo
            tarjeta.appendChild(go);
        });
        SFX.amenaza();
        referencia("menacing");
    }, 1500));  // cuando el perfil ya ha entrado
});

// --- To Be Continued ⟸: al llegar al final de la página (una vez por visita) ---
let tbcVisto = false;
addEventListener("scroll", () => {
    if (tbcVisto || innerHeight + scrollY < document.documentElement.scrollHeight - 5) return;
    tbcVisto = true;
    referencia("tbc");
    clip("tbc", SFX.continuara);  // "Roundabout" o, si no está, el riff sintetizado
    const victimas = document.querySelectorAll("body > :not(.fijo)");
    victimas.forEach(el => el.classList.add("sepia"));  // todo en tono de foto antigua
    const cartel = document.createElement("div");
    cartel.className = "tbc fijo";
    const flecha = document.createElement("p");
    flecha.className = "tbc-flecha";
    flecha.textContent = "To Be Continued";
    const sub = document.createElement("p");
    sub.className = "tbc-sub";
    sub.textContent = "Tus juegos pendientes... continuarán.";
    cartel.append(flecha, sub);
    document.body.appendChild(cartel);
    setTimeout(() => {  // a los 5 s, todo vuelve a la normalidad
        victimas.forEach(el => el.classList.remove("sepia"));
        cartel.remove();
    }, 5000);
}, { passive: true });

// --- ZA WARUDO: escribir "za warudo" o "the world" (con o sin espacio) para el tiempo 5 s ---
let teclasRecientes = "";  // las últimas teclas pulsadas
let tiempoParado = false;
addEventListener("keydown", e => {
    if (e.key.length !== 1) return;  // solo caracteres (no flechas, Shift, Enter...)
    teclasRecientes = (teclasRecientes + e.key.toLowerCase()).slice(-12);  // slice(-12): las 12 últimas
    const sinEspacios = teclasRecientes.replace(/ /g, "");  // replace(/ /g, ""): quita todos los espacios
    if (sinEspacios.endsWith("zawarudo") || sinEspacios.endsWith("theworld")) {  // || = "o"
        teclasRecientes = "";
        zaWarudo();
    }
});
function zaWarudo() {
    if (tiempoParado) return;
    tiempoParado = true;
    referencia("zawarudo");
    clip("zawarudo", () => { decir("ザ・ワールド！時よ止まれ！", "¡Za warudo! ¡Toki wo tomare!"); SFX.pararTiempo(); });
    document.documentElement.classList.add("tiempo-parado");  // documentElement = <html>: congela y pone en negativo
    const cartel = document.createElement("div");
    cartel.className = "za-warudo fijo";
    cartel.textContent = "¡TOKI WO TOMARE!";
    document.body.appendChild(cartel);
    setTimeout(() => {  // a los 5 s, el tiempo vuelve a fluir
        document.documentElement.classList.remove("tiempo-parado");
        cartel.textContent = "Y el tiempo vuelve a fluir...";
        clip("tiempo", () => decir("そして時は動き出す", "Y el tiempo vuelve a fluir"));
        setTimeout(() => {
            cartel.remove();
            tiempoParado = false;
        }, 2000);
    }, 5000);
}

// --- Juego sorpresa: ORA ORA / MUDA MUDA (5 "Otro" en 2 s) y "¡Pero era yo, Dio!" (20 % de las veces) ---
const btnOtroJojo = document.getElementById("sorpresa-otro");  // null si no hay juego sorpresa
const notaDio = document.getElementById("sorpresa-dio");
let golpesOtro = [];  // momentos (ms) de los últimos clics en "Otro"
let relojDio = null;
if (btnOtroJojo) btnOtroJojo.addEventListener("click", () => {
    const ahora = performance.now();
    golpesOtro = golpesOtro.filter(t => ahora - t < 2000);  // solo los de los últimos 2 s
    golpesOtro.push(ahora);
    if (golpesOtro.length >= 5) {
        golpesOtro = [];
        rafaga();
    } else if (Math.random() < 0.2) {
        dio();
    }
});
let enRafaga = false;  // ¿hay una ráfaga sonando? (evita que se acumulen)
function rafaga() {  // ráfaga de ORA (Jotaro) o MUDA (Dio), a cara o cruz
    if (enRafaga) return;  // mientras suena una, los clics no lanzan otra
    enRafaga = true;
    setTimeout(() => (enRafaga = false), 3000);  // libre otra vez a los 3 s
    const muda = Math.random() < 0.5;
    const grito = muda ? "MUDA" : "ORA";
    clip(muda ? "muda" : "ora", () => {
        decir(muda ? "無駄無駄無駄無駄" : "オラオラオラオラ", `${grito} ${grito} ${grito} ${grito}`);
        SFX.punetazos();
    }, 3);  // el clip se corta a los 3 s como máximo
    const r = btnOtroJojo.getBoundingClientRect();  // posición del botón en pantalla
    for (let i = 0; i < 12; i++) {  // 12 gritos repartidos alrededor del botón, uno cada 70 ms
        setTimeout(() => flotante(`${grito}!`, r.left + Math.random() * 240 - 60, r.top + Math.random() * 120 - 80, "ora"), i * 70);
    }
    referencia("ora");
}
function dio() {
    notaDio.textContent = "¿Esperabas una recomendación sensata? ¡Pero era yo, Dio!";
    clip("dio", () => { decir("このディオだ！", "¡Era yo, Dio!"); SFX.dramatico(); }, 3);  // máximo 3 s
    referencia("dio");
    clearTimeout(relojDio);  // si ya había uno en marcha, lo cancelamos
    relojDio = setTimeout(() => (notaDio.textContent = ""), 4000);
}
