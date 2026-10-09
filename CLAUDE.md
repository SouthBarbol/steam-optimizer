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
├── steam\_service.py    # llamadas a la Steam API y análisis
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
- Al crecer: separar steam_client.py (habla con Steam) y analysis.py (calcula).

## Estado actual

Fase 1 completada: repo en GitHub, clonado, venv, dependencias instaladas,
`.gitignore`, `README.md`, `SECURITY\_CHECKLIST.md`.

Fase 2 (en curso): conectar con la Steam Web API (`GetOwnedGames`) y mostrar
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
* Sugerir cambiar a Opus al llegar al análisis de géneros/horas y
  recomendaciones.

## Fase 3 (plan acordado, por empezar)

Idea central: de la enorme librería (gran parte es de la familia), recomendar
qué jugar. Lo más importante es el sistema de recomendaciones; debe basarse
en hechos (horas, géneros, datos reales), no en suposiciones. Se irá validando
si la lógica es correcta según se construya. Sugerir cambiar a Opus aquí.

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
2. Carátulas en la tabla (URL pública a partir del `appid`).
3. Géneros con caché en memoria (por `appid`, datos del juego, no del usuario),
   gráfico de horas por género y perfil gamer. Solo pedir el top por horas.
4. Qué jugar: puntuación por géneros y horas, con pendientes.
5. Qué comprar: mainstream y bizarras, con precio y descuentos.
Probablemente separar `steam_client.py` y `analysis.py` al llegar al paso 3.

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
y publicación.

