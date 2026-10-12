# 🔐 Checklist de seguridad - Steam Optimizer

Principio base: **los datos que no se guardan no se pueden filtrar.**
La app solo consulta datos públicos de Steam y no almacena nada del usuario.

## Ahora (setup del proyecto)
- [x] `.env` está en `.gitignore` antes del primer commit
- [x] `venv/` está en `.gitignore`

## Al conectar con la API de Steam
- [x] La API key vive solo en `.env` (nunca en el código ni en JavaScript del navegador)
- [x] Existe un `.env.example` con los nombres de las variables, sin valores reales
- [x] Todas las llamadas a Steam las hace Flask (servidor), no el navegador
- [x] No se guarda ningún dato del usuario (sin base de datos, sin logs con Steam IDs)
- [x] Los errores de `requests` se capturan para que la URL (con la API key) no salga en mensajes
- [x] Revocada la API key expuesta en una conversación y generada otra

## Al crear el formulario
- [x] Se valida la entrada: Steam ID de 17 dígitos (falta aceptar nombre de perfil, si se añade)
- [x] Nunca se piden contraseñas de Steam
- [x] Se mantiene el escapado automático de Jinja2 (no usar `|safe` con datos externos)
- [x] Mensajes de error genéricos, sin detalles internos
- [ ] Revisar la ruta temporal `/demo` y borrarla antes de publicar
- [x] Google Fonts: la fuente Press Start 2P se aloja en `static/fonts/` y se carga con
  `@font-face`; el navegador del visitante ya no contacta con Google
- [x] Carátulas (decisión aceptada): el navegador las pide directamente al CDN público de
  Steam (`cdn.cloudflare.steamstatic.com`). No lleva API key; Valve ve la IP del visitante
  y qué carátulas se piden. Alternativa más estricta (proxy en Flask) descartada por ahora

## Biblioteca familiar (fase 3)
- [x] IDs de familiares validados en el servidor: 17 dígitos, máx. 5, sin duplicados ni tu propio ID
- [x] Mensajes de error y avisos sin IDs: usan el nombre de Steam o "Familiar N"
- [x] Nunca se piden tokens de sesión de Steam (`GetSingleGamePlaytime` e `IFamilyGroupsService`
  descartados: exigirían una credencial que da acceso a la cuenta)
- [x] Los nombres de Steam (dato externo) se muestran con el escapado de Jinja2; el color del
  dueño usa un número (`dueno-N`), nunca el nombre dentro de una clase o atributo

## Géneros (fase 3)
- [x] Los géneros se piden a la tienda de Steam (`store.steampowered.com/api/appdetails`, no oficial)
  desde Flask (servidor), sin API key y con `timeout` de 10 s
- [x] Caché en memoria solo con datos del JUEGO (`appid` -> géneros), nunca del usuario; se vacía al
  reiniciar el servidor y las consultas fallidas no se guardan
- [x] Límite de la tienda (~200 peticiones cada 5 min): solo el top 10 de cada persona, sin repetir
  juegos; si Steam no responde (p. ej. 429) se muestra "Sin datos", sin detalles internos
- [x] Los géneros (dato externo) se muestran con el escapado de Jinja2; los `style="--i: N"` de las
  barras solo llevan números calculados por nosotros, nunca texto externo

## Qué jugar (paso 4)
- [x] Géneros, nº de reseñas (`appdetails`) y % de positivas (`appreviews`) se piden desde Flask, sin
  API key y con `timeout` de 10 s; caché solo con datos del JUEGO; las consultas fallidas no se guardan
- [x] Presupuesto por visita para no saturar Steam: 20 pendientes + 10 abandonados + 15 notas nuevas
- [x] El `appid` se fuerza a número (`int`) antes de meterlo en la URL de `appreviews`
- [x] Nombres de juegos y bios (llevan el nombre dentro) se pintan con Jinja2 (escapado automático);
  probado con un nombre malicioso (`<script>...`, `onerror=`): sale como texto
- [x] Enlaces a la tienda con `target="_blank" rel="noopener noreferrer"`: Steam no puede tocar
  nuestra pestaña ni recibe nuestra URL (que lleva los Steam IDs)
- [x] Las fichas de Steam Match y de "¿Te atreves?" las pinta el servidor; el JavaScript (`match.js`,
  `atreverse.js`) solo muestra u oculta; probado con un nombre y una etiqueta maliciosos
- [x] Etiquetas: API oficial (`IStoreBrowseService/GetItems`, `IStoreService/GetTagList`) desde Flask,
  sin API key, por lotes de 50 con `timeout`; `appid` forzado a número; caché solo de datos del juego;
  un lote fallido no se guarda

