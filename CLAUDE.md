# Steam Optimizer

Web app en Python (Flask) que consulta la Steam Web API, analiza la librería
pública de un usuario y recomienda qué jugar (de su librería) y qué comprar
(juegos similares a sus géneros y horas más jugadas).

Es un proyecto de aprendizaje: el objetivo es aprender Python, Flask, GitHub y
a trabajar con Claude Code.

## Cómo quiero que trabajes

* Responde en español.
* Soy principiante en Python y estoy algo oxidado con Git. Explica cada concepto nuevo con brevedad. Justifica tu decisión con cada paso que vayamos a dar
* Antes de modificar archivos, cuéntame qué vas a cambiar y por qué.
* Avanza en pasos pequeños, uno cada vez. No hagas varias tareas a la vez.
* No reescribas archivos enteros si basta con un cambio puntual.
* Si hay varias formas de hacer algo, propón la más simple.
* No añadas librerías nuevas sin preguntarme.
* Optimiza el uso de tokens
* Añade comentarios al código explicando que hace cada linea, función,método, ...

## Entorno

* Windows 11 y VS Code.
* Entorno virtual en `venv/` (activar con `.\\venv\\Scripts\\Activate.ps1`).
* Dependencias: flask, requests, python-dotenv (ver `requirements.txt`).
* Control de versiones con Git y GitHub Desktop. No hagas commits ni push
sin que yo lo pida.

## Estructura

```
steam-optimizer/
├── app.py              # servidor Flask: rutas, validación y orquestación (pedir_*), cabeceras de seguridad
├── steam_client.py     # capa de integración: TODAS las llamadas a Steam y sus cachés en memoria
├── analysis.py         # capa de lógica: cálculos puros (estadísticas, qué jugar, qué comprar, frases)
├── templates/index.html
├── static/css/style.css, static/fonts/ (Press Start 2P), static/sonidos/ (clips privados, en .gitignore)
├── static/js/          # sonido, efectos, carga, logros, match, atreverse, ruleta (tragaperras),
│                       # navegacion (menú y cohete), libreria (buscar/ordenar/HIGH SCORES)
├── ALGORITMO.md        # cómo recomiendan "qué jugar" y "qué comprar" (mantenerlo al día)
├── .env / .env.example, requirements.txt, README.md, SECURITY_CHECKLIST.md
```

## Seguridad (prioridad alta)

Principio: los datos que no se guardan no se pueden filtrar.

* No guardar datos de usuarios: ni Steam ID, ni librería, ni estadísticas. Sin base de datos.
* La API key de Steam solo vive en `.env`, nunca en el código ni en el JavaScript del navegador.
* Nunca escribas, muestres ni pegues claves reales. Usa `.env.example` para documentar variables.
* Todas las llamadas a Steam las hace Flask (servidor), no el navegador.
* Validar la entrada del usuario (Steam ID de 17 dígitos o nombre de perfil con caracteres permitidos).
* No pedir nunca contraseñas de Steam.
* Mantener el escapado automático de Jinja2 (no usar `|safe` con datos externos).
* `debug=False` y HTTPS antes de publicar.
* Sigue y actualiza `SECURITY\_CHECKLIST.md` según avancemos.

## Arquitectura

Monolito sencillo por capas, renderizado en el servidor, sin base de datos.
(Sujeta a cambios futuros según necesitemos.)

Flujo:
Navegador (formulario con Steam ID)
  -> Capa de presentación: rutas de Flask y plantillas Jinja2.
     Valida la entrada y muestra el resultado.
  -> Capa de lógica: análisis de horas, géneros y recomendaciones.
     Funciones puras: reciben datos y devuelven datos, sin Flask ni red.
  -> Capa de integración: cliente de la Steam Web API (requests).
  -> Steam Web API

Transversal: configuración (.env leído con python-dotenv).

Reglas:
- La lógica no importa Flask ni hace peticiones HTTP.
- Solo la capa de integración conoce la API key y las URLs de Steam.
- La validación de la entrada ocurre en la capa de presentación.
- No se guardan datos de usuarios. No hay base de datos.
- No se registran (log/print) Steam IDs ni librerías de usuarios.

