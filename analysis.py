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
    "ludopata": ("🎰", "Ludópata del azar", "10 veces \"Otra\". No te va a salir nada mejor, tío."),
    "abismo": ("🕳️", "Explorador del abismo", "Has llegado al final de la página. Aquí no hay nada. ¿Contento?"),
    "patos": ("🦆", "Susurrador de patos", "Los patos te respetan."),  # paso 3.6d
    "esquina": ("📀", "Esquina perfecta", "Has visto el logo dar en la esquina. Ya puedes morir tranquilo."),  # 3.6e
    "compulsivo": ("👆", "Clic compulsivo", "La tarjeta te ha pedido que pares. No has parado."),  # 3.6e
    "konami": ("🎮", "Código Konami", "↑↑↓↓←→←→BA. Tienes una edad. Respeto."),  # 3.6e
    "jojo": ("⭐", "¿Eso es una JoJo referencia??", "Las has encontrado todas. Yare yare daze."),  # 3.6f
    "piedra": ("💔", "Corazón de piedra", "Todos los juegos te han tirado ficha y los has rechazado a todos."),  # 4.5a
    "enamoradizo": ("💘", "Enamoradizo", "Match con todos. Tienes el corazón más grande que el disco duro."),  # 4.5a
    "sinmiedo": ("🧭", "Sin miedo", "Has abierto un juego de territorio inexplorado. Tu zona de confort te echa de menos."),  # 4.5c
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


# ===================== Qué jugar (paso 4) =====================
TOP_RECOMENDACIONES = 5  # cuántas recomendaciones se muestran
PRESUPUESTO_GENEROS = 20  # consultas NUEVAS de géneros a Steam por visita (las de la caché no cuentan)
ULTIMOS_JUGADOS = 10  # cuántos juegos recientes forman tu "racha actual"
PESO_RACHA = 0.6  # cuánto pesa la racha frente a tus horas de siempre (0 = nada, 1 = todo): 60/40
MAX_IGUALES = 2  # en el top, como mucho 2 juegos con los mismos géneros en común contigo
UMBRAL_PRIMO = 20  # horas: si un familiar le echó al menos esto a un juego, el juego recibe un plus
PLUS_PRIMO = 1.25  # el plus: puntos × 1,25 (+25 %)
UMBRAL_JOYA = 1000  # menos reseñas que esto en Steam: joya oculta...
PLUS_JOYA = 1.2  # ...puntos × 1,2
UMBRAL_SUPERVENTAS = 100000  # más reseñas que esto: superventas...
CASTIGO_SUPERVENTAS = 0.9  # ...puntos × 0,9
FINALISTAS = 15  # solo a estos se les consulta la nota de las reseñas (una llamada por juego)
MIN_RESENAS_NOTA = 10  # con menos reseñas, el % no es fiable: sin efecto
UMBRAL_ACLAMADO, PLUS_ACLAMADO = 90, 1.15  # 90 % positivas o más: × 1,15
UMBRAL_MIXTO, CASTIGO_MIXTO = 70, 0.9  # por debajo del 70 %: × 0,9
UMBRAL_MALO, CASTIGO_MALO = 50, 0.75  # por debajo del 50 %: × 0,75
JOYA_MIN_PCT = 80  # la pegatina 💎 exige además este % de positivas (si se sabe)
UMBRAL_ABANDONO = 120  # minutos: menos de 2 h jugadas = abandonado (como en las estadísticas)
PRESUPUESTO_ABANDONOS = 10  # consultas NUEVAS de géneros de abandonados por visita
MIN_ABANDONOS_ANTI = 3  # anti-gusto: aparece en al menos 3 abandonados...
PCT_ABANDONOS_ANTI = 25  # ...y en al menos el 25 % de tus abandonados analizados...
MAX_GUSTO_ANTI = 20  # ...y tu % en ese género (de siempre o de la racha) es menor que esto
CASTIGO_ANTI = 0.8  # pendientes con algún anti-gusto: puntos × 0,8
TOP_EXPERIENCIA = 10  # etiquetas de cada juego jugado que cuentan como "lo que conoces"
TOP_DEFINEN = 3  # etiquetas que definen a un pendiente (las 3 más votadas, sin las neutras)
TOP_ATREVIDOS = 3  # juegos en "¿Te atreves?" (1 visible + "Otro")
# Etiquetas que no dicen DE QUÉ va un juego (modo, formato, estilo o calidad): no cuentan como "nuevas"
ETIQUETAS_NEUTRAS = {
    "Un jugador", "Multijugador", "Multijugador local", "Cooperativos", "Cooperativos en línea",
    "Cooperativos locales", "Pantalla dividida", "Para mando", "Solo ratón", "Indie", "Free to Play",
    "Acceso anticipado", "Versiones nuevas", "Secuelas", "Clásicos", "Buena trama", "Gran banda sonora",
    "Banda sonora", "Preciosos", "Adictivos", "Divertidos", "Cortos", "2D", "3D", "2.5D", "Pixelados",
    "Estilizados", "Coloridos", "Primera persona", "Tercera persona", "Modificables", "Mods", "Episódicos",
    "Valor continuo", "Lineales", "No lineales", "Finales múltiples", "Las elecciones importan", "Retro",
    "Nostalgia", "Vieja escuela", "Años 80", "Años 90", "Épicos", "Ambientales", "Música",
}


