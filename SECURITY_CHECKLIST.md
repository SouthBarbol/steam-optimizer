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

## JavaScript del navegador
- [x] El JavaScript no llama a Steam ni a ninguna otra web (solo usa datos ya presentes en la página)
- [x] Los datos se pasan de Jinja2 a JavaScript solo con `|tojson` (escapa `<`, `>`, `'`, `&`)
- [x] El JavaScript escribe en la página solo con `textContent`, nunca con `innerHTML`

## Antes de publicar
- [ ] Quitar o generalizar las comparaciones con bromas sobre personas reales (`analysis.py`)
- [ ] Revisar el tono de las bromas de "tu mamá" (pensadas para amigos)
- [ ] Sin imágenes, gifs ni música con derechos de autor (p. ej. referencias a JoJo: solo texto y Web Audio)
- [ ] Límite de la tienda con muchos visitantes: todas las consultas salen de la IP del servidor;
  valorar acotar peticiones por visita/minuto o el tamaño de la caché
- [ ] `debug=False` en producción
- [ ] HTTPS activo en el hosting
- [ ] Dependencias actualizadas (`pip list --outdated`)
- [ ] Nota de privacidad visible: "No almacenamos ningún dato. Solo consultamos tu perfil público de Steam"
- [ ] Repaso del historial de Git: ninguna clave subida por error (si ocurre, regenerarla)

## Si en el futuro se añade login
- [ ] Usar "Sign in through Steam" (OpenID); nunca gestionar contraseñas propias
