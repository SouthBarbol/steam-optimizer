# Steam Optimizer

Web app en Python (Flask) que consulta la Steam Web API, analiza la librería
pública de un usuario y recomienda qué jugar (de su librería) y qué comprar
(juegos similares a sus géneros y horas más jugadas).

Es un proyecto de aprendizaje: el objetivo es aprender Python, Flask, GitHub y
a trabajar con Claude Code.

## Cómo quiero que trabajes

* Responde en español.
* Soy principiante en Python y estoy algo oxidado con Git. Explica cada concepto nuevo con brevedad.
* Antes de modificar archivos, cuéntame qué vas a cambiar y por qué.
* Avanza en pasos pequeños, uno cada vez. No hagas varias tareas a la vez.
* No reescribas archivos enteros si basta con un cambio puntual.
* Si hay varias formas de hacer algo, propón la más simple.
* No añadas librerías nuevas sin preguntarme.
* Optimiza el uso de tokens

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

## Estado actual

Fase 1 completada: repo en GitHub, clonado, venv, dependencias instaladas,
`.gitignore`, `README.md`, `SECURITY\_CHECKLIST.md`.

Fase 2 (siguiente): crear `.env` y `.env.example`, conectar con la Steam Web API
(`GetOwnedGames`) en `steam\_service.py` y mostrar la librería de un usuario.

## Después

Análisis de géneros y horas, recomendaciones, formulario web y publicación.