def pendientes(juegos):
    """Juegos que (probablemente) no has jugado: tus horas a 0 o desconocidas (None = préstamo)."""
    return [j for j in juegos if not j.get("playtime_forever")]  # "not" es True para 0 y para None


def ultimos_jugados(juegos, n=ULTIMOS_JUGADOS):
    """Los n juegos que has jugado más recientemente (por la fecha de tu última partida)."""
    def fecha(j):  # función dentro de otra: solo se usa aquí
        if not j.get("propio"):  # préstamo jugado en las últimas 2 semanas: no trae fecha, pero es reciente
            return float("inf")  # "infinito": va el primero
        return j.get("rtime_last_played") or 0  # segundos desde 1970; 0 = Steam no lo sabe
    jugados = [j for j in juegos if j.get("playtime_forever") and fecha(j)]  # con horas y con fecha
    return sorted(jugados, key=fecha, reverse=True)[:n]  # del más reciente al más antiguo


def racha_actual(recientes, generos):
    """{género: % de tus últimos juegos que lo tienen}. Un voto por juego, sin mirar horas."""
    votos, contados = {}, 0  # {género: nº de juegos} y cuántos juegos han votado
    for j in recientes:
        lista = generos.get(j["appid"])
        if lista is None:  # consulta fallida: ese juego no vota
            continue
        contados += 1
        for g in lista:
            votos[g] = votos.get(g, 0) + 1  # un voto más para ese género
    return {g: round(v / contados * 100) for g, v in votos.items()} if contados else {}


def afinidad(generos_juego, tus_pct):
    """Suma tus % de horas en los géneros del juego. Devuelve (puntos, motivo).

    tus_pct: {género: % de tus horas del top}. Motivo: [(género, %), ...] de mayor a menor.
    Los géneros que no dicen cómo se juega (NO_DEFINEN_PERFIL: Indie, Free to Play...) no suman.
    """
    coinciden = [(g, tus_pct[g]) for g in generos_juego if g in tus_pct and g not in NO_DEFINEN_PERFIL]
    coinciden.sort(key=lambda par: par[1], reverse=True)  # el género que más pesa, primero
    return sum(pct for _, pct in coinciden), coinciden  # "_" = el nombre, que aquí no hace falta


def abandonados(juegos):
    """Juegos que probaste menos de 2 h y no has tocado en las últimas 2 semanas."""
    return [j for j in juegos
            if 0 < (j.get("playtime_forever") or 0) < UMBRAL_ABANDONO and not j.get("playtime_2weeks")]


def anti_gustos(dejados, generos, por_genero, racha):
    """Conjunto de géneros que sueles abandonar y que NO están entre tus gustos."""
    siempre = {g["nombre"]: g["pct"] for g in por_genero}
    votos, contados = {}, 0  # {género: nº de abandonados que lo tienen} y abandonados con datos
    for j in dejados:
        lista = generos.get(j["appid"])
        if lista is None:  # sin consultar o fallo: no vota
            continue
        contados += 1
        for g in lista:
            if g not in NO_DEFINEN_PERFIL:
                votos[g] = votos.get(g, 0) + 1
    return {g for g, v in votos.items()  # {... for ...}: conjunto por comprensión
            if v >= MIN_ABANDONOS_ANTI
            and v / contados * 100 >= PCT_ABANDONOS_ANTI
            and max(siempre.get(g, 0), racha.get(g, 0)) < MAX_GUSTO_ANTI}


def experiencia(juegos, etiquetas):
    """Etiquetas de los juegos que has jugado DE VERDAD (2 h o más): "lo que conoces"."""
    conocidas = set()
    for j in juegos:
        if (j.get("playtime_forever") or 0) >= UMBRAL_ABANDONO:  # los abandonados no cuentan
            conocidas.update(etiquetas.get(j["appid"], [])[:TOP_EXPERIENCIA])  # update: añade varias
    return conocidas


def etiquetas_nuevas(etiquetas_juego, conocidas):
    """De las 3 etiquetas que definen el juego (sin las neutras), las que nunca has jugado."""
    definen = [e for e in etiquetas_juego if e not in ETIQUETAS_NEUTRAS][:TOP_DEFINEN]
    return [e for e in definen if e not in conocidas]