## Repaso general (paso 4.3)
- [x] Logs: el servidor de desarrollo escribía en la consola cada petición con su URL, que lleva
  `?steam_id=...`. Silenciado (`werkzeug` a nivel WARNING en `app.py`); probado: el ID ya no aparece.
  OJO al publicar: el servidor de producción (gunicorn, nginx...) tiene sus propios registros de
  acceso; configurarlos para no guardar la URL completa (o pasar a POST, ver abajo)
- [x] Cabeceras de seguridad en cada respuesta (`cabeceras_seguridad` en `app.py`):
  `Content-Security-Policy` (solo scripts propios; imágenes propias y del CDN de Steam; sin plugins;
  sin iframes), `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`.
  `style-src` permite `'unsafe-inline'` por los `style="--i: N"` (solo números nuestros). Regla para el
  futuro: nada de `<script>` ni `onclick=` dentro del HTML (la CSP los bloquearía); todo en `static/js/`
- [ ] Antes de publicar: formulario con `method="post"` para que los IDs no queden en la URL
  (historial del navegador y registros del hosting)

## Qué comprar (paso 5)
- [x] Búsquedas en la tienda (`IStoreQueryService/Query`) desde Flask, sin API key, con `timeout` de 15 s.
  A Steam solo se le envían etiquetas ("Roguelike", "Terror"...) y filtros, nunca Steam IDs ni la librería
- [x] Caché en memoria de 3 h solo con datos de la TIENDA (búsqueda -> juegos); las entradas caducadas se
  borran al guardar otra (la memoria no crece sin fin) y las consultas fallidas no se guardan
- [x] Coste por visita: 3 búsquedas (en caché 3 h) + 1 de la tragaperras de la tienda (sin caché)
- [x] Juegos adultos fuera de las recomendaciones de compra y de la tragaperras (etiquetas sexuales
  entre sus 5 más votadas); tampoco se recomienda lo que ya tenéis tú o tu familia
- [x] Nombre, precio, estudio y etiquetas (datos externos) se pintan con Jinja2 (escapado automático);
  probado con un nombre malicioso. El `style="--temblor: Npx"` de las ofertas solo lleva un número
  calculado por nosotros; el `appid` va en las URLs solo si es un número entero (también en el JS)

## JavaScript del navegador
- [x] El JavaScript no llama a Steam ni a ninguna otra web (solo usa datos ya presentes en la página)
- [x] Los datos se pasan de Jinja2 a JavaScript solo con `|tojson` (escapa `<`, `>`, `'`, `&`)
- [x] El JavaScript escribe en la página solo con `textContent`, nunca con `innerHTML`; los elementos
  nuevos (menú, cabeceras-botón, letra del neón) se crean con `createElement` y nodos de texto
- [x] Scripts propios en `static/js/` (sonido, efectos, carga, logros, match, atreverse, ruleta,
  navegacion, libreria): nada de `<script>` ni `onclick=` dentro del HTML (lo bloquearía la CSP)
- [x] El JavaScript no guarda nada (ni `localStorage` ni cookies): sonido, modo CRT, contadores y logros duran
  solo la visita
  (el sonido encendido pasa a la siguiente página como `?sonido=1` en la URL; Flask lo ignora)

## Antes de publicar
- [ ] Quitar o generalizar las comparaciones con bromas sobre personas reales (`analysis.py`)
- [ ] Revisar el tono de las bromas de "tu mamá" (pensadas para amigos)
- [ ] Clips ORIGINALES de JoJo en `static/sonidos/` (decisión del usuario, solo uso privado): tienen derechos
  de autor. Si la web se publica para uso comercial (o se abre al público), quitarlos y sustituirlos por los
  respaldos sintetizados o por sonidos con licencia libre. Están en `.gitignore`: no subirlos nunca a un repo
  público. El resto de efectos no usa imágenes, gifs ni música con derechos (el modo caos es un tema original)
- [ ] Límite de la tienda con muchos visitantes: todas las consultas salen de la IP del servidor
  (una visita nueva puede costar ~70 consultas + 4 de la tienda); valorar acotar peticiones por
  visita/minuto o el tamaño de las cachés
- [ ] Personalización de frases: quitar las bios satíricas (vivienda, capitalismo, fondos buitre) y revisar
  todas las frases de broma (ver roadmap en `CLAUDE.md`)
- [ ] `debug=False` en producción
- [ ] HTTPS activo en el hosting
- [ ] Dependencias actualizadas (`pip list --outdated`)
- [ ] Nota de privacidad visible: "No almacenamos ningún dato. Solo consultamos tu perfil público de Steam"
- [ ] Repaso del historial de Git: ninguna clave subida por error (si ocurre, regenerarla)

## Si en el futuro se añade login
- [ ] Usar "Sign in through Steam" (OpenID); nunca gestionar contraseñas propias
