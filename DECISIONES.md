# Registro de decisiones

Cada decisión importante del proyecto: qué se decidió, por qué y qué se descartó.
Sirve para estudiar el proyecto y poder explicarlo. El detalle de cómo se recomiendan
juegos está en `ALGORITMO.md`; la seguridad, en `SECURITY_CHECKLIST.md`.

## Arquitectura

**Monolito por capas, sin base de datos.**
- `app.py` (presentación: rutas, validación, plantillas), `analysis.py` (lógica: funciones
  puras, sin red ni Flask), `steam_client.py` (integración: TODAS las llamadas a Steam y la API key).
- Por qué: es lo más simple de entender y probar. Cada capa tiene una sola responsabilidad y la
  lógica se prueba con datos falsos sin tocar Steam.
- Sin base de datos: "los datos que no se guardan no se pueden filtrar". Solo hay cachés en
  memoria de datos públicos de Steam (géneros, etiquetas, tienda), nunca datos de usuarios.

**Consultas a Steam en paralelo, con un semáforo y cerrojos.**
- `en_paralelo()` lanza varias peticiones a la vez con hilos (`ThreadPoolExecutor`); un
  semáforo (`MAX_A_LA_VEZ` = 5) limita cuántas van a Steam a la vez para no saturarlo; un cerrojo
  por caché evita que dos hilos la escriban a la vez. La red siempre va FUERA del cerrojo.
- Por qué: con 4 personas, la página pasó de 23,8 s a ~10 s en frío y ~3,7 s después.
- Regla: la función que se pasa a `en_paralelo` solo devuelve datos; no escribe nada compartido
  ni lanza otra `en_paralelo` (podría quedarse bloqueada esperándose a sí misma: deadlock).
- Descartado: solapar secciones enteras (poco beneficio, mucho riesgo de deadlock).

## Publicación (paso 5)

**Hosting: Render, plan gratis, región Frankfurt** (2026-10-14).
- Necesidades: gratis, para que 3 amigos la prueben durante varios días.
- Pega aceptada: se duerme tras 15 min sin visitas y tarda ~1 min en despertar; al despertar
  la caché está vacía (la primera visita es más lenta).
- Descartados: GitHub Pages (solo sirve archivos estáticos: no ejecuta Python, y la API key
  quedaría a la vista en el navegador; además Steam no permite llamadas desde navegadores, CORS);
  PythonAnywhere (desactiva los hilos en las webs: `en_paralelo` se colgaría); Vercel y similares
  (sin memoria entre visitas: la caché no sirve); VPS (administrar Linux y su seguridad uno mismo);
  tu PC + túnel (el PC tendría que estar siempre encendido).
- Futuro: si gusta, quizá app móvil o PWA. Flask haría de servidor: la API key nunca puede ir
  dentro de una app (cualquiera podría sacarla).

**Borrada la ruta `/demo`.** Era de pruebas (datos inventados); en una web pública es una puerta
más que vigilar y no aporta nada.

**Formulario con POST en vez de GET.**
- Con GET los Steam IDs iban en la URL: quedaban en el historial y en los registros del
  servidor (Render guarda las URLs que recibe). Con POST van en el cuerpo de la petición.
- Precio aceptado: F5 pregunta "¿reenviar formulario?" y no se pueden compartir enlaces con
  resultados.
- El sonido encendido sí sigue en la URL (`/?sonido=1`, no es un dato personal): `sonido.js`
  cambia el destino del formulario.
- Sin protección CSRF: no hay cuentas ni nada que cambiar; un POST forzado solo haría un análisis.

**Servidor de producción: gunicorn, 1 proceso y varios hilos.**
- `python app.py` es el servidor de pruebas de Flask: no sirve para producción.
- UN solo proceso: las cachés viven en la memoria de un proceso; con dos, cada uno tendría la
  suya (el doble de llamadas a Steam) y los cerrojos no se coordinarían entre ellos.
- Comando de arranque en Render: `gunicorn --workers 1 --threads 8 app:app` (`app:app` = la
  variable `app` del archivo `app.py`; 8 hilos = 8 visitas a la vez; las llamadas a Steam siguen
  limitadas a 5 por el semáforo). Escucha en el puerto que le da Render (variable `PORT`).
- gunicorn 26.2.0 en `requirements.txt` (no funciona en Windows: en local se sigue usando
  `python app.py`). No registra las peticiones por defecto (y con POST los IDs ya no van en la URL).
- `requirements.txt` pasado de UTF-16 a UTF-8: `pip freeze > requirements.txt` en PowerShell 5.1
  lo guarda en UTF-16, un formato raro que podría dar problemas al instalar en Render.
  Si se regenera, hacerlo desde Git Bash o convertirlo a UTF-8.

## Interfaz

**Carátulas que no existen: imagen propia de "ups".**
- Antes salía el texto alternativo grande ("Carátula de X"). Ahora `efectos.js` vigila los
  errores de imagen y pone `static/img/sin-caratula.svg`.
- Sin `onerror` en el HTML: la CSP (`script-src 'self'`) prohíbe JavaScript dentro del HTML, y
  es justo lo que nos protege si alguien colara código en un nombre de juego.
- Se cambia la imagen, no se borra el `<img>`: así la ruleta sigue funcionando.

**Comparaciones de horas sin repetir en la página.** Un `set` por visita (`usadas`) que se pasa
a cada persona; `comparaciones()` lo modifica (Python no copia un set al pasarlo a una función).
Vive solo durante esa visita: no se guarda nada y no hay problemas con los hilos.

**Botón 📸 Compartir (estilo Spotify Wrapped).**
- Imagen vertical 1080×1920 (formato historia), solo de tus datos: perfil, horas, comparación,
  juego favorito con carátula, Pile of Shame, Stand y recomendación de Steam Match.
- Se dibuja en el navegador con `<canvas>`: no se sube a ningún servidor, sin librerías. Nunca
  lleva el Steam ID.
- Los datos los prepara `analysis.py` (`resumen_compartir`) y llegan al JS en `data-resumen`
  con `|tojson` (escapado seguro).
- Carátulas con `crossOrigin = "anonymous"`: el CDN de Steam da permiso CORS, así el canvas no
  queda "contaminado" y se puede exportar.
- En el móvil abre el menú de compartir (`navigator.share`); en el PC, o si falla, se descarga.
- La fuente Press Start 2P no tiene mayúsculas con tilde: en la imagen se evitan ("Ó").
