# Steam Optimizer

Web app en Python (Flask) que analiza tu librería de Steam y recomienda
a qué jugar y qué comprar según tus etiquetas, géneros y horas jugadas.

> Proyecto de aprendizaje: Python, Flask y Claude Code.

## Qué hace

- Muestra tu librería ordenada por horas, con carátulas y de quién es cada juego.
- Biblioteca familiar: añade hasta 5 Steam IDs de familiares (no se guardan).
- Estadísticas por persona: Pile of Shame, juegos abandonados, horas en perspectiva
  y duelo familiar.
- Ruleta del caos: un juego al azar de toda la librería con una frase absurda.
- Horas por género (con los 10 juegos más jugados de cada persona) y perfil gamer según su etiqueta
  favorita de Steam (con todos sus juegos jugados 2 h o más).
- Qué jugar (Steam Match): tus pendientes puntuados según tus géneros, tu racha reciente,
  los consejos de la familia y las reseñas de Steam. Detalle en `ALGORITMO.md`.
- ¿Te atreves?: pendientes con etiquetas a las que nunca has jugado.
- Qué comprar: 6 juegos mainstream (populares y afines a tus etiquetas favoritas) y 6 bizarros
  (mezclas raras de tus gustos, poco conocidos pero bien valorados), con precio, descuento y reseñas.
  Nunca recomienda lo que ya tenéis tú o tu familia ni juegos para adultos. Detalle en `ALGORITMO.md`.
- Tragaperras de la tienda: un juego al azar de toda la tienda de Steam con una frase absurda
  (y premio si sale una joya, o trombón si sale un desastre).
- El rincón de la pesturria: juegos famosos por malos (muchísimas reseñas y casi todas negativas),
  uno al azar con una frase de bar. Con moscas.
- Navegación: menú fijo de secciones, botón para volver arriba y librería plegable con buscador,
  orden por nombre u horas y tabla de récords (HIGH SCORES).
- Personalidad: efectos, sonidos sintetizados (empiezan silenciados), logros absurdos,
  referencias a JoJo, botones de recreativa y modo tele antigua (CRT).

## Privacidad

No almacenamos ningún dato. Solo consultamos tu perfil público de Steam.
El servidor guarda en memoria los géneros, etiquetas y reseñas de cada juego, las búsquedas en la
tienda durante 3 horas y la lista de los más vendidos durante 24 horas (datos de los juegos, no tuyos),
para no repetir consultas.
Las carátulas las descarga tu navegador del CDN de Steam.

## Limitaciones

- Solo funciona con perfiles y detalles de juegos **públicos**.
- Los juegos de la biblioteca familiar (prestados) solo aparecen si los has
  jugado en las **últimas 2 semanas**, porque la API oficial de Steam no
  expone un historial completo. Sus horas se muestran como "—" (desconocidas).
- Los géneros salen de la tienda de Steam (API no oficial, con límite de peticiones):
  se piden para el top 10 de cada persona y, con un máximo de consultas nuevas por visita
  (20 y 10), para tus pendientes y tus abandonados. La primera carga puede tardar ~20 s;
  las siguientes son casi instantáneas. Si Steam no responde, se avisa con "Sin datos".
- La etiqueta INDIE de la tabla solo aparece en juegos del top 10 de alguien.
- Steam Match puede recomendarte un préstamo de la familia al que ya jugaste hace más de
  2 semanas: no podemos saber tus horas en él.
- "Qué comprar" usa la búsqueda de la tienda de Steam (`IStoreQueryService/Query`), poco
  documentada: el orden por popularidad o valoración se dedujo probando y puede cambiar.
  Los precios son los de España (euros) y se refrescan cada 3 horas.
- El rincón de la pesturria busca entre los 5.000 juegos más vendidos de siempre: la primera visita
  de cada día tarda unos 13 s más.

## Instalación

1. Clona el repositorio
2. Crea y activa el entorno virtual:
   `python -m venv venv` y `.\venv\Scripts\Activate.ps1`
3. Instala las dependencias: `pip install -r requirements.txt`
4. Copia `.env.example` a `.env` y añade tu API key de Steam
5. Arranca el servidor con `python app.py` y abre http://127.0.0.1:5000

## Sonidos opcionales (uso privado)

Las referencias a JoJo pueden usar clips originales de la serie, que **no se incluyen** (tienen derechos
de autor). Si los tienes, cópialos en `static/sonidos/` con estos nombres: `za-warudo.mp3`,
`tiempo-fluye.mp3`, `ora-ora.mp3`, `muda-muda.mp3`, `to-be-continued.mp3`, `kono-dio-da.mp3` y
`yare-yare.mp3`. El modo caos puede usar además `ay-ay-ay.mp3`. Si faltan, suenan efectos
sintetizados y la voz del navegador.

## Créditos

Fuente [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P),
con licencia SIL Open Font License (OFL), alojada en `static/fonts/`.

## Estado

En desarrollo