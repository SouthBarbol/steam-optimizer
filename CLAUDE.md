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

## Estructura prevista

```
steam-optimizer/
├── app.py              # servidor Flask
├── steam_client.py     # capa de integración: llamadas a Steam (antes steam_service.py)
├── analysis.py         # capa de lógica: cálculos puros
├── templates/          # HTML
├── static/css, js/     # estilos y scripts
├── .env                # secretos (NO se sube a Git)
├── .env.example        # nombres de variables, sin valores
├── requirements.txt
├── README.md
└── SECURITY\_CHECKLIST.md
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

Fase 1 completada: repo en GitHub, clonado, venv, dependencias instaladas,
`.gitignore`, `README.md`, `SECURITY\_CHECKLIST.md`.

Fase 2 completada: conectar con la Steam Web API (`GetOwnedGames`) y mostrar
la librería de un usuario.
* Hecho: `.env` y `.env.example` creados; `steam\_service.py` con
  `get\_owned_games(steam_id)`.
* Hecho también: `steam\_service.py` captura los errores sin exponer la API key
  y está comentado línea a línea; `app.py` creado (ruta `/?steam_id=...`,
  valida 17 dígitos, muestra juegos ordenados por horas).
* Hecho además: plantilla `templates/index.html` (Jinja2) y estilo gamer en
  `static/css/style.css` (fuente Press Start 2P de Google Fonts). Ruta temporal
  `/demo` con juegos inventados para ver la página sin API key (probada, se ve bien);
  BORRARLA antes de publicar. `SECURITY\_CHECKLIST.md` actualizado.
* Hecho: API key nueva generada y puesta en `.env`; el problema del 401 está
  resuelto. Probado `get_owned_games` desde terminal (95 juegos) y `app.py` en
  el navegador (`/?steam_id=...`, incluida la validación): funciona.
* Hecho: juegos de biblioteca familiar. `get_owned_games` usa
  `include_played_free_games=1` (95 -> 102 juegos), se añadió
  `get_recently_played_games` y `unir_juegos` (sin duplicados, marca
  `propio`), y `index.html` muestra la etiqueta "Familia" en los no propios.
* LIMITACIÓN conocida: la API oficial solo expone los juegos prestados
  (biblioteca familiar) si se han jugado en las últimas 2 semanas
  (`GetRecentlyPlayedGames`); no hay historial completo. La vía no oficial
  (`IFamilyGroupsService`) exige un token de sesión personal y se descartó
  por seguridad. Documentar también en el README.
  Probado también `IPlayerService/GetSingleGamePlaytime`: da 403 (exige token
  de sesión del usuario, no basta la API key). Pedir el token se descartó
  (riesgo de robo de cuenta, parece phishing, términos de Valve). Limitación
  DEFINITIVA: en juegos prestados no jugados en 2 semanas mostramos "—" (dato
  desconocido), no 0.
* Hecho: Google Fonts resuelto. La fuente Press Start 2P se aloja en
  `static/fonts/` (`@font-face` en `style.css`); ya no hay peticiones a Google.
* Pendiente: borrar la ruta `/demo` antes de publicar. (Opcional: añadir
  un favicon; hoy `favicon.ico` da 404, es inofensivo.)

## Próxima sesión (empezar aquí)

* Fase 3 en curso: pasos 0, 1, 2 y sub-pasos 3.1-3.4 HECHOS y probados por el usuario en el navegador.
* Paso 3.5 HECHO (checklist y README al día). Siguiente: **3.6** (capa de personalidad),
  ver "Fase 3". Optimizaciones (p. ej. consultas de géneros en paralelo) al final, con el resultado
  completo. Proponer primero el código de cada sub-paso, como siempre.
* Modelo: Opus. Para el paso 3 (géneros, caché) y siguientes, effort high
  (comprobar que el usuario lo ha subido).
* Recordar al usuario reiniciar el servidor (Ctrl+C y `python app.py`) tras
  cambiar `.py` o plantillas: con `debug=False` Flask no recarga solo (el CSS
  y el JS sí se ven con Ctrl+F5).
* Pruebas: con datos falsos sustituyendo `app.get_owned_games`, etc. por
  lambdas y usando `app.app.test_client()`; scripts de prueba en el scratchpad
  (no en el repo). Para no ver Steam IDs reales, el usuario prueba con los suyos
  en el navegador.

## Fase 3 (plan acordado, en curso)

Idea central: de la enorme librería (gran parte es de la familia), recomendar
qué jugar. Lo más importante es el sistema de recomendaciones; debe basarse
en hechos (horas, géneros, datos reales), no en suposiciones. Se irá validando
si la lógica es correcta según se construya.

Recomendaciones: dos estilos, **mainstream** (populares, afines a tus géneros)
y **bizarras** (raras o poco convencionales pero relacionadas con tus gustos).

Biblioteca familiar: la librería familiar = unión de las librerías de los
miembros. El formulario pedirá el Steam ID propio y, opcionalmente, los de
familiares (hasta ~5, separados por comas; se escriben cada vez, no se guardan).
Cada miembro necesita perfil y detalles de juegos públicos. Se marca de quién
es cada juego. Limitación: no se sabe qué juegos el editor excluye del
préstamo. Se descartó el endpoint no oficial con token de sesión (seguridad).

Orden de trabajo (un paso cada vez):
0. Biblioteca familiar con varios IDs en el formulario (validar cada ID).
   Sin duplicados: un juego aparece una vez con la lista de todos sus dueños.
   HECHO: dueños con su nombre de Steam (`get_player_names`, una llamada a
   `GetPlayerSummaries`; si falla, "Tú"/"Familiar N"; nombres repetidos llevan
   "(N)"), un color por dueño, horas con un decimal y "—" si se desconocen.
1. Estadísticas con datos ya disponibles: Pile of Shame (% con 0 h), juegos
   abandonados (<2 h), horas en perspectiva, juego sorpresa (aleatorio entre
   pendientes) y duelo familiar (ranking de juegos y horas).
   HECHO: `analysis.py` (capa de lógica), una tarjeta por persona con su color,
   comparaciones bizarras, juego sorpresa con botón "Otro" en JS
   (`static/js/sorpresa.js`, sin llamar a Steam) y duelo familiar (horas,
   colección, favoritos; incluye recientes de cada familiar).
2. Carátulas en la tabla (URL pública a partir del `appid`).
   HECHO: `preparar_juegos` pasa el `appid`; `<img class="caratula">` en la celda
   "Juego" con `header.jpg` del CDN de Steam (`loading="lazy"`, sin imagen en /demo).
   El navegador pide las imágenes a Steam directamente (decisión aceptada y
   anotada en `SECURITY_CHECKLIST.md`; proxy en Flask descartado por ahora).
3. Géneros con caché en memoria (por `appid`, datos del juego, no del usuario),
   gráfico de horas por género y perfil gamer. Solo pedir el top por horas.
4. Qué jugar: puntuación por géneros y horas, con pendientes.
5. Qué comprar: mainstream y bizarras, con precio y descuentos.
Paso 3 acordado: géneros de Steam Store `appdetails` (`l=spanish`, sin key);
caché en memoria {appid: géneros} sin guardar fallos; horas COMPLETAS de cada juego
a cada uno de sus géneros (los % no suman 100, avisarlo); gráfico con barras CSS;
perfil gamer con frases-plantilla. Para TODOS los perfiles (tú y cada familiar),
top `TOP_GENEROS = 10` por persona, appids sin repetir; mostrar % de horas que cubre
el top; si Steam limita (429) -> "Sin datos" y aviso.
Sub-pasos: 3.1 separar `steam_client.py` (HECHO) · 3.2 `get_genres(appid)` + caché
en `steam_client.py` (HECHO; devuelve lista, `[]` si el juego no tiene ficha, `None`
si falla la consulta, que no se guarda en caché) ·
3.3 `top_jugados`, `horas_por_genero` y `perfil_gamer` en `analysis.py` (HECHO y
probado con datos falsos). "Indie" NO decide el perfil (`NO_DEFINEN_PERFIL`), va como
pegatina: en el perfil si supera `UMBRAL_INDIE` = 50 % de las horas del top, y en la
tabla en cada juego con género Indie (comprobación pendiente en 3.4) ·
3.4 app + plantilla (HECHO: `pedir_generos` en `app.py`; pegatina INDIE en tabla y perfil, solo
en juegos del top de alguien; aviso de carga + bloques animados con `static/js/carga.js`, base de la
carga 99 % del 3.6; logro en cuadro RPG, sello INDIE y barras de 10 bloques solo CSS con macro
`barra`, 5 visibles + plegable `<details>`; texto letra a letra, confeti y sonidos pasan al 3.6), con estilo elegido A + C (A: barras "de vida" de 10 bloques que se
rellenan con "blip" y perfil en cuadro de diálogo RPG con texto letra a letra; C: perfil
revelado como "logro desbloqueado" con destello, confeti y pegatina Indie como sello).
Página de muestra con datos inventados (fuera del repo):
`<scratchpad>/muestra/muestra.html` (si no existe en una sesión nueva, rehacerla) ·
3.6 (NUEVO) capa de personalidad: `static/js/efectos.js` y `sonido.js` propios (Web
Audio API, sin archivos ni librerías), botón 🔇 que empieza silenciado,
`prefers-reduced-motion`, y efectos bizarros elegidos por el usuario de la muestra
(pato errante, carga 99 %, Pile of Shame con trombón, terremoto, modo caos/Konami,
pantallazo azul, salvapantallas DVD, logros absurdos, tarjeta cascarrabias, juegos
olvidados que lloran, título glitch). Los efectos de los pasos 4 y 5, cuando existan.
Al usuario le gustaron TODOS. Apuntes suyos para el 3.6:
  - Pato: que pase "de vez en cuando" (p. ej. a intervalos aleatorios), no 1 de cada 10 visitas.
  - Modo caos: SOLO manual (botón o Konami), nunca automático; es muy intenso.
  - Carga del 99 %: le encanta. Más énfasis en "preguntando a tu mamá" y añadir "me estoy
    echando a tu mamá". TONO para TODOS los textos: humano, de colega, tontería entre
    amigos (ej.: "Tu mamá dice que es tarde", "Vale, ya. Tu mamá te manda saludos").
  - Logros absurdos: profundizar. Ideas basadas en datos reales (calculados en la visita,
    NO se guardan; nada de localStorage): Coleccionista de polvo (muchos sin jugar), Fiel
    hasta la muerte (un juego >50 % de tus horas), Picaflor (muchos <2 h), Toca césped
    (>1.000 h), Indie hasta la médula, Lobo solitario / Familia numerosa (0 o 5 familiares),
    Insomne (visita de madrugada, hora del navegador), Ludópata del azar ("Otro" 10 veces),
    Paciencia infinita (esperar la carga), Susurrador de patos, Esquina perfecta (DVD),
    Clic compulsivo (cascarrabias), Explorador del abismo (scroll al final). Contador
    "logros X/N" de la visita.
  - Referencias a JoJo (idea del usuario), también en el 3.6:
    · Efectos: ゴゴゴゴ morados flotando alrededor de la tarjeta líder del duelo; "To Be Continued ⟸"
      con sepia (`filter: sepia()`) al final de la tabla o si Pile of Shame > 50 % ("Tus juegos
      pendientes... continuarán"); ZA WARUDO como código secreto (congela animaciones, `filter: invert()`,
      "Toki wo tomare!"); ORA ORA / MUDA MUDA al pulsar "Otro" muchas veces seguidas.
    · Textos: sorpresa "¿Esperabas una recomendación sensata? ¡Pero era yo, Dio!"; cascarrabias
      "Yare yare daze..."; carga 99 % "Tu mamá está usando su Stand para frenar la barra".
    · Estadísticas de Stand (la favorita, datos reales): hexágono con notas A-E en el perfil. Poder =
      horas totales; Velocidad = juegos abandonados/terminados rápido; Alcance = variedad de géneros;
      Persistencia = horas del favorito; Precisión = Pile of Shame bajo; Potencial = pendientes.
      Los umbrales de cada nota se decidirán al implementarlo (cálculo en `analysis.py`).
    · Logro absurdo "¿Es eso una referencia a JoJo?" al encontrarlas todas.
    · SIN imágenes, gifs ni música del anime (p. ej. "Roundabout" tiene derechos); sonidos con Web
      Audio y solo textos/memes ·
3.5 `SECURITY_CHECKLIST.md` y `README.md`.

Extra en pasos 4 y 5: además de las recomendaciones razonadas, un juego
totalmente aleatorio (de la librería en el 4, de la tienda en el 5) con una
descripción bizarra de por qué se recomienda, generada DESPUÉS de elegir el
juego. Método decidido: plantillas de frases absurdas con huecos rellenados
con datos del juego (nombre, género, año...). Sin IA, para evitar costes.
Distinto del "juego sorpresa" del paso 1 (azar solo entre pendientes, sin texto).

Fuentes de datos: Steam Store `appdetails` (no oficial, una llamada por juego,
con límite de peticiones) y/o SteamSpy (etiquetas). Aceptamos usar APIs no
documentadas, vigilando límites de velocidad y posibles cambios.

Descartado: logros completados (coste de recursos: una llamada por juego),
aceptar nombre de perfil y comparar con un amigo. Reconsiderar los logros solo
si sobran recursos.

## Después

Formulario más cómodo para los IDs familiares (idea futura), borrar `/demo`
y publicación. Antes de publicar: quitar o generalizar las comparaciones con
bromas internas sobre personas reales (Calero, Mauri, Navarro) en `analysis.py`, y
revisar el tono de las bromas de "tu mamá" (pensadas para amigos) por si se publica.

