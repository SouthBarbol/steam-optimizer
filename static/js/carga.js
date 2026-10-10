// Muestra la caja de espera mientras Flask consulta a Steam (no llama a ninguna web)
const formulario = document.querySelector("form");  // el formulario del Steam ID
const caja = document.getElementById("cargando");  // la caja oculta con la animación

// "submit" se lanza al enviar el formulario (solo si pasa la validación del navegador)
formulario.addEventListener("submit", () => {
    caja.hidden = false;  // quitamos "hidden": la caja aparece
});

// "pageshow" se lanza al mostrar la página, también al volver con el botón Atrás.
// El navegador puede restaurar la página tal cual la dejamos (con la caja visible), así que la ocultamos
window.addEventListener("pageshow", () => {
    caja.hidden = true;
});
