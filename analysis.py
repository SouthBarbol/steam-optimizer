# Capa de lógica: funciones puras (reciben datos y devuelven datos).
# Aquí NO se importa Flask ni se hacen peticiones a Steam.
import random  # módulo estándar de Python para elegir al azar

# Duraciones de referencia: (texto tras la cifra, dato que se muestra entre paréntesis, segundos)
# OJO: las tres últimas son bromas internas; quitarlas o generalizarlas antes de publicar.
COMPARACIONES = [
    ("veces lo que tarda la luz del Sol en llegar a la Tierra", "8 min 20 s", 500),
    ("récords de Usain Bolt en los 100 m", "9,58 s", 9.58),
    ('veces "Never Gonna Give You Up" seguidas', "3 min 33 s", 213),
    ('veces "Bohemian Rhapsody" seguidas', "5 min 55 s", 355),
    ("vueltas de la Estación Espacial a la Tierra", "~92 min", 92 * 60),
    ("maratones de El Señor de los Anillos (versión extendida)", "~11 h 26 min", 686 * 60),
    ("viajes del Apolo 11 hasta la órbita lunar", "~76 h", 76 * 3600),
    ("años en Mercurio", "88 días", 88 * 86400),
    ("días en Venus", "una rotación = 243 días terrestres", 243 * 86400),
    ("gestaciones de elefante", "~22 meses", 22 * 30.4 * 86400),
    ("veces domando a Calero", "5 s", 5),
    ("veces que Mauri llega a la pota", "2 cervezas × 20 min", 2 * 20 * 60),
    ("lustros ardiendo en el caldero de Satán", "1 día con Navarro = 5 lustros", 86400 / 5),
]


def formatear(numero):
    """Formato español: 14447423 -> "14.447.423"; 2.35 -> "2,4"."""
    if numero >= 10:  # cifras grandes: sin decimales, con puntos de millar
        return f"{round(numero):,}".replace(",", ".")  # ":," pone comas de millar; las cambiamos por puntos
    return f"{numero:.1f}".replace(".", ",")  # ":.1f" = un decimal; coma decimal


def comparaciones(horas, cantidad=2):
    """Elige al azar 'cantidad' comparaciones bizarras (con datos reales) para tus horas jugadas."""
    segundos = horas * 3600  # pasamos tus horas a segundos
    # Solo las que salen al menos 1 vez (evita cosas como "0,0 gestaciones de elefante")
    validas = [c for c in COMPARACIONES if segundos / c[2] >= 1]
    elegidas = random.sample(validas, min(cantidad, len(validas)))  # sample: elementos distintos al azar
    # Frase final, p. ej. "1.234 veces domando a Calero (5 s)"
    return [f"{formatear(segundos / seg)} {texto} ({dato})" for texto, dato, seg in elegidas]


def candidatos_sorpresa(juegos):
    """Juegos que (probablemente) no has jugado: tus horas a 0 o desconocidas (préstamos de la familia).

    Devuelve una lista simple para la plantilla y el JavaScript: nombre, dueños y si las horas se desconocen.
    """
    return [
        {
            "nombre": j.get("name", "?"),
            "duenos": j.get("duenos", []),
            "desconocido": j.get("playtime_forever") is None,  # True = "—": puede que ya lo hayas probado
        }
        for j in juegos
        if not j.get("playtime_forever")  # "not" es True tanto para 0 como para None
    ]


def estadisticas(juegos):
    """Calcula Pile of Shame, abandonados y horas en perspectiva a partir de la lista de juegos.

    juegos: lista unida (unir_familia), con "propio" y "playtime_forever" en minutos (None = desconocido).
    """
    # Solo tus juegos propios: en ellos las horas son seguras (en los prestados pueden faltar)
    propios = [j for j in juegos if j.get("propio")]
    total_propios = len(propios)  # cuántos juegos tienes
    # sum(1 for ...) cuenta cuántos elementos cumplen la condición
    sin_jugar = sum(1 for j in propios if (j.get("playtime_forever") or 0) == 0)  # 0 minutos
    abandonados = sum(1 for j in propios if 0 < (j.get("playtime_forever") or 0) < 120)  # menos de 2 h

    # Todas tus horas conocidas (propios + préstamos recientes); los None (desconocidos) se saltan
    minutos = sum(j["playtime_forever"] for j in juegos if j.get("playtime_forever") is not None)
    horas = minutos / 60  # de minutos a horas

    # Juego favorito = el de más minutos (solo entre los que tienen horas conocidas y mayores que 0)
    jugados = [j for j in juegos if j.get("playtime_forever")]  # descarta 0 y None
    # max(..., key=...) devuelve el elemento con el valor más alto; default=None si la lista está vacía
    top = max(jugados, key=lambda j: j["playtime_forever"], default=None)
    favorito = {"nombre": top.get("name", "?"), "horas": round(top["playtime_forever"] / 60)} if top else None

    return {  # diccionario con todo lo que mostrará la plantilla
        "total_propios": total_propios,
        "sin_jugar": sin_jugar,
        # porcentaje con un decimal; si no tienes juegos evitamos dividir entre 0
        "pile_pct": round(sin_jugar / total_propios * 100, 1) if total_propios else 0,
        "abandonados": abandonados,
        "horas": round(horas),  # horas enteras
        "dias": round(horas / 24, 1),  # días seguidos jugando
        "pct_anio": round(horas / (365 * 24) * 100, 1),  # porcentaje de un año entero
        "comparaciones": comparaciones(horas),  # 2 frases bizarras elegidas al azar
        "favorito": favorito,  # {"nombre", "horas"} del juego más jugado, o None
    }