def territorio_inexplorado(juegos, etiquetas):
    """{appid: [etiquetas nuevas]} de tus pendientes con algo que nunca has jugado."""
    conocidas = experiencia(juegos, etiquetas)
    if not conocidas:  # sin etiquetas de lo que has jugado (p. ej. falló Steam): no se aparta nada
        return {}
    resultado = {}
    for j in pendientes(juegos):
        nuevas = etiquetas_nuevas(etiquetas.get(j["appid"], []), conocidas)
        if nuevas:
            resultado[j["appid"]] = nuevas
    return resultado


def elegir_atrevidos(atrevidos, n=TOP_ATREVIDOS):
    """Los n inexplorados con más puntos; si se puede, cada uno con una etiqueta nueva distinta."""
    random.shuffle(atrevidos)  # a igualdad de puntos, al azar
    atrevidos.sort(key=lambda r: r["puntos"], reverse=True)
    elegidos, vistas = [], set()  # vistas: primeras etiquetas nuevas ya usadas
    for r in atrevidos:
        if r["nuevas"][0] not in vistas:  # [0]: la etiqueta nueva más votada del juego
            elegidos.append(r)
            vistas.add(r["nuevas"][0])
    saltados = [r for r in atrevidos if r not in elegidos]  # si no hay variedad, se rellena con estos
    return (elegidos + saltados)[:n]


def consejos_familia(jugados, umbral=UMBRAL_PRIMO):
    """{appid: {"nombre", "horas"}} del familiar que más horas le echó a cada juego (si llega al umbral).

    jugados: {familiar: sus juegos con SUS horas} (lo que devuelve pedir_familia en app.py).
    """
    consejos = {}
    for nombre, lista in jugados.items():  # .items(): pares (clave, valor) del diccionario
        for j in lista:
            horas = (j.get("playtime_forever") or 0) / 60
            previo = consejos.get(j["appid"])  # otro familiar que ya lo aconsejó (o None)
            if horas >= umbral and (previo is None or horas > previo["horas"]):
                consejos[j["appid"]] = {"nombre": nombre, "horas": round(horas)}
    return consejos


def con_variedad(puntuados, n, max_iguales=MAX_IGUALES):
    """Elige los n primeros saltándose los que repetirían demasiado la misma mezcla de géneros.

    puntuados: ya ordenados de más a menos puntos. Si no hay variedad suficiente,
    se rellena con los saltados (en su orden), para devolver siempre n si hay n.
    """
    elegidos, cuenta = [], {}  # cuenta: {mezcla de géneros: cuántos van en el top}
    for r in puntuados:
        mezcla = tuple(r["comunes"])  # tupla: como una lista, pero sirve de clave de diccionario
        if cuenta.get(mezcla, 0) < max_iguales:
            elegidos.append(r)
            cuenta[mezcla] = cuenta.get(mezcla, 0) + 1
        if len(elegidos) == n:  # ya están todos: dejamos de buscar
            break
    saltados = [r for r in puntuados if r not in elegidos]  # los que no entraron, en su orden
    return (elegidos + saltados)[:n]


def multiplicador_fama(resenas):
    """(multiplicador, ¿es joya?) según el nº de reseñas en Steam. Sin dato (None): sin efecto."""
    if resenas is None:
        return 1, False  # no inventamos: ni plus ni castigo
    if resenas < UMBRAL_JOYA:
        return PLUS_JOYA, True  # poca gente lo conoce: joya oculta
    if resenas > UMBRAL_SUPERVENTAS:
        return CASTIGO_SUPERVENTAS, False  # lo conoce todo el mundo: un poco menos
    return 1, False  # término medio: sin efecto


def nota_fiable(valoracion):
    """% de reseñas positivas si es fiable (al menos MIN_RESENAS_NOTA reseñas); si no, None."""
    if valoracion and valoracion["total"] >= MIN_RESENAS_NOTA:
        return valoracion["pct"]
    return None


def multiplicador_valoracion(pct):
    """Multiplicador según el % de reseñas positivas (el de nota_fiable). None: sin efecto."""
    if pct is None:
        return 1
    if pct >= UMBRAL_ACLAMADO:
        return PLUS_ACLAMADO  # aclamado
    if pct >= UMBRAL_MIXTO:
        return 1  # bien valorado: sin efecto
    if pct >= UMBRAL_MALO:
        return CASTIGO_MIXTO  # reseñas variadas
    return CASTIGO_MALO  # más negativas que positivas


