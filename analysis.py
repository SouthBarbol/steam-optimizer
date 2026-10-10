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


def unir_juegos(propios, recientes):
    """Une juegos propios y recientes sin duplicados; marca con propio=False los que no son tuyos."""
    ids_propios = {j["appid"] for j in propios}  # conjunto con los appid de tu librería (búsqueda rápida)
    resultado = [{**j, "propio": True} for j in propios]  # copia cada juego propio añadiéndole propio=True
    resultado += [  # añade los recientes que NO están en tu librería (probablemente de la familia)
        {**j, "propio": False} for j in recientes if j["appid"] not in ids_propios
    ]
    return resultado  # lista unida


def unir_familia(mios, familia, yo):
    """Une tus juegos con los de la familia sin duplicados; cada juego lleva la lista "duenos".

    mios: resultado de unir_juegos (con la marca "propio").
    familia: lista de pares (etiqueta, juegos), p. ej. [("Familiar 1", [...]), ...].
    yo: tu etiqueta (tu nombre de Steam, o "Tú" si no se pudo obtener).
    Las horas (playtime_forever) son siempre las TUYAS; None si Steam no las da.
    """
    # Diccionario {appid: juego}: la clave appid no se repite, así cada juego aparece una sola vez
    juegos = {j["appid"]: {**j, "duenos": [yo] if j["propio"] else []} for j in mios}
    for etiqueta, lista in familia:  # recorremos la librería de cada familiar
        for j in lista:  # y cada uno de sus juegos
            if j["appid"] in juegos:  # el juego ya está en la lista...
                juegos[j["appid"]]["duenos"].append(etiqueta)  # ...solo añadimos otro dueño
            else:  # juego nuevo: no lo tienes ni lo has jugado recientemente
                # copiamos sus datos con TUS horas a None = desconocidas (Steam no las da para préstamos)
                juegos[j["appid"]] = {**j, "playtime_forever": None, "propio": False, "duenos": [etiqueta]}
    return list(juegos.values())  # devolvemos solo los juegos, sin las claves


# Cuántos juegos (los más jugados de cada persona) se consultan para los géneros
TOP_GENEROS = 10

# Etiquetas de Steam que no deciden el perfil: no describen CÓMO se juega
# (modelo de negocio, estado de desarrollo o tamaño del estudio). "Indie" va aparte, como pegatina
NO_DEFINEN_PERFIL = {"Free to Play", "Acceso anticipado", "Indie"}

# El perfil lleva la pegatina "Indie" si ese género supera este % de las horas del top
UMBRAL_INDIE = 50

# Perfil gamer según el género con más horas: (título, frase). {horas} se rellena con el dato real
PERFILES = {
    "Acción": ("Gatillazo Gatillero Pistolerito", "{horas} h de reflejos, explosiones y cero paciencia para los menús."),
    "Aventura": ("Willifó", "{horas} h mirando detrás de cada roca por si había un cofre."),
    "Rol": ("Mega virgin plus", "{horas} h subiendo de nivel; la vida real sigue en nivel 1."),
    "Estrategia": ("Imperio otomano enjoyer", "{horas} h planeando; seguro que ya tienes un plan para leer esto."),
    "Simuladores": ("Funambulista a media jornada", "{horas} h trabajando en mundos que no pagan nómina."),
    "Deportes": ("El pinche cuervo pendejo mamado", "{horas} h de deporte sin sudar una gota."),
    "Carreras": ("Francesco Virgolini", "{horas} h de la maquina mas veloz de tutti ITALIE."),
    "Casual": ("Putisimo Chill", "{horas} h de partidas de «solo una más»."),
    "Multijugador masivo": ("Tauren nivel enseñame media aunque sea carla", "{horas} h con pajilleritos premium."),
}
# Para géneros que no están en PERFILES (p. ej. "Sin género" o alguno nuevo de Steam)
PERFIL_DESCONOCIDO = ("Inclasificable", "{horas} h en géneros que ni Steam sabe nombrar.")


def top_jugados(juegos, n=TOP_GENEROS):
    """Los n juegos con más horas conocidas (mayores que 0), de más a menos."""
    jugados = [j for j in juegos if j.get("playtime_forever")]  # descarta 0 y None
    return sorted(jugados, key=lambda j: j["playtime_forever"], reverse=True)[:n]  # [:n] = los n primeros


def horas_por_genero(juegos, generos):
    """Suma las horas de cada juego del top a TODOS sus géneros (por eso los % no suman 100).

    juegos: los juegos de UNA persona, con SUS minutos en "playtime_forever".
    generos: {appid: lista de géneros, o None si la consulta a Steam falló}.
    """
    top = top_jugados(juegos)  # sus juegos más jugados
    total = sum(j.get("playtime_forever") or 0 for j in juegos)  # todos sus minutos conocidos
    minutos_top = sum(j["playtime_forever"] for j in top)  # minutos del top
    acumulado = {}  # {género: minutos}
    sin_datos = 0  # juegos del top cuyos géneros no se pudieron consultar
    for j in top:  # recorremos los juegos del top
        lista = generos.get(j["appid"])  # None si falló o no se pidió
        if lista is None:  # sin datos de este juego...
            sin_datos += 1  # ...lo contamos para avisar...
            continue  # ...y saltamos al siguiente juego
        for g in lista or ["Sin género"]:  # [] (sin ficha en la tienda) cuenta como "Sin género"
            acumulado[g] = acumulado.get(g, 0) + j["playtime_forever"]  # .get(g, 0): 0 si es la primera vez
    ordenados = sorted(acumulado.items(), key=lambda par: par[1], reverse=True)  # de más a menos minutos
    return {  # diccionario con todo lo que mostrará la plantilla
        "generos": [  # pct = % de las horas del top; también sirve como ancho de la barra
            {"nombre": g, "horas": round(m / 60), "pct": round(m / minutos_top * 100)}
            for g, m in ordenados
        ],
        "cobertura": round(minutos_top / total * 100) if total else 0,  # % de sus horas que cubre el top
        "sin_datos": sin_datos,  # cuántos juegos del top no tienen datos
        "juegos": len(top),  # puede ser menos de 10 si ha jugado a pocos
    }


def perfil_gamer(generos):
    """Título y frase según el género con más horas; None si no hay datos suficientes.

    generos: la lista "generos" que devuelve horas_por_genero (ya ordenada de más a menos horas).
    """
    estilos = [g for g in generos if g["nombre"] not in NO_DEFINEN_PERFIL]  # quita "Indie", "Free to Play"...
    if not estilos:  # no queda ningún género que describa su estilo
        return None  # la plantilla no mostrará perfil
    principal = estilos[0]  # el primero es el de más horas
    titulo, frase = PERFILES.get(principal["nombre"], PERFIL_DESCONOCIDO)  # si no está, el genérico
    # next(...) busca el primer elemento que cumple la condición; 0 si no hay ninguno
    pct_indie = next((g["pct"] for g in generos if g["nombre"] == "Indie"), 0)
    return {
        "titulo": titulo,
        "frase": frase.format(horas=formatear(principal["horas"])),  # rellena el hueco {horas}
        "genero": principal["nombre"],  # el género en el que se basa (para mostrarlo)
        "indie": pct_indie > UMBRAL_INDIE,  # True = mostrar la pegatina "Indie"
    }
