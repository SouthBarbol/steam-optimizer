// Juego sorpresa: el botón "Otro" elige otro juego al azar entre los candidatos
// que el servidor ya metió en la página. No hace ninguna petición a Steam.

const caja = document.getElementById("sorpresa");  // el cuadro del juego sorpresa (null si no existe)

if (caja) {  // solo si hay cuadro (sin candidatos, la plantilla no lo dibuja)
    // dataset.candidatos lee el atributo data-candidatos; JSON.parse lo convierte en una lista de objetos
    const candidatos = JSON.parse(caja.dataset.candidatos);
    const nombre = document.getElementById("sorpresa-nombre");  // donde va el nombre del juego
    const nota = document.getElementById("sorpresa-nota");      // donde va la nota "(de Ana, ...)"

    // addEventListener: ejecuta la función cada vez que se pulsa el botón
    document.getElementById("sorpresa-otro").addEventListener("click", () => {
        let elegido;
        do {  // repite el sorteo si sale el mismo juego que ya se ve (si hay más de uno)
            // Math.random() da un número entre 0 y 1; por la longitud y redondeado abajo = posición al azar
            elegido = candidatos[Math.floor(Math.random() * candidatos.length)];
        } while (candidatos.length > 1 && elegido.nombre === nombre.textContent);

        // textContent escribe TEXTO (nunca HTML), así un nombre raro no puede inyectar código
        nombre.textContent = elegido.nombre;
        nota.textContent = elegido.desconocido
            ? `(de ${elegido.duenos.join(", ")}, puede que ya lo hayas probado)`  // ? : = if/else en una línea
            : "";
    });
}