def que_jugar(juegos, generos, por_genero, racha, consejos=None, resenas=None, anti=None, inexplorados=None,
              valoraciones=None, n=TOP_RECOMENDACIONES):
    """Los n pendientes con más afinidad: mezcla tus gustos de siempre y tu racha actual.

    juegos: tu lista unida (unir_familia). generos: {appid: géneros, o None si no se pudo consultar}.
    por_genero: la lista "generos" de horas_por_genero (tus % de horas por género, de siempre).
    racha: lo que devuelve racha_actual ({género: % de tus últimos juegos}); {} si no hay fechas.
    consejos: lo que devuelve consejos_familia (juegos a los que un familiar echó muchas horas).
    resenas: {appid: nº de reseñas en Steam, o None si no se sabe} (joya oculta / superventas).
    anti: lo que devuelve anti_gustos (géneros que sueles abandonar).
    inexplorados: lo que devuelve territorio_inexplorado ({appid: etiquetas que nunca has jugado}).
    valoraciones: {appid: lo que devuelve get_valoracion} (% de positivas); solo de los finalistas.
    """
    consejos = consejos or {}  # None -> {} (un {} como valor por defecto se compartiría entre llamadas)
    resenas = resenas or {}
    anti = anti or set()  # set(): conjunto vacío ({} sería un diccionario)
    inexplorados = inexplorados or {}
    valoraciones = valoraciones or {}
    siempre = {g["nombre"]: g["pct"] for g in por_genero}  # de lista a diccionario: búsqueda rápida
    peso = PESO_RACHA if racha else 0  # sin racha (no hay fechas), solo tus horas de siempre
    lista = pendientes(juegos)
    puntuados, analizados = [], 0  # dos variables a la vez: lista vacía y contador a 0
    atrevidos = []  # pendientes de territorio inexplorado (para "¿Te atreves?")
    for j in lista:
        generos_j = generos.get(j["appid"])  # None = no consultado (fuera del presupuesto) o fallo
        if generos_j is None:
            continue  # sin datos no se puede puntuar: se queda para otra visita
        analizados += 1
        p_siempre, comunes_s = afinidad(generos_j, siempre)
        p_racha, comunes_r = afinidad(generos_j, racha)
        puntos = (1 - peso) * p_siempre + peso * p_racha  # mezcla de las dos afinidades (con decimales)
        consejo = consejos.get(j["appid"])  # ¿algún familiar le echó muchas horas?
        if consejo:
            puntos *= PLUS_PRIMO  # *= multiplica y guarda; solo multiplica: con 0 puntos sigue en 0
        if anti & set(generos_j):  # &: géneros que están en los dos conjuntos; vacío = False
            puntos *= CASTIGO_ANTI  # tiene algún género que sueles abandonar (una vez, aunque tenga varios)
        fama, joya = multiplicador_fama(resenas.get(j["appid"]))  # joya oculta / superventas
        pct = nota_fiable(valoraciones.get(j["appid"]))  # % de positivas, o None
        puntos = round(puntos * fama * multiplicador_valoracion(pct))  # redondeamos una sola vez, al final
        joya = joya and (pct is None or pct >= JOYA_MIN_PCT)  # desconocido y MALO no es una joya
        reco = {
            "appid": j["appid"],
            "nombre": j.get("name", "?"),
            "duenos": j.get("duenos", []),
            "desconocido": j.get("playtime_forever") is None,  # préstamo: quizá ya lo probaste
            "puntos": puntos,
            # géneros en común, sin % (la fórmula es secreta); {...}: conjunto, sin repetidos
            "comunes": sorted({g for g, _ in comunes_s + comunes_r}),
            "consejo": consejo,  # {"nombre", "horas"} del familiar, o None
            "joya": joya,  # True = pocas reseñas (para la pegatina 💎)
            "pct_positivo": pct,  # % de reseñas positivas en Steam (None si no se sabe)
            "aclamado": pct is not None and pct >= UMBRAL_ACLAMADO,  # para la pegatina 👑
        }
        nuevas = inexplorados.get(j["appid"])  # etiquetas que nunca has jugado (o None)
        if nuevas:  # territorio inexplorado: fuera del top, a "¿Te atreves?" (aunque tenga 0 puntos)
            atrevidos.append({**reco, "nuevas": nuevas})
        elif puntos:  # 0 = no se parece a nada de lo que juegas: no se recomienda
            puntuados.append(reco)
    random.shuffle(puntuados)  # a igualdad de puntos, orden al azar (sort respeta el orden previo)
    puntuados.sort(key=lambda r: r["puntos"], reverse=True)  # de más a menos afinidad
    return {
        "recomendados": con_variedad(puntuados, n),  # los n mejores, sin repetir demasiado la misma mezcla
        "atreverse": elegir_atrevidos(atrevidos),  # territorio inexplorado (opción "¿Te atreves?")
        "analizados": analizados,  # pendientes con géneros conocidos...
        "pendientes": len(lista),  # ...de todos los pendientes ("analizados 40 de 230")
    }


