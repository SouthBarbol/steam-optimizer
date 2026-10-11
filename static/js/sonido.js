// Motor de sonido: los efectos se GENERAN con código (Web Audio API), sin archivos ni librerías.
// Empieza silenciado salvo que la página anterior lo tuviera encendido (?sonido=1 en la URL, lo pone el
// formulario). Aun así, el navegador no deja sonar nada hasta el primer clic o tecla en cada página.
// Expone SFX (sonidos con nombre) para los demás scripts. No llama a ninguna web.

// ¿Está el sonido encendido? URLSearchParams lee los parámetros de la URL (?steam_id=...&sonido=1)
let sonidoActivo = new URLSearchParams(location.search).get("sonido") === "1";
let ctxAudio = null;  // "contexto de audio": la mesa de mezclas del navegador; se crea al primer uso
let audioListo = false;  // ¿ha habido ya un clic o tecla? Sin eso el navegador no deja sonar

// En el primer gesto del usuario "despertamos" el audio. capture: true = antes que cualquier otro oyente
function prepararAudio() {
    if (audioListo) return;
    audio().resume();
    audioListo = true;
}
["pointerdown", "keydown"].forEach(ev => addEventListener(ev, prepararAudio, { capture: true }));

function audio() {
    if (!ctxAudio) ctxAudio = new (window.AudioContext || window.webkitAudioContext)();  // webkit: Safari antiguo
    return ctxAudio;
}

// Un pitido: frecuencia (Hz), duración (s), forma de onda, retraso (s), volumen y frecuencia final (desliza el tono)
function tono(freq, dur = 0.1, tipo = "square", retraso = 0, vol = 0.07, freqFinal = null) {
    if (!sonidoActivo || !audioListo) return;  // silenciado o sin gesto aún: no hace nada (no se acumulan)
    const c = audio(), t = c.currentTime + retraso;  // t = momento en que empieza
    const osc = c.createOscillator(), gan = c.createGain();  // oscilador = genera la onda; gain = volumen
    osc.type = tipo;  // "square" (cuadrada) suena a consola de 8 bits
    osc.frequency.setValueAtTime(freq, t);
    if (freqFinal) osc.frequency.exponentialRampToValueAtTime(freqFinal, t + dur);  // desliza hasta freqFinal
    gan.gain.setValueAtTime(vol, t);
    gan.gain.exponentialRampToValueAtTime(0.0001, t + dur);  // se apaga poco a poco (evita un "clic")
    osc.connect(gan).connect(c.destination);  // oscilador -> volumen -> altavoces
    osc.start(t);
    osc.stop(t + dur + 0.05);
}

// Ruido blanco (golpes, explosiones); "filtro" en Hz quita los agudos y lo hace más grave; retraso en s
function ruido(dur = 0.3, vol = 0.15, filtro = null, retraso = 0) {
    if (!sonidoActivo || !audioListo) return;
    const c = audio();
    const buf = c.createBuffer(1, Math.floor(c.sampleRate * dur), c.sampleRate);  // 1 canal, "dur" segundos
    const datos = buf.getChannelData(0);
    for (let i = 0; i < datos.length; i++) datos[i] = (Math.random() * 2 - 1) * (1 - i / datos.length);  // azar que se apaga
    const fuente = c.createBufferSource();
    fuente.buffer = buf;
    const gan = c.createGain();
    gan.gain.value = vol;
    let nodo = fuente;  // último eslabón de la cadena
    if (filtro) {  // filtro "paso bajo": deja pasar solo los graves
        const f = c.createBiquadFilter();
        f.type = "lowpass";
        f.frequency.value = filtro;
        fuente.connect(f);
        nodo = f;
    }
    nodo.connect(gan).connect(c.destination);
    fuente.start(c.currentTime + retraso);  // empieza dentro de "retraso" segundos
}

// Nota MIDI -> frecuencia en Hz (69 = La a 440 Hz; cada número es un semitono; ** = potencia)
const hz = nota => 440 * 2 ** ((nota - 69) / 12);

