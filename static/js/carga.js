// Carga "sospechosa": mientras Flask consulta a Steam, la barra sube al 99 % y se atasca con excusas.
// La espera es real (la marca el servidor); esto solo la adorna. No llama a ninguna web.
// Ojo: todos los <script> de la página comparten nombres globales; no repetir los de otros archivos (p. ej. "caja")
const formulario = document.querySelector("form");  // el formulario del Steam ID
const cajaCarga = document.getElementById("cargando");  // la caja oculta con la animación
const cargaTexto = document.getElementById("carga-texto");  // el texto que va cambiando
const cargaRelleno = document.getElementById("carga-relleno");  // la parte verde de la barra
let cargaReloj = null;  // temporizador en marcha (para poder pararlo)

// Excusas del 99 %. La primera sale siempre; el resto, en orden aleatorio
const EXCUSAS = [
    "Tu padre dice que si la de trabajar te la sabes.",
    "Me eché a tu mamá me eché a tu mamá.",
    "Tu mamá dice que es tarde para estar con el Steam.",
    "Esperando a que tu mamá cuelgue el teléfono...",
    "Tu padre ha visto tus horas y se ha tenido que sentar.",
    "Tu parienta quiere saber por qué tienes tantos juegos sin abrir.",
    "Vale, ya. Tu mamá te manda saludos.",
    "Pajerito premium",
    "El último 1 % es duro de pelar, pichita.",
    "Casi. De verdad. Palabra de supercolega del infierno.",
    "Steam va a pedales hoy, no es culpa mía.",
    "Tu mamá está usando su Stand para frenar la barra.",
    "Tu mamá dice que escribas «za warudo». No sé, ella sabrá.",
];

function excusas() {  // fase 2: atascado en el 99 %, cambiando de excusa
    // [primera, ...resto barajado]; sort con un número al azar desordena la lista (sencillo, vale para esto)
    const orden = [EXCUSAS[0], ...EXCUSAS.slice(1).sort(() => Math.random() - 0.5)];
    let n = 0;  // cuántas excusas llevamos
    const siguiente = () => {
        cargaTexto.textContent = `99 % · ${orden[n % orden.length]}`;  // % = resto: al acabar, vuelve a empezar
        SFX.blip(1);  // un pitido por excusa (no suena si el sonido está apagado)
        n++;
    };
    siguiente();  // la primera, ya
    cargaReloj = setInterval(siguiente, 2200);  // y luego una cada 2,2 s
}

// "submit" se lanza al enviar el formulario (solo si pasa la validación del navegador)
formulario.addEventListener("submit", () => {
    cajaCarga.hidden = false;  // quitamos "hidden": la caja aparece
    let pct = 0;  // porcentaje mostrado
    clearInterval(cargaReloj);  // por si quedaba uno de antes
    // fase 1: sube un 3 % cada 60 ms hasta el 99 % (unos 2 s)
    cargaReloj = setInterval(() => {
        pct = Math.min(pct + 3, 99);  // Math.min: nunca pasa de 99
        cargaRelleno.style.width = pct + "%";
        cargaTexto.textContent = `Analizando tu librería... ${pct} %`;
        if (pct === 99) {  // llegó al 99: paramos esta fase y empiezan las excusas
            clearInterval(cargaReloj);
            excusas();
        }
    }, 60);
});

// "pageshow" se lanza al mostrar la página, también al volver con el botón Atrás.
// El navegador puede restaurar la página tal cual la dejamos (con la caja visible), así que la reiniciamos
window.addEventListener("pageshow", () => {
    clearInterval(cargaReloj);  // para la barra o las excusas
    cajaCarga.hidden = true;
    cargaRelleno.style.width = "0";
});
