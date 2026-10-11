# Steam Optimizer

Web app en Python (Flask) que analiza tu librería de Steam y recomienda
a qué jugar y qué comprar según tus géneros y horas jugadas.

> Proyecto de aprendizaje: Python, Flask y Claude Code.

## Qué hace

- Muestra tu librería ordenada por horas, con carátulas y de quién es cada juego.
- Biblioteca familiar: añade hasta 5 Steam IDs de familiares (no se guardan).
- Estadísticas por persona: Pile of Shame, juegos abandonados, horas en perspectiva,
  juego sorpresa y duelo familiar.
- Horas por género y perfil gamer, calculados con los 10 juegos más jugados de cada persona.

## Privacidad

No almacenamos ningún dato. Solo consultamos tu perfil público de Steam.
El servidor guarda en memoria los géneros de cada juego (datos del juego, no tuyos)
para no repetir consultas. Las carátulas las descarga tu navegador del CDN de Steam.

## Limitaciones

- Solo funciona con perfiles y detalles de juegos **públicos**.
- Los juegos de la biblioteca familiar (prestados) solo aparecen si los has
  jugado en las **últimas 2 semanas**, porque la API oficial de Steam no
  expone un historial completo. Sus horas se muestran como "—" (desconocidas).
- Los géneros salen de la tienda de Steam (API no oficial, con límite de peticiones):
  solo se piden para el top 10 de cada persona. La primera carga puede tardar ~20 s;
  las siguientes son casi instantáneas. Si Steam no responde, se avisa con "Sin datos".
- La etiqueta INDIE de la tabla solo aparece en juegos del top 10 de alguien.

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
`yare-yare.mp3`. Si faltan, suenan efectos sintetizados y la voz del navegador.

## Créditos

Fuente [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P),
con licencia SIL Open Font License (OFL), alojada en `static/fonts/`.

## Estado

En desarrollo