# ===================== Bios de Steam Match (paso 4.3a) =====================
# Plantillas absurdas con huecos que se rellenan con datos reales del juego.
# OJO: humor satírico (vivienda, capitalismo); revisar el tono antes de publicar.
BIOS_GENERALES = [
    "Me gustan los paseos largos por la playa y el {genero}. Sobre todo el {genero}.",
    "Llevo tanto tiempo en tu biblioteca que un fondo buitre ya quiere alquilarme por habitaciones.",
    "Busco a alguien de {genero} que no me deje a las 2 h.",
    "Mi signo es {genero}, con ascendente «pendiente de instalar».",
    "Prometo no ocupar 60 GB. Bueno, igual sí. Bueno, seguro que sí.",
    "Soy {nombre}. Mis amigos me llaman «ese que nunca abres».",
    "He visto cosas que no creerías. Principalmente tu escritorio, desde dentro de una carpeta.",
    "Red flag: no me has jugado. Green flag: aún estás a tiempo.",
    "Mi terapeuta dice que deje de esperar tu doble clic.",
    "No soy como los otros juegos. Yo también tengo {genero}, pero con sentimientos.",
    "Un pato me dijo que haríamos match. Los patos nunca mienten.",
    "Busco relación seria. Mínimo tres partidas y conocer a tu mando.",
    "Me salté el tutorial de la vida. Ahora soy {genero} a tiempo completo.",
    "Vivo en tu disco duro sin pagar alquiler. Ni en Cádiz ni en Madrid lo consigue nadie más.",
    "Ocupo un hueco de tu SSD que en Madrid se alquilaría por 900 € al mes como «estudio con encanto».",
    "Busco jugador solvente: nómina, aval de tus padres y tres meses de fianza. Lo de la fianza va en serio.",
    "Me compraste en rebajas. Es lo más cerca que vas a estar de tener una propiedad.",
    "Si no me juegas no es culpa tuya: es el capitalismo, que te tiene 40 h a la semana pagando un zulo.",
    "Soy {genero}, no un piso turístico: puedes quedarte en mí más de tres noches.",
    "Un fondo buitre compró la carpeta de al lado. Ahora el vecindario se llama «Gaming Living Premium».",
    "El capitalismo me hizo pendiente. Tú puedes hacerme libre. Doble clic, camarada.",
]
BIOS_PRIMO = [
    "{familiar} me dedicó {horas} h y aún así sigo pensando en ti.",
    "{horas} h con {familiar}. Lo nuestro sería distinto, te lo juro.",
    "Pregúntale a {familiar} por mí. Mejor no, que se pone celoso.",
    "{familiar} y yo tuvimos {horas} h de algo bonito. Ahora quiero conocer al resto de la familia.",
]
BIOS_PRESTAMO = [
    "Soy de {dueno}, pero mi corazón es tuyo. Que no se entere.",
    "Técnicamente esto es infidelidad familiar. Técnicamente.",
    "Vivo en casa de {dueno}, como todo el mundo a los 35 con estos alquileres.",
    "Soy de {dueno}, pero lo compartimos como un piso de estudiantes: sin preguntar y sin fregar.",
]
BIOS_JOYA = [
    "Poca gente me conoce, como a un piso asequible en Cádiz.",
    "Me han descubierto tres personas y un bot. Sé la cuarta.",
    "Underground desde antes de que fuera guay.",
]
BIOS_ACLAMADO = [
    "El {pct} % de la gente me quiere. El otro {resto} % no tiene corazón.",
    "{pct} % de reseñas positivas y aún así sigo soltero.",
    "Tengo un {pct} % de aprobación. Ningún político puede decir lo mismo.",
]
PROB_BIO_ESPECIAL = 0.5  # si el juego tiene algo especial, probabilidad de usar una frase de ese tipo


def bio(reco, usadas):
    """Una bio absurda para la ficha de Steam Match. usadas: frases ya elegidas (para no repetir)."""
    consejo = reco.get("consejo") or {}  # {} si no hay consejo, para que .get() no falle
    pct = reco.get("pct_positivo")
    huecos = {  # todos los huecos posibles, siempre definidos (format falla si falta uno)
        "nombre": reco["nombre"],
        "genero": random.choice(reco["comunes"]) if reco["comunes"] else "cariño",
        "familiar": consejo.get("nombre", ""),
        "horas": consejo.get("horas", 0),
        "dueno": reco["duenos"][0] if reco["duenos"] else "alguien",
        "pct": pct or 0,
        "resto": 100 - (pct or 0),
    }
    especiales = []  # frases de las cosas especiales que tiene este juego
    if consejo:
        especiales += BIOS_PRIMO
    if reco.get("desconocido"):
        especiales += BIOS_PRESTAMO
    if reco.get("joya"):
        especiales += BIOS_JOYA
    if pct is not None and pct >= UMBRAL_ACLAMADO:
        especiales += BIOS_ACLAMADO
    fuente = especiales if especiales and random.random() < PROB_BIO_ESPECIAL else BIOS_GENERALES
    libres = [f for f in fuente if f not in usadas] or fuente  # sin repetir (si se agotan, se repite)
    plantilla = random.choice(libres)
    usadas.add(plantilla)
    return plantilla.format(**huecos)  # **huecos: cada clave rellena su {hueco}


def poner_bios(recomendados):
    """Añade una bio distinta a cada recomendación (modifica la lista y la devuelve)."""
    usadas = set()
    for r in recomendados:
        r["bio"] = bio(r, usadas)
    return recomendados


