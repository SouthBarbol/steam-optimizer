// Logros absurdos: contador X/N, lista desplegable y avisos en cola. No se guarda nada (al recargar, a 0).
// Usa SFX (sonido.js) y espera (efectos.js). Otros scripts pueden llamar a desbloquear("id").
// No llama a ninguna web.

const zonaLogros = document.getElementById("trofeos");  // null si la página no tiene resultados
// JSON.parse convierte el texto JSON del atributo data-catalogo en una lista de JavaScript
const catalogoLogros = zonaLogros ? JSON.parse(zonaLogros.dataset.catalogo) : [];
const ganadosLogros = new Set();  // Set = conjunto (como en Python): ids desbloqueados, sin repetir
const colaLogros = [];  // avisos pendientes de mostrar
let mostrandoLogro = false;  // ¿hay un aviso en pantalla?

function desbloquear(id) {  // gana un logro (si existe y no lo tenías ya)
    const logro = catalogoLogros.find(l => l.id === id);  // find: el primero que cumple la condición
    if (!logro || ganadosLogros.has(id)) return;
    ganadosLogros.add(id);
    pintarLogros();  // actualiza contador y lista
    colaLogros.push(logro);  // push: añade al final de la cola
    if (!mostrandoLogro) siguienteLogro();  // si no hay ninguno en pantalla, arranca la cola
}

async function siguienteLogro() {  // muestra los avisos de la cola, uno detrás de otro
    mostrandoLogro = true;
    while (colaLogros.length) {
        const l = colaLogros.shift();  // shift: saca el primero de la cola
        // Construimos el aviso con createElement + textContent (nunca innerHTML)
        const aviso = document.createElement("div");
        aviso.className = "toast";
        const icono = document.createElement("span");
        icono.className = "toast-icono";
        icono.textContent = l.icono;
        const texto = document.createElement("div");
        const cabecera = document.createElement("small");
        cabecera.textContent = "LOGRO DESBLOQUEADO";
        const titulo = document.createElement("strong");
        titulo.textContent = l.titulo;
        const frase = document.createElement("p");
        frase.textContent = l.texto;
        texto.append(cabecera, titulo, frase);  // append admite varios elementos a la vez
        aviso.append(icono, texto);
        document.getElementById("toasts").appendChild(aviso);
        SFX.fanfarria();
        await espera(4000);  // 4 s en pantalla...
        aviso.classList.add("saliendo");  // ...animación de salida...
        await espera(400);
        aviso.remove();  // ...y fuera
    }
    mostrandoLogro = false;
}

function pintarLogros() {  // contador "🏆 X/N" y lista (los pendientes salen como "???")
    document.getElementById("btn-logros").textContent = `🏆 ${ganadosLogros.size}/${catalogoLogros.length}`;
    const lista = document.getElementById("lista-logros");
    lista.textContent = "";  // vacía la lista para rehacerla
    for (const l of catalogoLogros) {
        const li = document.createElement("li");
        if (ganadosLogros.has(l.id)) {
            li.textContent = `${l.icono} ${l.titulo}: ${l.texto}`;
        } else {
            li.textContent = "🔒 ???";
            li.className = "bloqueado";
        }
        lista.appendChild(li);
    }
}

if (zonaLogros) {  // todo lo de abajo, solo en la página de resultados
    pintarLogros();

    // Botón 🏆: abre o cierra la lista
    const btnLogros = document.getElementById("btn-logros");
    btnLogros.addEventListener("click", () => {
        const lista = document.getElementById("lista-logros");
        lista.hidden = !lista.hidden;
        btnLogros.setAttribute("aria-expanded", !lista.hidden);  // lectores de pantalla: abierta o cerrada
    });

    // Logros de la visita: los de tus datos (calculados por Flask) + Insomne (hora de tu navegador, 0:00-5:59)
    const deLaVisita = JSON.parse(zonaLogros.dataset.ganados);
    if (new Date().getHours() < 6) deLaVisita.push("insomne");
    const darLogrosVisita = () => deLaVisita.forEach(desbloquear);
    // Salen al revelar TU perfil (la primera tarjeta), tras su animación. Si no hay botón, al poco de cargar
    const tuBoton = document.querySelector(".stats-rejilla > .stats:first-child .btn-revelar");
    if (tuBoton) tuBoton.addEventListener("click", () => setTimeout(darLogrosVisita, 2500));
    else setTimeout(darLogrosVisita, 1500);

    // Ludópata del azar: pulsar "Otra" 10 veces en la ruleta del caos
    let vecesOtro = 0;
    const btnOtro = document.getElementById("ruleta-otra");  // null si no hay ruleta
    if (btnOtro) btnOtro.addEventListener("click", () => {
        vecesOtro++;
        if (vecesOtro >= 10) desbloquear("ludopata");
    });

    // Corazón de piedra / Enamoradizo: ❌ o 💚 a TODAS las fichas de Steam Match (cada una cuenta una vez)
    const totalFichas = document.querySelectorAll("#match .ficha").length;
    const rechazados = new Set(), elegidos = new Set();  // Set: colección sin repetidos
    const anotar = (conjunto) => {
        // la ficha que se ve (match.js la cambia 350 ms después del clic, así que aún es la votada)
        const visible = document.querySelector("#match .ficha:not([hidden]) .ficha-nombre");
        if (visible) conjunto.add(visible.textContent);
        if (rechazados.size === totalFichas && elegidos.size === 0) desbloquear("piedra");
        if (elegidos.size === totalFichas) desbloquear("enamoradizo");
    };
    const btnNoLogro = document.getElementById("match-no"), btnSiLogro = document.getElementById("match-si");
    if (btnNoLogro) btnNoLogro.addEventListener("click", () => anotar(rechazados));
    if (btnSiLogro) btnSiLogro.addEventListener("click", () => anotar(elegidos));

    // Sin miedo: abrir en Steam un juego de "¿Te atreves?" (el clic llega antes de que se abra la pestaña)
    document.querySelectorAll("#atreverse .ver-steam").forEach(a =>
        a.addEventListener("click", () => desbloquear("sinmiedo")));

    // Gusto raro (5.5d): abrir en Steam un juego de las bizarras de "¿Qué comprar?"
    document.querySelectorAll(".compra-rejilla.bizarra .ver-steam").forEach(a =>
        a.addEventListener("click", () => desbloquear("gusto")));

    // Explorador del abismo: llegar al final de la página (con 5 px de margen)
    window.addEventListener("scroll", () => {
        if (innerHeight + scrollY >= document.documentElement.scrollHeight - 5) desbloquear("abismo");
    });
}
