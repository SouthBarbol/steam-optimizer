// Librería (fase E1b): buscar por nombre y ordenar la tabla, todo en el navegador (no llama a ninguna web).
// La tabla ya la pintó Jinja2 (con escapado); aquí solo se ocultan y se mueven filas.
const plegable = document.getElementById("libreria-plegable");  // null si no hay librería
if (plegable) {
    const cuerpo = plegable.querySelector("tbody");
    let filas = [...cuerpo.rows];  // rows: las filas <tr>; [...]: lista normal (para poder ordenarla)
    const buscador = document.getElementById("buscar-juego");
    const contador = document.getElementById("buscar-contador");
    // "Pokémon" -> "pokemon": NFD separa la tilde de la letra y el replace borra las tildes sueltas
    const sinTildes = (t) => t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();

    // --- Buscar: oculta las filas cuyo nombre no contiene lo escrito ---
    buscador.addEventListener("input", () => {  // "input": cada vez que cambia el texto
        const busca = sinTildes(buscador.value.trim());  // trim: sin espacios al principio ni al final
        let vistos = 0;
        filas.forEach(f => {
            f.hidden = !sinTildes(f.dataset.nombre).includes(busca);  // includes: ¿contiene el texto?
            if (!f.hidden) vistos++;
        });
        contador.textContent = busca ? `Mostrando ${vistos} de ${filas.length}` : "";  // sin búsqueda, sin contador
    });
    buscador.parentElement.hidden = false;  // con JavaScript funcionando, el buscador ya se puede usar

    // --- Ordenar: las cabeceras con data-orden pasan a ser botones ---
    let orden = { campo: null, sube: true };  // qué columna manda y en qué sentido
    const cabeceras = [...plegable.querySelectorAll("th[data-orden]")];
    cabeceras.forEach(th => {
        const boton = document.createElement("button");
        boton.type = "button";
        boton.className = "ordenar";
        boton.textContent = th.textContent;  // el mismo texto ("Juego", "Tus horas")
        th.replaceChildren(boton);  // replaceChildren: cambia el texto de la cabecera por el botón
        boton.addEventListener("click", () => {
            const campo = th.dataset.orden;
            // Mismo botón: invierte el sentido. Otro: empieza por A-Z en nombres y por más horas en horas
            orden = orden.campo === campo ? { campo, sube: !orden.sube } : { campo, sube: campo === "nombre" };
            filas.sort((a, b) => {
                if (campo === "nombre") {  // localeCompare: orden alfabético en español (á junto a a)
                    const r = a.dataset.nombre.localeCompare(b.dataset.nombre, "es");
                    return orden.sube ? r : -r;
                }
                const ha = Number(a.dataset.horas), hb = Number(b.dataset.horas);
                if (ha < 0 || hb < 0) return (ha < 0) - (hb < 0);  // "—" (-1) siempre al final
                return orden.sube ? ha - hb : hb - ha;
            });
            filas.forEach(f => cuerpo.appendChild(f));  // appendChild de una fila existente la MUEVE al final
            cabeceras.forEach(c => (c.firstChild.dataset.flecha = c === th ? (orden.sube ? "▲" : "▼") : ""));
        });
    });

    // --- HIGH SCORES (E4): la primera vez que se abre la librería, las horas cuentan hacia arriba ---
    const calmaLib = matchMedia("(prefers-reduced-motion: reduce)").matches;  // ¿reducir movimiento?
    let contado = false;  // solo cuenta una vez por visita
    plegable.addEventListener("toggle", () => {  // toggle: al abrir o cerrar el <details>
        if (!plegable.open || contado || calmaLib) return;
        contado = true;
        // La celda de horas de cada fila; fuera las "—" (-1) y la del pantallazo azul (es un botón)
        const celdas = filas.map(f => f.cells[1])
            .filter(c => !c.querySelector("button") && Number(c.parentElement.dataset.horas) >= 0);
        const finales = celdas.map(c => c.textContent);  // el texto exacto, para dejarlo al terminar
        const inicio = performance.now();
        const paso = (ahora) => {  // un fotograma de la animación
            const t = Math.min((ahora - inicio) / 1200, 1);  // de 0 a 1 en 1,2 s
            celdas.forEach((c, i) => {
                const meta = Number(c.parentElement.dataset.horas);
                c.textContent = t < 1 ? (meta * t).toFixed(1).replace(".", ",") : finales[i];  // toFixed(1): un decimal
            });
            if (t < 1) requestAnimationFrame(paso);  // requestAnimationFrame: el siguiente fotograma del navegador
        };
        requestAnimationFrame(paso);
    });

    // Si se salta a la librería desde el menú, se abre sola (para no llegar a una caja cerrada)
    document.addEventListener("click", (e) => {
        if (e.target.closest('a[href="#libreria"]')) plegable.open = true;  // closest: el enlace o algo dentro
    });
}