Evolución prevista:
- Fase 2: todo en steam_service.py.
- Fase 3 (paso 3.1, HECHO): `steam_service.py` renombrado a `steam_client.py`
  (solo habla con Steam); `unir_juegos` y `unir_familia` movidas a `analysis.py`.

## Estado actual

Fases 1 y 2 completadas (repo, venv, Steam Web API, librería en el navegador). Fase 3 casi terminada:
todo lo de abajo está HECHO y probado por el usuario en el navegador (y con commit), salvo lo que se indique.

* Biblioteca familiar (hasta 5 IDs, sin duplicados, dueños con nombre y color), estadísticas por persona
  (Pile of Shame, abandonados, horas en perspectiva, duelo familiar), carátulas, géneros con caché,
  perfil gamer, estadísticas de Stand (hexágono).
* Capa de personalidad (3.6): `sonido.js` (SFX sintetizados, 🔇 empieza silenciado, `?sonido=1` para
  mantenerlo), `efectos.js` (pato, trombón, terremoto, caos manual/Konami, pantallazo azul, DVD,
  cascarrabias, glitch, 7 referencias a JoJo), `carga.js` (99 % con excusas de "tu mamá"), `logros.js`
  (`desbloquear(id)`; catálogo `LOGROS` en `analysis.py`, 24 logros). Clips de JoJo y `ay-ay-ay.mp3` en
  `static/sonidos/` (en .gitignore; si faltan, suenan los sintetizados).
* Paso 4, qué jugar (detalle en `ALGORITMO.md`): 💘 Steam Match (`match.js`, ❌/💚 con confeti y
  logros piedra/enamoradizo), 🧭 ¿Te atreves? (territorio inexplorado, logro sinmiedo), 🎰 ruleta del caos
  (toda la librería con frase; absorbió al "juego sorpresa": cascarrabias, Dio, ORA/MUDA y logro
  Ludópata cuelgan de `#ruleta-otra`/`#ruleta-dio`).
* Paso 5, qué comprar (detalle en `ALGORITMO.md`): `buscar_tienda` y `tienda_al_azar` en
  `steam_client.py` (`IStoreQueryService/Query`, sin API key, caché 3 h); en `analysis.py`
  `tus_etiquetas` (amplias a mitad de peso, avisos de contenido fuera), `mezclas_raras`, `que_comprar`
  (6 mainstream + 6 bizarras; sin lo que tenéis, sin adultos, máx. 1 gratis y 1 por desarrolladora) y
  `tragaperras_tienda`; `pedir_compra` en `app.py`; sección 🛒 con macro `ficha_compra` y tragaperras
  amarilla de la tienda (`ruleta.js` = `montarTragaperras` para toda `.tragaperras`).
  5.5: jackpot (≥ 95 %: monedas `.flotante.cae`, `SFX.jackpot`) y gatillazo (< 40 %: trombón) en la
  tragaperras de la tienda (campos `premio`/`antiguo` de `tragaperras_tienda`); palanca en ambas tragaperras
  (`SFX.palanca`, llama a "Otra"); glitch `tele-rota` en las bizarras (al pasar el ratón y 15 % cada 8 s);
  logros Jackpot, Arqueólogo (< 2005) y Gusto raro (abrir una bizarra).
* 5.6, ☣️ El rincón de la pesturria (por dentro se llama `malisimo`): `mas_vendidos()` en
  `steam_client.py` (5 páginas de 1.000 con `sort` 11, caché 24 h, ~13 s la primera visita del día;
  sin nombres de etiquetas devuelve None para no colar adultos); `malisimos()` en `analysis.py` (< 40 %
  positivas y ≥ 500 reseñas, mismos filtros que comprar; hoy salen ~29) con `PLANTILLAS_MALISIMO` (frases
  "de bar" al gusto del usuario); `malo=` en `app.py` (con la variable `tuyos` compartida); sección roja
  `#malisimo` en la plantilla, que es una `.tragaperras` más (giro, palanca y "Otra" sin JS nuevo), con
  moscas 🪰 (CSS + `SFX.zumbido` al pasar el ratón) y precinto "PELIGRO · NO JUGAR"; logros Estómago
  de hierro (abrir una) y Catador de pesturria (10 distintas, contadas en `ruleta.js`). 24 logros.
