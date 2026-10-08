# Steam Optimizer

Web app en Python (Flask) que analiza tu librería de Steam y recomienda
a qué jugar y qué comprar según tus géneros y horas jugadas.

> Proyecto de aprendizaje: Python, Flask y Claude Code.

## Privacidad

No almacenamos ningún dato. Solo consultamos tu perfil público de Steam.

## Limitaciones

- Solo funciona con perfiles y detalles de juegos **públicos**.
- Los juegos de la biblioteca familiar (prestados) solo aparecen si los has
  jugado en las **últimas 2 semanas**, porque la API oficial de Steam no
  expone un historial completo. Se marcan con la etiqueta "Familia".

## Instalación

1. Clona el repositorio
2. Crea y activa el entorno virtual:
   `python -m venv venv` y `.\venv\Scripts\Activate.ps1`
3. Instala las dependencias: `pip install -r requirements.txt`
4. Copia `.env.example` a `.env` y añade tu API key de Steam

## Créditos

Fuente [Press Start 2P](https://fonts.google.com/specimen/Press+Start+2P),
con licencia SIL Open Font License (OFL), alojada en `static/fonts/`.

## Estado

En desarrollo