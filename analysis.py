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


# ===================== Logros absurdos (paso 3.6c) =====================
# Catálogo COMPLETO: id -> (icono, título, texto). Incluye los que da el navegador (logros.js) y los
# de pasos futuros, para que el contador "X/N" conozca el total. Se calculan en cada visita; no se guardan.
LOGROS = {
    "polvo": ("🕸️", "Coleccionista de polvo", "La mitad de tu librería sigue con el plástico puesto."),
    "fiel": ("💍", "Fiel hasta la muerte", "Un solo juego se lleva más de la mitad de tus horas. Eso es amor."),
    "picaflor": ("🦋", "Picaflor", "Pruebas, te aburres y a otra cosa. Muchos juegos no pasan de 2 h."),
    "cesped": ("🌱", "Toca césped", "Más de 1.000 h. Ahí fuera hay un sitio que se llama \"calle\"."),
    "indie": ("🎨", "Indie hasta la médula", "Más de la mitad de tus horas son de estudios pequeñitos."),
    "lobo": ("🐺", "Lobo solitario", "Ni un familiar. Tú contra el mundo."),
    "familia": ("👨‍👩‍👧‍👦", "Familia numerosa", "Cinco familiares. Esto ya es una comuna gamer."),
    "paciencia": ("⏳", "Paciencia infinita", "Más de 10 s esperando sin cerrar la pestaña. Respeto."),
    "insomne": ("🦉", "Insomne", "¿Mirando tus horas de Steam a estas horas? Tu mamá te está buscando."),
    "ludopata": ("🎰", "Ludópata del azar", "10 veces \"Otro\". No te va a salir nada mejor, tío."),
    "abismo": ("🕳️", "Explorador del abismo", "Has llegado al final de la página. Aquí no hay nada. ¿Contento?"),
    "patos": ("🦆", "Susurrador de patos", "Los patos te respetan."),  # paso 3.6d
    "esquina": ("📀", "Esquina perfecta", "Has visto el logo dar en la esquina. Ya puedes morir tranquilo."),  # 3.6e
    "compulsivo": ("👆", "Clic compulsivo", "La tarjeta te ha pedido que pares. No has parado."),  # 3.6e
    "konami": ("🎮", "Código Konami", "↑↑↓↓←→←→BA. Tienes una edad. Respeto."),  # 3.6e
    "jojo": ("⭐", "¿Eso es una JoJo referencia??", "Las has encontrado todas. Yare yare daze."),  # 3.6f
}

# Umbrales de los logros que dependen de tus datos (ajustables)
UMBRAL_POLVO = 50  # % de juegos sin estrenar
UMBRAL_FIEL = 50  # % de tus horas en tu favorito
UMBRAL_PICAFLOR = 30  # % de juegos abandonados (menos de 2 h)
UMBRAL_CESPED = 1000  # horas totales
UMBRAL_PACIENCIA = 10  # segundos que tardó la página
FAMILIA_NUMEROSA = 5  # familiares (el máximo que admite el formulario)


def catalogo_logros():
    """El catálogo en forma de lista de diccionarios (cómodo para pasarlo a JavaScript con |tojson)."""
    return [{"id": i, "icono": ic, "titulo": ti, "texto": te} for i, (ic, ti, te) in LOGROS.items()]


def logros_datos(stats, perfil, familiares, segundos):
    """Ids de los logros que se ganan con TUS datos (el resto los da el navegador).

    stats: tu resultado de estadisticas(); perfil: tu perfil_gamer() (puede ser None);
    familiares: cuántos IDs de familiares se analizaron; segundos: lo que tardó la página.
    """
    ganados = []  # lista de ids
    total = stats["total_propios"]
    if total and stats["pile_pct"] >= UMBRAL_POLVO:  # "total and": sin juegos no hay logro
        ganados.append("polvo")
    fav = stats["favorito"]  # {"nombre", "horas"} o None
    if fav and stats["horas"] and fav["horas"] / stats["horas"] * 100 > UMBRAL_FIEL:
        ganados.append("fiel")
    if total and stats["abandonados"] / total * 100 >= UMBRAL_PICAFLOR:
        ganados.append("picaflor")
    if stats["horas"] > UMBRAL_CESPED:
        ganados.append("cesped")
    if perfil and perfil["indie"]:  # el perfil ya decide si lleva el sello INDIE
        ganados.append("indie")
    if familiares == 0:
        ganados.append("lobo")
    elif familiares >= FAMILIA_NUMEROSA:  # elif = "si no, y además..."
        ganados.append("familia")
    if segundos > UMBRAL_PACIENCIA:
        ganados.append("paciencia")
    return ganados


# ===================== Estadísticas de Stand (paso 3.6f, referencia a JoJo) =====================
# Cada estadística: (umbrales para A, B, C y D; True si "más es mejor", False si "menos es mejor")
STAND = {
    "Poder": ([2000, 1000, 500, 100], True),  # horas totales
    "Velocidad": ([40, 30, 20, 10], True),  # % de juegos abandonados (velocidad para dejarlos)
    "Alcance": ([8, 6, 4, 2], True),  # géneros distintos en tu top
    "Persistencia": ([1000, 500, 200, 50], True),  # horas de tu juego favorito
    "Precisión": ([10, 25, 40, 60], False),  # Pile of Shame: cuanto MÁS BAJO, mejor
    "Potencial": ([100, 50, 20, 5], True),  # juegos sin estrenar (potencial sin explotar)
}
NO_SON_GENERO = {"Sin género", "Free to Play", "Acceso anticipado"}  # no cuentan para el Alcance


def nota(valor, umbrales, mas_es_mejor):
    """Convierte un valor en una nota de la A a la E según sus umbrales."""
    for letra, umbral in zip("ABCD", umbrales):  # zip empareja: ("A", 2000), ("B", 1000)...
        # "X if condición else Y": elige la comparación según el sentido de la estadística
        if (valor >= umbral) if mas_es_mejor else (valor <= umbral):
            return letra  # el primer umbral que alcanza es su nota
    return "E"  # no llegó a ninguno


def stand(stats, por_genero):
    """Ficha de Stand de una persona: nombre (su juego favorito) y 6 notas de la A a la E.

    stats: su resultado de estadisticas(); por_genero: su resultado de horas_por_genero().
    """
    total = stats["total_propios"]
    fav = stats["favorito"]  # {"nombre", "horas"} o None
    valores = {  # el dato real de cada estadística
        "Poder": stats["horas"],
        "Velocidad": stats["abandonados"] / total * 100 if total else 0,
        "Alcance": sum(1 for g in por_genero["generos"] if g["nombre"] not in NO_SON_GENERO),
        "Persistencia": fav["horas"] if fav else 0,
        "Precisión": stats["pile_pct"] if total else 100,  # sin juegos: la peor precisión
        "Potencial": stats["sin_jugar"],
    }
    return {
        "nombre": fav["nombre"].upper() if fav else "SIN NOMBRE",  # .upper() = en mayúsculas
        "notas": [  # en el orden de STAND (los diccionarios de Python conservan el orden)
            {"nombre": n, "nota": nota(valores[n], umbrales, sentido)} for n, (umbrales, sentido) in STAND.items()
        ],
    }