* "To Be Continued" de JoJo solo en la página de resultados (antes salía nada más entrar en el inicio).
* Fase de estética (CERRADA): espaciado con variables `--hueco-seccion`, `--hueco-tarjetas`, `--relleno`;
  menú fijo `[data-menu]` + cohete 🚀 (`navegacion.js`); librería plegable con buscador, orden y HIGH
  SCORES (`libreria.js`, medallas `podio-1..3`, horas que cuentan); corazones ❤️🖤 y ofertas que
  tiemblan; neón estropeado, botones `.arcade` con `SFX.clack`, modo CRT 📺 (`html.crt body::after`).
  Descartado por el usuario: telarañas/sepia, precios en unidades absurdas, fichas 3D (E5).

## Decisiones y limitaciones vigentes

* Préstamos de la familia: la API solo da tus horas si los jugaste en las últimas 2 semanas; si no, "—"
  (desconocido, no 0). Por eso Steam Match puede recomendar un préstamo que ya jugaste. Descartados
  `IFamilyGroupsService` y `GetSingleGamePlaytime` (exigen token de sesión: riesgo de robo de cuenta).
* APIs no documentadas aceptadas (`appdetails`, `Query` con `sort` deducido: 10 = populares,
  21 = valorados, 11 = más vendidos de siempre; el 22 es "peor valorados" pero empieza por miles de juegos
  con 0 % y casi sin reseñas, inútil; `Query` ignora filtros desconocidos y no filtra por reseñas),
  vigilando límites. SteamSpy descartado. Logros completados de Steam descartados (coste).
* Juegos adultos excluidos de lo que se recomienda comprar (la página la puede ver la familia).
* Tono de los textos: humano, de colega; humor bizarro. NADA de alquileres, vivienda, Euríbor ni
  capitalismo (al usuario no le gustan y "se notan escritas por una IA").
* Sin imágenes, gifs ni música con derechos en el repo; sin `localStorage` ni cookies.

## Cómo trabajar y probar

* Proponer el código de cada sub-paso antes de escribirlo; un paso cada vez.
* Recordar reiniciar el servidor (Ctrl+C y `python app.py`) tras cambiar `.py` o plantillas (con
  `debug=False` no recarga solo); el CSS y el JS se ven con Ctrl+F5.
* Pruebas en scripts `prueba_*.py` del scratchpad (se pierden al cerrar la sesión; rehacerlos si hacen
  falta): datos falsos + `app.app.test_client()`, sustituyendo TODAS las funciones de Steam de `app`
  (`get_owned_games`, `get_recently_played_games`, `get_player_names`, `get_genres_varios`, `get_tags`,
  `get_valoraciones` (devuelve `{appid: {"total", "pct"}}`), `buscar_tienda`,
  `tienda_al_azar`, `mas_vendidos`; si falta esta última, la prueba llama a Steam de verdad y tarda). Ojo: un nombre malicioso escapado contiene el texto "onerror=".
* El usuario permitió usar su Steam ID para probar con su librería real; no apuntarlo en archivos.
* No hay Node instalado: el JavaScript no se puede comprobar en terminal; probarlo en el navegador.
* Modelo: Opus, effort high.

## Roadmap restante (en orden)

1. ~~5.5~~ y ~~5.6~~ HECHOS (efectos de "¿Qué comprar?" y rincón de la pesturria). Paso 5 cerrado.
2. ~~Etiquetas en vez de géneros~~ HECHO (falta que el usuario lo pruebe en el navegador y haga commit).
   2a: `perfil_gamer` usa la n.º 1 de `tus_etiquetas` (toda la librería jugada; "Comedia" vale), `PERFILES`
   con 30 etiquetas (nombres exactos: "Tipo «Dark Souls»", "Construcción de barajas") y
   `PERFILES_GENERICOS`. 2b: Steam Match con `que_cuentan` + `tus_etiquetas`; reseñas en el lote de
   `get_tags` (`include_reviews`, `get_valoraciones`); borrados presupuestos, finalistas, `get_valoracion`,
   `get_resenas`, `en_cache`; variedad por las 3 etiquetas principales (`MAX_IGUALES` = 1); anti-gustos
   15 % / 10 %. Siguen con géneros (solo el top 10 de cada persona): barras, Alcance y pegatina INDIE
   (la etiqueta "Indie" se probó y falla 1 de cada 4). Detalle en `ALGORITMO.md`.