// Catálogo de sonidos con nombre (se irán añadiendo más en los siguientes pasos)
const SFX = {
    blip: n => tono(260 + n * 45, 0.05),  // bloque de barra: cada uno más agudo (n = posición 0-9)
    voz: () => tono(500 + Math.random() * 300, 0.03, "square", 0, 0.03),  // "voz" del texto letra a letra
    moneda: () => { tono(988, 0.08); tono(1319, 0.35, "square", 0.08); },  // al activar el sonido
    fanfarria: () => {  // logro desbloqueado: tres notas subiendo y una larga
        [523, 659, 784].forEach((f, i) => tono(f, 0.14, "square", i * 0.11));
        tono(1047, 0.6, "square", 0.33);
        tono(784, 0.6, "triangle", 0.33, 0.06);
    },
    golpe: () => { tono(140, 0.25, "triangle", 0, 0.3, 40); ruido(0.15, 0.2, 800); },  // sello que cae
    // Paso 3.6d
    cuac: () => { tono(900, 0.12, "sawtooth", 0, 0.06, 350); tono(850, 0.14, "sawtooth", 0.15, 0.06, 300); },  // pato
    trombon: () => {  // "wah wah wah wahhh" triste: tres notas bajando y una larga que se hunde
        [392, 370, 349].forEach((f, i) => tono(f, 0.4, "sawtooth", i * 0.45, 0.05));
        tono(330, 1.1, "sawtooth", 1.35, 0.05, 250);
    },
    terremoto: () => ruido(1.3, 0.5, 120),  // retumbe: ruido muy filtrado (solo graves)
    glitch: () => ruido(0.12, 0.08, 4000),  // chisporroteo corto
    // Modo caos: tema ORIGINAL "a lo Sandstorm" (trance a 136 BPM). No copia la melodía real, que tiene derechos.
    trance: (compases = 4) => {
        const sem = 60 / 136 / 4;  // duración de una semicorchea: 60 s / 136 pulsos / 4 semicorcheas por pulso
        const acordes = [[69, 72, 76, 81], [65, 69, 72, 77], [64, 67, 72, 76], [62, 67, 71, 74]];  // Lam, Fa, Do, Sol
        const patron = [0, 2, 1, 2, 0, 2, 1, 2, 3, 2, 1, 2, 0, 2, 3, 2];  // nota del acorde en cada semicorchea
        for (let c = 0; c < compases; c++) {  // un acorde por compás
            const acorde = acordes[c % acordes.length];
            for (let s = 0; s < 16; s++) {  // 16 semicorcheas por compás
                const t = (c * 16 + s) * sem;  // cuándo suena esta semicorchea (s desde ahora)
                tono(hz(acorde[patron[s]]), sem * 0.9, "sawtooth", t, 0.035);  // arpegio "du-du-du-du"
                if (s % 4 === 0) tono(150, 0.18, "sine", t, 0.35, 40);  // bombo en cada pulso (tono que cae)
                if (s % 4 === 2) {  // a contratiempo: bajo (dos octavas abajo) y charles
                    tono(hz(acorde[0] - 24), sem * 1.8, "sawtooth", t, 0.05);
                    ruido(0.04, 0.05, 9000, t);
                }
            }
        }
    },
    error: () => { tono(220, 0.25, "square", 0, 0.08); tono(110, 0.5, "square", 0.25, 0.08); },  // 3.6e: dos notas graves
};

// Botón 🔇/🔊: enciende o apaga el sonido
const btnSonido = document.getElementById("btn-sonido");
const campoSonido = document.getElementById("campo-sonido");  // campo oculto del formulario
const avisoSonido = document.getElementById("aviso-sonido");  // bocadillo "el sonidito está apagao"

function pintarSonido() {  // pone el botón, el campo del formulario y el aviso según sonidoActivo
    btnSonido.textContent = sonidoActivo ? "🔊 SONIDO" : "🔇 SONIDO";
    btnSonido.setAttribute("aria-pressed", sonidoActivo);  // lectores de pantalla: botón pulsado o no
    campoSonido.value = sonidoActivo ? "1" : "0";  // viajará en la URL al pulsar "Analizar"
    if (sonidoActivo) avisoSonido.hidden = true;  // encendido: el aviso sobra
}

btnSonido.addEventListener("click", () => {
    sonidoActivo = !sonidoActivo;  // "!" invierte: true <-> false
    pintarSonido();
    SFX.moneda();  // solo suena si se acaba de encender (apagado, tono() no hace nada)
});

pintarSonido();  // estado inicial (puede venir encendido de la página anterior)
avisoSonido.hidden = sonidoActivo;  // apagado: mostramos el aviso...
setTimeout(() => (avisoSonido.hidden = true), 8000);  // ...durante 8 s

