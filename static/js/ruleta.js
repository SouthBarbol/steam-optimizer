// Ruleta del caos (paso 4.4): el botón "Otra" sortea otra ficha entre las que el servidor ya metió
// en la página (cada una con su frase absurda ya escrita). No llama a ninguna web.
const ruleta = document.getElementById("ruleta");  // la sección (null si no hay juegos)
if (ruleta) {
    const fichas = JSON.parse(ruleta.dataset.fichas);  // data-fichas -> lista de {nombre, appid, frase}
    const img = document.getElementById("ruleta-img");
    const nombre = document.getElementById("ruleta-nombre");
    const frase = document.getElementById("ruleta-frase");
    const enlace = document.getElementById("ruleta-steam");
    const btnRuleta = document.getElementById("ruleta-otra");

    // Tragaperras (paso 4.5b): el nombre gira ~1 s entre juegos al azar y se para en el elegido
    const ficha = img.closest(".ficha");  // closest: el antepasado más cercano con esa clase
    const quietoRuleta = matchMedia("(prefers-reduced-motion: reduce)").matches;  // ¿reducir movimiento?
    const GIRO_MS = 1000, PASO_MS = 70;  // dura 1 s; cambia de nombre cada 70 ms
    let actual = nombre.textContent;  // el juego elegido (durante el giro, el texto visible es aleatorio)
    let giro = null;  // temporizador del giro en marcha (null si no gira)

    const pintar = (f) => {  // enseña la ficha f entera
        img.src = `https://cdn.cloudflare.steamstatic.com/steam/apps/${f.appid}/header.jpg`;
        img.alt = `Carátula de ${f.nombre}`;  // alt es texto: no se interpreta como HTML
        nombre.textContent = f.nombre;  // textContent: TEXTO, nunca HTML (no se puede inyectar código)
        frase.textContent = `«${f.frase}»`;
        enlace.href = `https://store.steampowered.com/app/${f.appid}/`;
    };

    if (fichas.length > 1) {  // con un solo juego no hay nada que sortear
        btnRuleta.addEventListener("click", () => {
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
        btnRuleta.hidden = false;  // con JavaScript funcionando, ya se puede usar
    }
}