BIOS_ATREVIDO = [  # "¿Te atreves?": {nueva} = la etiqueta que nunca has jugado; {nombre} = el juego
    "«{nueva}» te da miedo. Normal. A mí me da miedo el Euríbor.",
    "Soy {nombre}, tu primera vez en «{nueva}». Seré delicado. O no.",
    "Sal de tu zona de confort. Total, tu zona de confort es un zulo de 25 m² en Madrid.",
    "Dicen que «{nueva}» no es lo tuyo. También decían que en Cádiz no subirían los alquileres.",
    "Un fondo buitre apostó a que nunca jugarías a «{nueva}». Hazle perder dinero.",
    "Si me juegas, un cangrejo de Cádiz aplaudirá. No sé por qué. Pero lo hará.",
    "Probar «{nueva}» es como mudarse de Madrid a Cádiz: vértigo al principio y luego no vuelves.",
    "El pato dice que estás preparado para «{nueva}». El pato nunca se equivoca.",
]


def poner_retos(atrevidos):
    """Añade a cada juego de "¿Te atreves?" una frase absurda distinta (modifica la lista y la devuelve)."""
    frases = random.sample(BIOS_ATREVIDO, len(BIOS_ATREVIDO))  # sample: todas, barajadas y sin repetir
    for i, r in enumerate(atrevidos):  # enumerate: da la posición (i) y el juego (r)
        # r["nuevas"][0]: su etiqueta nueva más votada; % len: si hubiera más juegos que frases, se repite
        r["reto"] = frases[i % len(frases)].format(nombre=r["nombre"], nueva=r["nuevas"][0])
    return atrevidos


PLANTILLAS_RULETA = [  # ruleta del caos (provisionales): {nombre}, {etiqueta}, {horas}, {duenos}
    "{nombre}. Una lagartija ha girado la ruleta por ti y ya no hay vuelta atrás.",
    "{nombre}, porque anoche soñaste con un pulpo con gorra que susurraba «{etiqueta}».",
    "Llevas {horas} con {nombre}. Un monje del Tíbet lleva lo mismo meditando sobre él.",
    "{nombre} es de {duenos}. Lo mínimo es abrirlo antes de que acabe el siglo.",
    "Juega a {nombre} con un calcetín en la mano. No ayuda, pero así puedes decir que lo hiciste.",
    "Si hoy no juegas a {nombre}, mañana tus calcetines amanecerán ordenados por colores.",
    "{nombre}: {horas} y un toque de «{etiqueta}», como un caracol en el microondas.",
    "La ruleta ha caído en {nombre}. La ruleta está trucada, pero no sabemos a favor de quién.",
]
SIN_ETIQUETA = "Misterio"  # para juegos sin etiquetas en Steam
TOP_ETIQUETAS_RULETA = 3  # la etiqueta del hueco sale al azar de entre estas más votadas


def juntar_nombres(nombres):
    """["Ana"] -> "Ana"; ["Ana", "Luis", "Juan"] -> "Ana, Luis y Juan"; [] -> "Alguien"."""
    if not nombres:  # lista vacía
        return "Alguien"
    if len(nombres) == 1:
        return nombres[0]
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]  # [:-1]: todos menos el último; [-1]: el último


def ruleta(juegos, etiquetas):
    """Todos los juegos, cada uno con una frase absurda ya rellenada (para la ruleta del caos).

    etiquetas: {appid: [etiquetas de más a menos votada]} (de get_tags). No modifica 'juegos'.
    """
    fichas = []
    for j in juegos:
        # Sus etiquetas más votadas sin las neutras (las que no dicen nada del juego)
        utiles = [e for e in etiquetas.get(j["appid"], []) if e not in ETIQUETAS_NEUTRAS]
        minutos = j.get("playtime_forever")  # None = desconocido (préstamo no jugado en 2 semanas)
        if minutos is None:
            horas = "un número secreto de horas"
        else:  # con 0 minutos, "0 h" (formatear daría "0,0")
            horas = f"{formatear(minutos / 60)} h" if minutos else "0 h"
        frase = random.choice(PLANTILLAS_RULETA).format(  # plantilla al azar con sus huecos rellenos
            nombre=j.get("name", "?"),
            etiqueta=random.choice(utiles[:TOP_ETIQUETAS_RULETA]) if utiles else SIN_ETIQUETA,
            horas=horas,
            duenos=juntar_nombres(j.get("duenos", [])),  # todos los dueños: "Ana, Luis y Juan"
        )
        fichas.append({"nombre": j.get("name", "?"), "appid": j["appid"], "frase": frase})
    return fichas


