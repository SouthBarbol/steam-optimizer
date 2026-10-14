// Compartir resumen (estilo Spotify Wrapped): dibuja TU resumen en un <canvas> de 1080×1920 y lo descarga
// como PNG. Todo pasa en tu navegador: la imagen no se sube a ningún sitio. Nunca lleva el Steam ID.
const btnCompartir = document.getElementById("btn-compartir");  // solo existe en la página de resultados
const ANCHO = 1080, ALTO = 1920, MARGEN = 80;  // tamaño de historia de Instagram/WhatsApp
const COLOR = { fondo: "#0b0b1a", cian: "#00f0ff", magenta: "#ff2bd6", texto: "#e6e6ff" };  // los de style.css
const FUENTE = '"Press Start 2P", monospace';
const coma = (n) => String(n).replace(".", ",");  // 4.2 -> "4,2" (decimales a la española)

// Escribe un texto centrado partiéndolo en líneas que quepan; devuelve la "y" donde seguir escribiendo
function escribirEnLienzo(ctx, texto, y, tamano, color) {
    ctx.font = `${tamano}px ${FUENTE}`;  // tamaño y fuente del pincel
    ctx.fillStyle = color;
    const palabras = String(texto).split(" ");
    let linea = "";
    for (const p of palabras) {  // vamos añadiendo palabras mientras quepan en el ancho útil
        const prueba = linea ? `${linea} ${p}` : p;
        if (ctx.measureText(prueba).width > ANCHO - 2 * MARGEN && linea) {  // no cabe: pintamos y saltamos
            ctx.fillText(linea, ANCHO / 2, y);
            y += tamano * 1.6;  // interlineado
            linea = p;
        } else linea = prueba;
    }
    ctx.fillText(linea, ANCHO / 2, y);  // la última línea
    return y + tamano * 1.6;
}

async function dibujarResumen(r) {  // async: puede "esperar" (await) a que cargue la fuente
    await document.fonts.load(`40px ${FUENTE}`);  // sin esto, el canvas pintaría con otra letra
    const lienzo = document.createElement("canvas");  // en memoria: no se añade a la página
    lienzo.width = ANCHO; lienzo.height = ALTO;
    const ctx = lienzo.getContext("2d");  // el "pincel" 2D
    ctx.fillStyle = COLOR.fondo; ctx.fillRect(0, 0, ANCHO, ALTO);  // fondo
    ctx.strokeStyle = COLOR.magenta; ctx.lineWidth = 12;  // borde neón
    ctx.strokeRect(30, 30, ANCHO - 60, ALTO - 60);
    ctx.textAlign = "center";  // x = el centro del texto
    // y = el borde de ARRIBA del texto (por defecto es la línea base y los textos grandes pisarían al anterior)
    ctx.textBaseline = "top";

    let y = 110;  // cursor vertical: baja tras cada texto
    // en minúsculas: Press Start 2P no tiene la É mayúscula. 44 px: así cabe en una línea
    y = escribirEnLienzo(ctx, "¿Qué juego toca hoy?", y, 44, COLOR.cian);
    y = escribirEnLienzo(ctx, r.nombre, y + 10, 36, COLOR.magenta);
    if (r.perfil) {  // perfil gamer (None si no hay datos de etiquetas)
        y = escribirEnLienzo(ctx, r.perfil.titulo, y + 60, 40, COLOR.cian);
        y = escribirEnLienzo(ctx, r.perfil.frase, y, 24, COLOR.texto);
    }
    y = escribirEnLienzo(ctx, `${r.horas} H`, y + 50, 100, COLOR.magenta);  // las horas, bien grandes
    y = escribirEnLienzo(ctx, `= ${coma(r.dias)} días seguidos`, y, 28, COLOR.texto);
    if (r.comparacion) y = escribirEnLienzo(ctx, `o ${r.comparacion}`, y + 10, 22, COLOR.texto);

    const fav = r.favorito;  // tu juego más jugado (null si no has jugado a nada)
    if (fav) {
        y = escribirEnLienzo(ctx, "TU VICIO:", y + 45, 30, COLOR.cian);
        const img = await cargarImagen(`https://cdn.cloudflare.steamstatic.com/steam/apps/${fav.appid}/header.jpg`);
        const ancho = 640, alto = 299;  // la carátula de Steam (460×215) ampliada sin deformarla
        if (img) {  // null solo si fallan la de Steam y la nuestra
            ctx.drawImage(img, (ANCHO - ancho) / 2, y + 10, ancho, alto);  // centrada: x = (sobrante) / 2
            y += alto + 30;  // bajamos el cursor por debajo de la imagen
        }
        y = escribirEnLienzo(ctx, `${fav.nombre} · ${fav.horas} h`, y, 26, COLOR.magenta);
    }

    y = escribirEnLienzo(ctx, `PILE OF SHAME: ${coma(r.pile_pct)} %`, y + 45, 34, COLOR.cian);
    y = escribirEnLienzo(ctx, `${r.sin_jugar} de ${r.total} sin estrenar · ${r.abandonados} abandonados`, y, 22, COLOR.texto);

    y = escribirEnLienzo(ctx, `STAND: ${r.stand.nombre}`, y + 45, 28, COLOR.cian);
    const columna = (ANCHO - 2 * MARGEN) / 3;  // 3 columnas en el ancho útil
    r.stand.notas.forEach((n, i) => {  // i = 0..5 -> fila i/3 (redondeada abajo) y columna i % 3 (resto)
        const centro = MARGEN + columna * (i % 3) + columna / 2;  // centro de su columna
        const fila = y + Math.floor(i / 3) * 50;  // cada fila, 50 px más abajo
        ctx.font = `20px ${FUENTE}`;
        const nombre = `${n.nombre} `;  // con espacio detrás, para separarlo de la nota
        // empezamos media pareja "Nombre A" a la izquierda del centro: así la pareja queda centrada
        const inicio = centro - ctx.measureText(nombre + n.nota).width / 2;
        ctx.textAlign = "left";  // ahora x = donde EMPIEZA el texto (para pintar uno detrás de otro)
        ctx.fillStyle = COLOR.texto;
        ctx.fillText(nombre, inicio, fila);  // el nombre en blanco...
        ctx.fillStyle = COLOR.magenta;
        ctx.fillText(n.nota, inicio + ctx.measureText(nombre).width, fila);  // ...y la nota detrás, en magenta
        ctx.textAlign = "center";  // lo dejamos como estaba para los demás textos
    });
    y += 100;  // 2 filas de notas

    if (r.match) {  // el n.º 1 de Steam Match (puede no haber)
        y = escribirEnLienzo(ctx, "STEAM MATCH TE RECOMIENDA:", y + 25, 26, COLOR.cian);
        escribirEnLienzo(ctx, r.match.nombre, y, 30, COLOR.magenta);
    }
    return lienzo;
}

