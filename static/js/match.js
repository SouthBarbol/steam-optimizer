// Steam Match (paso 4.3c): pasa fichas con ❌ / 💚 y sincroniza la ficha con la lista.
// Las fichas y la lista ya las pintó Jinja2 (con escapado); aquí solo se muestran u ocultan
// (hidden, clases y textContent). No llama a ninguna web y no guarda nada.
const seccionMatch = document.getElementById("match");  // null si no hay recomendaciones
const fichas = seccionMatch ? [...seccionMatch.querySelectorAll(".ficha")] : [];  // [...]: lista normal
if (fichas.length) {  // sin fichas (o sin sección) no hay nada que hacer
    const filas = [...seccionMatch.querySelectorAll(".fila")];
    const btnNo = document.getElementById("match-no");
    const btnSi = document.getElementById("match-si");
    const aviso = document.getElementById("es-match");
    // ¿Pidió el sistema "reducir movimiento"? Entonces, cambios sin animación
    const quieto = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const DURACION = quieto ? 0 : 350;  // ms que tarda la ficha en salir (igual que la transition del CSS)
    let actual = 0;  // posición de la ficha que se ve
    let ocupado = false;  // true mientras una ficha sale volando (ignora clics)

    // Funciones con "const": así no se escapan al espacio global que comparten todos los scripts
    const mostrar = (i) => {  // enseña la ficha i y resalta su fila
        fichas.forEach((f, n) => (f.hidden = n !== i));  // oculta todas menos la i
        filas.forEach((f, n) => f.classList.toggle("actual", n === i));  // toggle(clase, sí/no)
        actual = i;
    };

    const lanzar = (lado) => {  // la ficha sale por "izq" o "der" y entra la siguiente
        ocupado = true;
        const ficha = fichas[actual];
        ficha.classList.add(lado);  // el CSS la desliza y la gira
        setTimeout(() => {  // cuando ha terminado de salir...
            ficha.classList.remove(lado);  // ...la dejamos como estaba (para cuando vuelva)
            mostrar((actual + 1) % fichas.length);  // % = resto: tras la última, la primera
            ocupado = false;
        }, DURACION);
    };

    btnNo.addEventListener("click", () => {
        if (ocupado) return;
        aviso.textContent = "";
        lanzar("izq");
    });

    btnSi.addEventListener("click", () => {
        if (ocupado) return;
        const nombre = fichas[actual].querySelector(".ficha-nombre").textContent;  // texto ya escapado por Jinja2
        aviso.textContent = `¡ES UN MATCH! Tú y ${nombre} 💚`;  // textContent: texto, nunca HTML
        filas[actual].querySelector(".fila-match").hidden = false;  // 💚 en su fila
        lanzar("der");
    });

    filas.forEach((fila, i) => {
        fila.tabIndex = 0;  // se puede llegar con la tecla Tab
        const elegir = (evento) => {
            if (ocupado || evento.target.closest("a")) return;  // el enlace "STEAM ↗" va a lo suyo
            aviso.textContent = "";
            mostrar(i);
            fichas[i].scrollIntoView({ behavior: quieto ? "auto" : "smooth", block: "center" });  // sube a la ficha
        };
        fila.addEventListener("click", elegir);
        fila.addEventListener("keydown", (e) => { if (e.key === "Enter") elegir(e); });  // Enter = clic
    });

    btnNo.hidden = btnSi.hidden = false;  // con JavaScript funcionando, ya se pueden usar
    mostrar(0);  // marca la primera fila como "actual"
}
