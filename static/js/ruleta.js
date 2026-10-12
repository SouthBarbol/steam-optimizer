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

    if (fichas.length > 1) {  // con un solo juego no hay nada que sortear
        btnRuleta.addEventListener("click", () => {
            // filter: todas menos la que ya se ve (así nunca repite)
            const otras = fichas.filter(x => x.nombre !== nombre.textContent);
            if (!otras.length) return;  // si no queda ninguna distinta, no hace nada
            const f = otras[Math.floor(Math.random() * otras.length)];  // posición al azar
            if (!Number.isInteger(f.appid)) return;  // el appid va en URLs: solo si es un número entero
            img.src = `https://cdn.cloudflare.steamstatic.com/steam/apps/${f.appid}/header.jpg`;
            img.alt = `Carátula de ${f.nombre}`;  // alt es texto: no se interpreta como HTML
            nombre.textContent = f.nombre;  // textContent: TEXTO, nunca HTML (no se puede inyectar código)
            frase.textContent = `«${f.frase}»`;
            enlace.href = `https://store.steampowered.com/app/${f.appid}/`;
        });
        btnRuleta.hidden = false;  // con JavaScript funcionando, ya se puede usar
    }
}