// ===================== Referencias a JoJo (paso 3.6f) =====================
// Clips ORIGINALES de la serie: tienen derechos de autor, solo para uso privado (ver SECURITY_CHECKLIST.md).
// Van en static/sonidos/ (en .gitignore: NO se suben a GitHub). Si falta un archivo, suena el respaldo.
const CLIPS = {
    zawarudo: "za-warudo.mp3",  // Dio: "ZA WARUDO! Toki wo tomare!"
    tiempo: "tiempo-fluye.mp3",  // "Soshite toki wa ugokidasu" (y el tiempo vuelve a fluir)
    ora: "ora-ora.mp3",  // Jotaro: "ORA ORA ORA..."
    muda: "muda-muda.mp3",  // Dio: "MUDA MUDA MUDA..."
    tbc: "to-be-continued.mp3",  // "Roundabout" (Yes), el final de los episodios
    dio: "kono-dio-da.mp3",  // Dio: "Kono Dio da!" (¡pero era yo, Dio!)
    yare: "yare-yare.mp3",  // Jotaro: "Yare yare daze"
};

function clip(nombre, respaldo, maxSeg = 0) {  // reproduce un clip; si falla, "respaldo"; maxSeg > 0 lo corta
    if (!sonidoActivo || !audioListo) return;
    const reproductor = new Audio(`/static/sonidos/${CLIPS[nombre]}`);  // Audio: reproductor de un archivo de sonido
    reproductor.volume = 0.7;  // de 0 a 1
    // play() devuelve una "promesa": si el archivo no está (404) o no se puede reproducir, salta el catch
    reproductor.play().catch(() => { if (respaldo) respaldo(); });
    if (maxSeg) setTimeout(() => reproductor.pause(), maxSeg * 1000);  // pause(): lo para a los maxSeg segundos
}

// Voz del navegador (síntesis de voz, sin librerías): en japonés si hay una voz japonesa instalada;
// si no, la versión en español (una voz española leyendo japonés no diría nada)
function decir(japones, espanol) {
    if (!sonidoActivo || !audioListo || !window.speechSynthesis) return;  // navegador sin voz: nada
    const hayJapones = speechSynthesis.getVoices().some(v => v.lang.startsWith("ja"));  // some: ¿alguna cumple?
    const frase = new SpeechSynthesisUtterance(hayJapones ? japones : espanol);
    frase.lang = hayJapones ? "ja-JP" : "es-ES";
    frase.pitch = 0.6;  // tono más grave: más dramático
    frase.rate = 1.1;  // un pelín más rápido
    speechSynthesis.cancel();  // corta lo que estuviera diciendo: así las frases no se acumulan en cola
    speechSynthesis.speak(frase);
}

// Respaldos sintetizados (y sonidos sin clip). Object.assign añade más sonidos al catálogo SFX
Object.assign(SFX, {
    amenaza: () => { tono(55, 2.5, "sawtooth", 0, 0.05, 50); tono(58, 2.5, "sawtooth", 0, 0.04, 52); },  // ゴゴゴ: zumbido grave
    pararTiempo: () => {  // barrido que cae, tic-tac que se ralentiza y dos latidos
        tono(1200, 1.2, "sawtooth", 0, 0.06, 60);
        [0, 0.3, 0.7, 1.2, 1.9].forEach(t => tono(1500, 0.03, "square", 1.2 + t, 0.05));
        tono(60, 0.25, "sine", 3.4, 0.3, 40);
        tono(60, 0.25, "sine", 3.7, 0.3, 40);
    },
    punetazos: () => {  // ráfaga de golpes, cada vez más seguidos
        for (let i = 0; i < 12; i++) ruido(0.05, 0.25, 1500, i * (0.12 - i * 0.005));
    },
    dramatico: () => {  // "dun, dun, duuun"
        tono(110, 0.3, "sawtooth", 0, 0.08);
        tono(104, 0.3, "sawtooth", 0.35, 0.08);
        tono(98, 1, "sawtooth", 0.7, 0.08);
    },
    continuara: () => {  // riff de bajo ORIGINAL (no es "Roundabout"): Mi Mi Sol La Si
        [40, 40, 43, 45, 47].forEach((n, i) => tono(hz(n), 0.25, "triangle", i * 0.28, 0.12));
    },
});
