// "¿Te atreves?" (paso 4.R5): el botón "Otro" enseña el siguiente juego de territorio inexplorado.
// Las tarjetas ya las pintó Jinja2 (con escapado); aquí solo se cambia "hidden". No llama a ninguna web.
const retos = [...document.querySelectorAll(".reto")];  // [...]: lista normal; [] si no hay sección
if (retos.length > 1) {  // con un solo juego no hace falta el botón
    const btnReto = document.getElementById("reto-otro");
    let visible = 0;  // posición de la tarjeta que se ve
    btnReto.addEventListener("click", () => {
        retos[visible].hidden = true;  // oculta la actual...
        visible = (visible + 1) % retos.length;  // ...pasa a la siguiente (% = resto: tras la última, la 1.ª)
        retos[visible].hidden = false;  // ...y la enseña
    });
    btnReto.hidden = false;  // con JavaScript funcionando, ya se puede usar
}