# ===================== Qué comprar (paso 5.2) =====================
TOP_ETIQUETAS_GUSTO = 5  # etiquetas de cada juego que cuentan (las más votadas, sin las neutras)
TOP_FAVORITAS = 5  # tus etiquetas favoritas que se usan en la búsqueda mainstream
RAREZAS = (6, 10)  # puestos de tus etiquetas (del 6.º al 10.º) que se mezclan con tus favoritas
MEZCLAS = 2  # búsquedas de mezclas raras (tu n.º 1 y tu n.º 2, cada una con una rareza al azar)
# Probado con una librería real: a peso completo estas salían arriba en casi todo y convertían la búsqueda
# en "cualquier juego popular". Cuentan, pero a mitad de peso y sin quitar hueco a las específicas.
ETIQUETAS_AMPLIAS = {
    "Acción", "Aventura", "Estrategia", "Rol", "Casuales", "Simulación", "Deportes", "Carreras", "Puzles",
}
PESO_AMPLIAS = 0.5  # las etiquetas amplias cuentan a la mitad (con 0,3 casi desaparecían)
# Avisos de contenido: no son un gusto (evita mezclas como "Estrategia + Contenido sexual")
ETIQUETAS_CONTENIDO = {"Contenido sexual", "Desnudos", "Hentai", "Sexual Themes", "Violentos", "Sangrientos"}
# Juegos que NO se recomiendan si alguna de estas está entre sus 5 etiquetas más votadas (la página
# puede verla la familia). La violencia no excluye
ETIQUETAS_ADULTAS = {"Contenido sexual", "Desnudos", "Hentai", "Sexual Themes"}
TOP_ADULTAS = 5  # cuántas etiquetas más votadas se miran para decidir si un juego es adulto
NO_SON_GUSTO = ETIQUETAS_NEUTRAS | ETIQUETAS_AMPLIAS | ETIQUETAS_CONTENIDO  # "|" une conjuntos


def principales(etiquetas_juego, n=TOP_ETIQUETAS_GUSTO):
    """Las n etiquetas más votadas de un juego que dicen algo de tus gustos (sin neutras, amplias
    ni avisos de contenido)."""
    return [e for e in etiquetas_juego if e not in NO_SON_GUSTO][:n]


def amplias(etiquetas_juego, n=TOP_ETIQUETAS_GUSTO):
    """Las etiquetas amplias del juego que están entre sus n más votadas (sin contar neutras ni avisos)."""
    utiles = [e for e in etiquetas_juego if e not in ETIQUETAS_NEUTRAS and e not in ETIQUETAS_CONTENIDO][:n]
    return [e for e in utiles if e in ETIQUETAS_AMPLIAS]


def tus_etiquetas(juegos, etiquetas):
    """Tus etiquetas favoritas: [(etiqueta, % de tus horas), ...] de mayor a menor.

    Solo juegos jugados de verdad (2 h o más) y con etiquetas. Cada una de sus etiquetas principales suma
    las horas COMPLETAS del juego (las amplias, a mitad de peso), así que los % no suman 100.
    """
    minutos_por = {}  # {etiqueta: minutos}
    total = 0  # minutos de los juegos que cuentan
    for j in juegos:
        minutos = j.get("playtime_forever") or 0  # "or 0": None (desconocido) cuenta como 0
        tags = etiquetas.get(j["appid"], [])
        suyas, anchas = principales(tags), amplias(tags)  # específicas y amplias, por separado
        if minutos < UMBRAL_ABANDONO or not (suyas or anchas):  # abandonado o sin etiquetas: no cuenta
            continue
        total += minutos
        for e in suyas:
            minutos_por[e] = minutos_por.get(e, 0) + minutos  # específicas: horas completas (.get: 0 si no estaba)
        for e in anchas:
            minutos_por[e] = minutos_por.get(e, 0) + minutos * PESO_AMPLIAS  # amplias: a la mitad
    if not total:
        return []
    pcts = [(e, round(m * 100 / total)) for e, m in minutos_por.items()]
    return sorted(pcts, key=lambda par: par[1], reverse=True)  # la que más pesa, primero


def mezclas_raras(favoritas, n=MEZCLAS):
    """Parejas [favorita, rareza] para buscar bizarras: tu n.º 1, tu n.º 2... cada una con una etiqueta
    al azar de tus puestos 6.º a 10.º (distinta en cada pareja). [] si tienes menos de 6 etiquetas."""
    nombres = [e for e, _ in favoritas]  # solo los nombres, sin los %
    rarezas = nombres[RAREZAS[0] - 1:RAREZAS[1]]  # [5:10] = puestos 6.º a 10.º
    elegidas = random.sample(rarezas, min(n, len(rarezas)))  # sample: distintas y al azar
    return [[nombres[i], rara] for i, rara in enumerate(elegidas)]  # i = 0 -> tu n.º 1, i = 1 -> tu n.º 2


