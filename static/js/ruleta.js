// Tragaperras (pasos 4.4, 4.5b y 5.4): el botón "Otra" sortea otra ficha entre las que el servidor ya metió
// en la sección (cada una con su frase absurda ya escrita) y la enseña con giro de tragaperras: el nombre gira
// ~1 s entre juegos al azar y se para en el elegido. No llama a ninguna web.
// Sirve para TODAS las secciones con clase "tragaperras" (la ruleta de tu librería y la de la tienda).
const quietoRuleta = matchMedia("(prefers-reduced-motion: reduce)").matches;  // ¿reducir movimiento?
const GIRO_MS = 1000, PASO_MS = 70;  // dura 1 s; cambia de nombre cada 70 ms

function montarTragaperras(seccion) {
    const fichas = JSON.parse(seccion.dataset.fichas);  // data-fichas -> lista de {nombre, appid, frase, detalle?}
    const parte = (clase) => seccion.querySelector(clase);  // busca SOLO dentro de esta sección
    const img = parte(".tragaperras-img");
    const nombre = parte(".ficha-nombre");
    const frase = parte(".tragaperras-frase");
    const detalle = parte(".tragaperras-detalle");  // null en la ruleta de la librería (no tiene)
    const enlace = parte(".ver-steam");
    const boton = parte(".tragaperras-otra");
    const ficha = img.closest(".ficha");  // closest: el antepasado más cercano con esa clase
    let actual = nombre.textContent;  // el juego elegido (durante el giro, el texto visible es aleatorio)
    let giro = null;  // temporizador del giro en marcha (null si no gira)

    const pintar = (f) => {  // enseña la ficha f entera
        img.src = `https://cdn.cloudflare.steamstatic.com/steam/apps/${f.appid}/header.jpg`;
        img.alt = `Carátula de ${f.nombre}`;  // alt es texto: no se interpreta como HTML
        nombre.textContent = f.nombre;  // textContent: TEXTO, nunca HTML (no se puede inyectar código)
        frase.textContent = `«${f.frase}»`;
        if (detalle) detalle.textContent = f.detalle;  // precio y reseñas (solo en la tienda)
        enlace.href = `https://store.steampowered.com/app/${f.appid}/`;
    };

    if (fichas.length < 2) return;  // con un solo juego no hay nada que sortear (el botón sigue oculto)
    boton.addEventListener("click", () => {
        // Todas menos la elegida (así nunca repite), y solo con appid entero (va en las URLs)
        const otras = fichas.filter(x => x.nombre !== actual && Number.isInteger(x.appid));
        if (!otras.length) return;  // si no queda ninguna distinta, no hace nada
        const f = otras[Math.floor(Math.random() * otras.length)];  // la ganadora, al azar
        actual = f.nombre;
        clearInterval(giro);  // si ya giraba, se reinicia con la nueva ganadora
        if (quietoRuleta) return pintar(f);  // sin animación: directo
        ficha.classList.add("girando");  // CSS: carátula desenfocada
        frase.textContent = "«…»";
        const fin = performance.now() + GIRO_MS;  // momento en que debe pararse
        giro = setInterval(() => {  // se repite cada PASO_MS
            if (performance.now() >= fin) {  // se acabó el giro
                clearInterval(giro);
                ficha.classList.remove("girando");
                pintar(f);
                SFX.moneda();
                return;
            }
            nombre.textContent = fichas[Math.floor(Math.random() * fichas.length)].nombre;  // nombre al azar
            SFX.tic();
        }, PASO_MS);
    });
    boton.hidden = false;  // con JavaScript funcionando, ya se puede usar
}

document.querySelectorAll(".tragaperras").forEach(montarTragaperras);  // una por sección