3. ~~Optimizaciones~~ HECHO. 3.1 HECHO: `mas_vendidos` pide sus 5 páginas a la vez (`ThreadPoolExecutor`, cerrojo
   `_cerrojo_vendidos` para que dos visitas no la rellenen a la vez, semáforo global `_semaforo_steam` de
   `MAX_A_LA_VEZ` = 5; los hilos no escriben nada compartido, solo devuelven). En frío: 20 s -> 12 s.
   Steam reordena ~40 de los 5.000 entre consultas (no es fallo de los hilos). El usuario pide cuidado
   con la concurrencia (cerrojos, semáforos). 3.2 HECHO: `get_genres_varios` (hilos + mismo semáforo;
   `_cerrojo_generos` en cada lectura/escritura de la caché, la petición fuera del cerrojo; aceptado que
   2 visitas simultáneas puedan pedir el mismo juego dos veces). 50 géneros: 15,4 s -> 3,7 s. Solo tú, en
   frío: 12 s -> 9,4 s (el usuario medía 23,8 s con 4 familiares antes del 3.2).
   Con familia (usuario, pestaña Red): 23,8 s -> 15,2 s. 3.3 HECHO: `en_paralelo(funcion, elementos)` en
   `steam_client.py` (genérica, con el semáforo; la función no escribe nada compartido ni anida otra
   `en_paralelo` -> deadlock); `datos_familiar` en `app.py`, y `pedir_familia` monta las listas en el hilo
   principal (con familia: 15,2 -> 14,1 s). 3.4 HECHO: lotes de `get_tags` con `en_paralelo`
   (`_pedir_lote_etiquetas` devuelve, `get_tags` escribe con `_cerrojo_etiquetas`; `_cerrojo_nombres` en
   `_cargar_nombres_etiquetas`). Con familia (cronómetro del scratchpad, 412 juegos en 9 lotes): get_tags
   4,2 -> 0,8 s; en frío 14,6 -> 11,3 s; segunda visita ~5 s. 3.5 HECHO: `buscar_en_tienda` + `en_paralelo`
   en `pedir_compra`; `_cerrojo_tienda` en `buscar_tienda` (la limpieza recorría la caché sin cerrojo: riesgo
   teórico, no se pudo reproducir). Con familia: en frío 9,8 s, segunda visita 3,7 s (antes del paso 3:
   23,8 s; el usuario mide ~11 s en el navegador). PASO 3 CERRADO (falta commit). Descartado: solapar
   secciones enteras (~3 s más, código complejo y riesgo de deadlock con el semáforo). Idea para el paso 5:
   precalentar la caché al arrancar (hilo en segundo plano: `mas_vendidos` y nombres de etiquetas). (la primera visita tarda; `mas_vendidos` hace 5
   consultas seguidas, ~13 s, una vez al día); acotar consultas por visita.
4. **EMPEZAR AQUÍ**. Personalización de frases (antes de publicar): rehacer todas las de broma (`BIOS_*`, `BIOS_ATREVIDO`,
   `PLANTILLAS_RULETA`, `PLANTILLAS_TIENDA`, textos de logros, `PERFILES`) con humor bizarro, al estilo de
   `PLANTILLAS_MALISIMO` (exageración burra + confesión absurda, que al usuario SÍ le gusta); quitar las de
   alquileres/vivienda/capitalismo; quitar o generalizar las bromas sobre personas reales (Calero, Mauri,
   Navarro) en `analysis.py`; revisar el tono de "tu mamá". Proponerlas antes.
5. Publicar: borrar `/demo`, formulario con POST, HTTPS, repasar `SECURITY_CHECKLIST.md` ("Antes de
   publicar"), elegir hosting y cómo guardar allí la API key. Opcional: formulario más cómodo para los
   IDs familiares y favicon (hoy 404).