// Carga una imagen y espera a que llegue. crossOrigin "anonymous": la pide con permiso CORS (Steam lo da),
// así el canvas no queda "contaminado" y se puede exportar. Si falla, usamos nuestra sin-caratula.svg
// (SIN_CARATULA viene de efectos.js, que ya está cargado cuando se pulsa el botón)
function cargarImagen(url) {
    return new Promise((listo) => {  // Promise: "te aviso cuando acabe" (await espera a ese aviso)
        const img = new Image();
        img.crossOrigin = "anonymous";
        img.onload = () => listo(img);
        // si falla la de Steam, probamos la nuestra; si falla también la nuestra, null (sin imagen)
        img.onerror = () => url === SIN_CARATULA ? listo(null) : cargarImagen(SIN_CARATULA).then(listo);
        img.src = url;
    });
}

// Descarga el PNG (en el PC, o si el móvil no deja compartir)
function descargar(blob) {
    const enlace = document.createElement("a");  // enlace invisible para descargarlo
    enlace.href = URL.createObjectURL(blob);  // dirección temporal al archivo en memoria
    enlace.download = "mi-resumen-steam.png";  // nombre del archivo descargado
    enlace.click();
    // liberamos la memoria un segundo después (si es al instante, Firefox puede cancelar la descarga)
    setTimeout(() => URL.revokeObjectURL(enlace.href), 1000);
}

if (btnCompartir) {  // en la portada no hay botón: no hacemos nada
    const resumen = JSON.parse(btnCompartir.dataset.resumen);  // data-resumen -> objeto
    btnCompartir.hidden = false;  // ya hay JS que lo atienda: lo enseñamos
    btnCompartir.addEventListener("click", async () => {
        const lienzo = await dibujarResumen(resumen);
        lienzo.toBlob((blob) => {  // el dibujo, convertido en un archivo PNG en memoria
            const archivo = new File([blob], "mi-resumen-steam.png", { type: "image/png" });  // el PNG como archivo
            // ¿Este navegador sabe compartir archivos? (móviles, sí). "?." = "si existe": sin canShare, da falso
            if (!navigator.canShare?.({ files: [archivo] })) return descargar(blob);  // PC: se descarga
            // Menú de compartir del móvil (WhatsApp, Instagram...). Si falla, descargamos, salvo que lo hayas
            // cancelado tú (AbortError). Puede fallar si dibujar tardó mucho: el navegador solo deja compartir
            // justo después de un toque, y antes esperamos a la fuente y a la carátula
            navigator.share({ files: [archivo] }).catch((e) => { if (e.name !== "AbortError") descargar(blob); });
        }, "image/png");
    });
}