UMBRAL_MAINSTREAM = 10000  # reseñas: mainstream con al menos estas; bizarras, con menos
MIN_RESENAS_BIZARRA = 50  # con menos, el % no es fiable: una "joya" con 3 reseñas puede ser cualquier cosa
MIN_PCT_BIZARRA = 80  # % de positivas mínimo de una bizarra (rara, pero buena)
PLUS_OFERTA = 0.2  # descuento del 100 % = puntos × 1,2; del 50 % = × 1,1 (el PRECIO no puntúa)
MAX_GRATIS = 1  # gratis como mucho por lista (abundan entre los populares)
TOP_MAINSTREAM, TOP_BIZARRAS = 6, 6  # 6: la rejilla queda completa (3 + 3, 2 + 2 + 2 o 1 por fila)
# Solo suman las 3 etiquetas en común que más pesan: si sumaran todas, ganarían siempre los juegos con
# MUCHAS etiquetas tuyas (gestión, estrategia) y un FPS puro nunca podría competir (probado con datos reales)
TOP_AFINIDAD = 3


def es_adulto(juego):
    """True si alguna de sus 5 etiquetas más votadas es de contenido sexual."""
    return any(e in ETIQUETAS_ADULTAS for e in juego["etiquetas"][:TOP_ADULTAS])


def candidatos_compra(tienda, tuyos):
    """Quita repetidos, los que ya tenéis tú o tu familia (tuyos: set de appids), los adultos
    y los que no están a la venta (sin precio y no gratis)."""
    vistos, lista = set(), []
    for j in tienda:
        if j["appid"] in tuyos or j["appid"] in vistos or es_adulto(j) or not (j["precio"] or j["gratis"]):
            continue
        vistos.add(j["appid"])
        lista.append(j)
    return lista


def puntuar_compra(juego, tus_pct):
    """Copia del juego con "puntos" = afinidad × nota de reseñas × plus de oferta, y "motivo"."""
    suyas = principales(juego["etiquetas"]) + amplias(juego["etiquetas"])  # las amplias ya pesan la mitad en tus_pct
    comunes = sorted((e for e in suyas if e in tus_pct), key=lambda e: tus_pct[e], reverse=True)
    comunes = comunes[:TOP_AFINIDAD]  # solo las 3 que más pesan (también son el motivo y la mezcla de variedad)
    afinidad = sum(tus_pct[e] for e in comunes)  # suma de tus % en lo que compartís
    pct = juego["pct"] if juego["resenas"] >= MIN_RESENAS_NOTA else None  # pocas reseñas: sin efecto
    oferta = 1 + PLUS_OFERTA * juego["descuento"] / 100  # gratis: descuento 0, así que × 1 (no gana nada)
    return {**juego, "puntos": afinidad * multiplicador_valoracion(pct) * oferta,
            "comunes": comunes, "motivo": [(e, tus_pct[e]) for e in comunes]}


def elegir_compra(puntuados, n, estudios):
    """Los n mejores: sin afinidad fuera, como mucho MAX_GRATIS gratis, 1 juego por desarrolladora
    (evita dos entregas de la misma saga) y con variedad (con_variedad).

    estudios: desarrolladoras ya elegidas en otra lista (set); se le añaden las de los elegidos.
    """
    random.shuffle(puntuados)  # a igualdad de puntos, al azar
    puntuados.sort(key=lambda r: r["puntos"], reverse=True)
    lista, gratis, vistos = [], 0, set(estudios)  # set(...): copia, para no tocar 'estudios' todavía
    for r in puntuados:
        if r["puntos"] <= 0:  # nada en común contigo
            continue
        suyos = set(r.get("desarrolladores", []))  # .get: los de la caché antigua no traen el campo
        if suyos & vistos:  # "&": estudios en común -> misma saga o mismo estudio: ya tiene representante
            continue
        if r["gratis"]:
            if gratis >= MAX_GRATIS:
                continue
            gratis += 1
        vistos |= suyos  # "|=": añade sus estudios a los vistos
        lista.append(r)
    elegidos = con_variedad(lista, n)
    for r in elegidos:
        estudios.update(r.get("desarrolladores", []))  # la otra lista ya no podrá repetirlos
    return elegidos


def que_comprar(populares, raras, favoritas, tuyos):
    """Qué comprar: {"mainstream": [...], "bizarras": [...]}.

    populares: búsqueda mainstream (buscar_tienda); raras: búsquedas de mezclas raras unidas en una lista;
    favoritas: tus_etiquetas(...); tuyos: appids de la librería unida (tú + familia).
    """
    tus_pct = dict(favoritas)  # {etiqueta: %}
    main = [puntuar_compra(j, tus_pct) for j in candidatos_compra(populares, tuyos)
            if j["resenas"] >= UMBRAL_MAINSTREAM]
    biz = [puntuar_compra(j, tus_pct) for j in candidatos_compra(raras, tuyos)
           if MIN_RESENAS_BIZARRA <= j["resenas"] < UMBRAL_MAINSTREAM and (j["pct"] or 0) >= MIN_PCT_BIZARRA]
    estudios = set()  # desarrolladoras ya recomendadas (compartido: primero mainstream, luego bizarras)
    return {"mainstream": elegir_compra(main, TOP_MAINSTREAM, estudios),
            "bizarras": elegir_compra(biz, TOP_BIZARRAS, estudios)}
