# Capa de integración: el ÚNICO módulo que habla con Steam (conoce la API key y las URLs).
# Aquí no hay cálculos: solo pedir datos y devolverlos (los cálculos van en analysis.py).
import json  # para escribir la consulta de GetItems en formato JSON
import os  # para leer variables de entorno
import random  # para elegir un punto al azar del catálogo de la tienda
import threading  # hilos: cerrojo (Lock) y semáforo para las consultas en paralelo (paso 3)
import time  # para saber cuándo caduca la caché de la tienda
from concurrent.futures import ThreadPoolExecutor  # reparte tareas entre varios hilos

import requests  # librería para hacer peticiones HTTP
from dotenv import load_dotenv  # lee el archivo .env

load_dotenv()  # carga las variables de .env en el entorno

# ===================== Consultas en paralelo (paso 3) =====================
MAX_A_LA_VEZ = 5  # peticiones simultáneas a Steam como máximo en TODO el servidor (evita el error 429)
# Semáforo: 5 "llaves"; cada petición en paralelo coge una y la devuelve al terminar.
# Bounded: da error si alguien devuelve una llave de más (sería un fallo de programación)
_semaforo_steam = threading.BoundedSemaphore(MAX_A_LA_VEZ)


def en_paralelo(funcion, elementos):
    """Como [funcion(e) for e in elementos], pero a la vez y con los resultados en el mismo orden.
    Cada llamada espera turno en el semáforo (como mucho MAX_A_LA_VEZ en todo el servidor).

    Reglas para no romper nada:
    - funcion NO debe escribir nada compartido: solo devolver su resultado.
    - funcion NO debe llamar a en_paralelo ni a get_genres_varios: tendría cogida una llave mientras
      espera otras, y si las 5 están cogidas así, nadie avanza nunca (deadlock).
    """
    def con_turno(elemento):  # función dentro de otra: solo se usa aquí
        with _semaforo_steam:  # coge una llave; al salir del with la devuelve (aunque haya error)
            return funcion(elemento)
    with ThreadPoolExecutor(max_workers=MAX_A_LA_VEZ) as hilos:  # al salir, espera a que acaben todos
        return list(hilos.map(con_turno, elementos))  # map: resultados en el orden de "elementos"

# URL del endpoint de Steam que lista los juegos de un usuario
OWNED_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"


def get_owned_games(steam_id):  # recibe el Steam ID de 17 dígitos
    """Devuelve la lista de juegos de un usuario (perfil público)."""
    api_key = os.getenv("STEAM_API_KEY")  # lee la key desde el entorno (viene de .env)
    if not api_key:  # si no está definida...
        raise RuntimeError("Falta STEAM_API_KEY en el archivo .env")  # ...avisamos

    params = {  # parámetros que requests añadirá a la URL
        "key": api_key,
        "steamid": steam_id,
        "include_appinfo": 1,  # incluye el nombre de cada juego
        "include_played_free_games": 1,  # incluye también los juegos gratuitos que has jugado
        "format": "json",
    }
    try:  # intenta hacer la petición; si algo falla, salta al except
        respuesta = requests.get(OWNED_GAMES_URL, params=params, timeout=10)  # GET a Steam, máx. 10 s
        respuesta.raise_for_status()  # lanza error si Steam devolvió 4xx/5xx
    except requests.exceptions.HTTPError as e:  # Steam respondió con un código de error
        # Solo mostramos el código (e.response.status_code), nunca la URL, porque lleva la API key
        raise RuntimeError(f"Steam devolvió un error HTTP {e.response.status_code}") from None
    except requests.exceptions.RequestException:  # fallo de red, timeout, etc.
        # Mensaje genérico: el error original podría contener la URL con la key
        raise RuntimeError("No se pudo conectar con Steam") from None

    # .json() convierte la respuesta en diccionario; .get(...) evita fallar si falta una clave
    # Si el perfil es privado, "games" no existe y devolvemos una lista vacía
    return respuesta.json().get("response", {}).get("games", [])


# URL del endpoint de Steam que lista los juegos jugados en las últimas 2 semanas
RECENT_GAMES_URL = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/"


def get_recently_played_games(steam_id):  # recibe el Steam ID de 17 dígitos
    """Devuelve los juegos jugados en las últimas 2 semanas (incluye los de biblioteca familiar)."""
    api_key = os.getenv("STEAM_API_KEY")  # lee la key desde el entorno (viene de .env)
    if not api_key:  # si no está definida...
        raise RuntimeError("Falta STEAM_API_KEY en el archivo .env")  # ...avisamos

    params = {  # parámetros que requests añadirá a la URL
        "key": api_key,
        "steamid": steam_id,
        "format": "json",
    }
    try:  # intenta hacer la petición; si algo falla, salta al except
        respuesta = requests.get(RECENT_GAMES_URL, params=params, timeout=10)  # GET a Steam, máx. 10 s
        respuesta.raise_for_status()  # lanza error si Steam devolvió 4xx/5xx
    except requests.exceptions.HTTPError as e:  # Steam respondió con un código de error
        # Solo mostramos el código, nunca la URL, porque lleva la API key
        raise RuntimeError(f"Steam devolvió un error HTTP {e.response.status_code}") from None
    except requests.exceptions.RequestException:  # fallo de red, timeout, etc.
        # Mensaje genérico: el error original podría contener la URL con la key
        raise RuntimeError("No se pudo conectar con Steam") from None

    # Si no hay juegos recientes (o el perfil es privado), "games" no existe y devolvemos []
    return respuesta.json().get("response", {}).get("games", [])


# URL del endpoint de Steam que devuelve datos públicos de perfiles (entre ellos el nombre)
PLAYER_SUMMARIES_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"


def get_player_names(steam_ids):  # recibe una lista de Steam IDs (máx. 100)
    """Devuelve {steam_id: nombre de Steam} con UNA sola llamada para todos los IDs."""
    api_key = os.getenv("STEAM_API_KEY")  # lee la key desde el entorno (viene de .env)
    if not api_key:  # si no está definida...
        raise RuntimeError("Falta STEAM_API_KEY en el archivo .env")  # ...avisamos

    params = {  # parámetros que requests añadirá a la URL
        "key": api_key,
        "steamids": ",".join(steam_ids),  # une la lista en un texto: "id1,id2,id3"
        "format": "json",
    }
    try:  # intenta hacer la petición; si algo falla, salta al except
        respuesta = requests.get(PLAYER_SUMMARIES_URL, params=params, timeout=10)  # GET a Steam, máx. 10 s
        respuesta.raise_for_status()  # lanza error si Steam devolvió 4xx/5xx
    except requests.exceptions.HTTPError as e:  # Steam respondió con un código de error
        # Solo mostramos el código, nunca la URL, porque lleva la API key
        raise RuntimeError(f"Steam devolvió un error HTTP {e.response.status_code}") from None
    except requests.exceptions.RequestException:  # fallo de red, timeout, etc.
        # Mensaje genérico: el error original podría contener la URL con la key
        raise RuntimeError("No se pudo conectar con Steam") from None

    jugadores = respuesta.json().get("response", {}).get("players", [])  # lista de perfiles encontrados
    # Diccionario por comprensión: para cada perfil, su ID -> su nombre visible ("personaname")
    return {p["steamid"]: p.get("personaname", "") for p in jugadores}


# URL (no oficial) de la tienda de Steam con los datos de un juego; no necesita API key
STORE_DETAILS_URL = "https://store.steampowered.com/api/appdetails"

# Caché en memoria: {appid: [géneros]}. Son datos del JUEGO, no del usuario.
# Vive mientras el servidor está encendido; al reiniciarlo se vacía.
_cache_generos = {}
_cerrojo_generos = threading.Lock()  # protege _cache_generos: varios hilos la leen y escriben a la vez


def get_genres(appid):
    """Devuelve la lista de géneros (en español) de un juego, o None si no se pudo consultar."""
    with _cerrojo_generos:  # leer la caché: con el cerrojo, por si otro hilo está escribiendo
        if appid in _cache_generos:  # ¿ya lo pedimos antes?...
            return _cache_generos[appid]  # ...devolvemos lo guardado, sin llamar a Steam (el with suelta el cerrojo)

    # La petición va FUERA del cerrojo: si no, los hilos irían de uno en uno y no ganaríamos nada
    params = {"appids": appid, "filters": "genres", "l": "spanish"}  # solo los géneros (en español)
    try:  # intenta hacer la petición; si algo falla, salta al except
        respuesta = requests.get(STORE_DETAILS_URL, params=params, timeout=10)  # GET a la tienda, máx. 10 s
        respuesta.raise_for_status()  # error si Steam devolvió 4xx/5xx (p. ej. 429 = demasiadas peticiones)
        cuerpo = respuesta.json() or {}  # "or {}": a veces Steam responde "null" cuando le saturamos
    except (requests.exceptions.RequestException, ValueError):  # red, código de error o JSON inválido
        return None  # fallo temporal: NO se guarda en caché, así se reintenta la próxima vez

    datos = cuerpo.get(str(appid), {})  # la clave de la respuesta es el appid como texto
    if datos.get("success"):  # el juego tiene ficha en la tienda
        info = datos.get("data") or {}  # "or {}": si no tiene géneros, Steam manda una lista vacía
        generos = [g["description"] for g in info.get("genres", [])]  # solo los nombres
    else:  # juego retirado o sin ficha: es un dato definitivo, no un fallo
        generos = []
    with _cerrojo_generos:  # escribir: un hilo cada vez
        _cache_generos[appid] = generos  # guardamos para no volver a pedirlo
    return generos


def _generos_con_turno(appid):
    """get_genres esperando turno en el semáforo (se ejecuta en un hilo)."""
    with _semaforo_steam:  # como mucho MAX_A_LA_VEZ peticiones en marcha en todo el servidor
        return get_genres(appid)


def get_genres_varios(appids):
    """{appid: géneros, o None si falló} de varios juegos, pedidos a la vez (paso 3.2)."""
    unicos = list(dict.fromkeys(appids))  # sin repetidos: cada juego lo pide un solo hilo
    with ThreadPoolExecutor(max_workers=MAX_A_LA_VEZ) as hilos:  # al salir, espera a que acaben todos
        # map devuelve los resultados en el mismo orden que unicos; zip los empareja con su appid
        return dict(zip(unicos, hilos.map(_generos_con_turno, unicos)))


# API OFICIAL de Steam con las etiquetas de los juegos (las ponen los jugadores); no necesita API key
ITEMS_URL = "https://api.steampowered.com/IStoreBrowseService/GetItems/v1/"
TAGLIST_URL = "https://api.steampowered.com/IStoreService/GetTagList/v1/"
LOTE_ETIQUETAS = 50  # juegos por llamada (probado con 61 sin problema)
_cache_etiquetas = {}  # {appid: [etiquetas en español, de más a menos votada]}; datos del JUEGO
_cache_valoraciones = {}  # {appid: {"total": nº de reseñas, "pct": % positivas o None}}; datos del JUEGO
_nombres_etiquetas = {}  # {número de etiqueta: nombre en español}; se pide una sola vez
_cerrojo_etiquetas = threading.Lock()  # protege _cache_etiquetas y _cache_valoraciones (varias visitas a la vez)
_cerrojo_nombres = threading.Lock()  # protege _nombres_etiquetas mientras se cargan (la primera vez)


def _cargar_nombres_etiquetas():
    """Pide a Steam los nombres de las ~450 etiquetas (solo la primera vez). True si los tenemos.
    Con cerrojo: si dos visitas llegan a la vez, la segunda espera y encuentra los nombres ya cargados,
    en vez de leerlos a medio escribir."""
    with _cerrojo_nombres:
        if not _nombres_etiquetas:  # diccionario vacío: aún no los hemos pedido (o falló)
            try:
                respuesta = requests.get(TAGLIST_URL, params={"language": "spanish"}, timeout=10)
                respuesta.raise_for_status()  # error si Steam devolvió 4xx/5xx
                lista = respuesta.json()["response"]["tags"]  # [{"tagid": 1667, "name": "Terror"}, ...]
            except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):  # red, JSON raro...
                return False  # sin nombres no podemos traducir: esta visita va sin etiquetas
            _nombres_etiquetas.update({t["tagid"]: t["name"] for t in lista})  # update: añade todos
        return True


def _pedir_lote_etiquetas(lote):
    """Etiquetas y reseñas de un lote de hasta 50 juegos (se ejecuta en un hilo). No toca nada compartido:
    devuelve {appid: (etiquetas, valoración)} de los que tienen ficha, o None si el lote falla."""
    consulta = {
        "ids": [{"appid": int(a)} for a in lote],  # int(): solo números en la consulta
        "context": {"language": "spanish", "country_code": "ES"},
        # sus 20 etiquetas más votadas + sus reseñas (vienen en el mismo lote: gratis)
        "data_request": {"include_tag_count": 20, "include_reviews": True},
    }
    try:
        respuesta = requests.get(ITEMS_URL, params={"input_json": json.dumps(consulta)}, timeout=15)
        respuesta.raise_for_status()
        items = respuesta.json()["response"].get("store_items", [])
    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
        return None  # este lote falla: no se guarda nada, se reintentará en otra visita
    datos = {}  # diccionario LOCAL de este hilo: nadie más lo ve
    for item in items:
        if item.get("success") == 1:  # 1 = juego con ficha en la tienda
            # Ordenamos por votos ("weight"), de más a menos, y traducimos número -> nombre (solo lectura)
            votadas = sorted(item.get("tags", []), key=lambda t: t.get("weight", 0), reverse=True)
            etiquetas = [_nombres_etiquetas[t["tagid"]] for t in votadas if t["tagid"] in _nombres_etiquetas]
            # summary_filtered: reseñas sin las "fuera de tema" (p. ej. bombardeos de reseñas)
            resenas = (item.get("reviews") or {}).get("summary_filtered") or {}
            valoracion = {"total": resenas.get("review_count", 0), "pct": resenas.get("percent_positive")}
            datos[item["appid"]] = (etiquetas, valoracion)
    return datos


def get_tags(appids):
    """{appid: [etiquetas, de más a menos votada]}, pidiendo a Steam por lotes de 50 solo lo que
    no está en caché. Si un lote falla, sus juegos no salen (se reintentan en otra visita).
    Los lotes se piden a la vez (paso 3.4). No llamarla desde en_paralelo (deadlock)."""
    with _cerrojo_etiquetas:  # leer qué falta: con el cerrojo, por si otra visita está escribiendo
        faltan = [a for a in dict.fromkeys(appids) if a not in _cache_etiquetas]  # sin repetidos ni los de caché
    if faltan and _cargar_nombres_etiquetas():  # nombres cargados ANTES de los hilos: ellos solo los leen
        # [i:i+50] para i = 0, 50, 100...: los lotes de 50
        lotes = [faltan[i:i + LOTE_ETIQUETAS] for i in range(0, len(faltan), LOTE_ETIQUETAS)]
        resultados = en_paralelo(_pedir_lote_etiquetas, lotes)  # varios lotes a la vez, resultados en orden
        with _cerrojo_etiquetas:  # escribir: solo este hilo, todo de una vez
            for lote, datos in zip(lotes, resultados):  # zip: cada lote con su resultado
                if datos is None:  # lote fallido: sus juegos no se guardan (se reintentan en otra visita)
                    continue
                for appid, (etiquetas, valoracion) in datos.items():
                    _cache_etiquetas[appid] = etiquetas
                    _cache_valoraciones[appid] = valoracion
                for a in lote:  # los del lote que Steam no devolvió con ficha (retirados...): dato definitivo
                    _cache_etiquetas.setdefault(a, [])  # setdefault: pone [] solo si no tiene ya etiquetas
    with _cerrojo_etiquetas:  # leer el resultado: con el cerrojo
        return {a: _cache_etiquetas[a] for a in appids if a in _cache_etiquetas}


def get_valoraciones(appids):
    """{appid: {"total", "pct"}} de los juegos ya pedidos con get_tags (vienen en el mismo lote).
    No llama a Steam: los juegos sin datos (retirados de la tienda o lote fallido) no salen."""
    with _cerrojo_etiquetas:  # leer con el cerrojo, por si otra visita está escribiendo
        return {a: _cache_valoraciones[a] for a in appids if a in _cache_valoraciones}


# ===================== Tienda: buscar juegos para comprar (paso 5.1) =====================
# URL de la Web API de Steam que busca en la tienda (no necesita API key; ver "Resultado 5.0" en CLAUDE.md)
QUERY_URL = "https://api.steampowered.com/IStoreQueryService/Query/v1/"
ORDEN_POPULARES = 10  # valores de "sort" SIN documentar, deducidos probando: 10 = más populares...
ORDEN_VALORADOS = 21  # ...y 21 = mejor valorados
CADUCIDAD_TIENDA = 3 * 3600  # segundos: los precios y las ofertas cambian, así que la caché caduca a las 3 h
_cache_tienda = {}  # {búsqueda: (momento en que se guardó, juegos)}; datos de la tienda, no del usuario
_cerrojo_tienda = threading.Lock()  # protege _cache_tienda (varias búsquedas y visitas a la vez)


def _ficha_tienda(item):
    """Convierte un juego de la respuesta de Steam en un diccionario sencillo."""
    compra = item.get("best_purchase_option") or {}  # la mejor forma de comprarlo ({} si no se vende)
    resenas = (item.get("reviews") or {}).get("summary_filtered") or {}
    votadas = sorted(item.get("tags", []), key=lambda t: t.get("weight", 0), reverse=True)  # más votadas primero
    fecha = (item.get("release") or {}).get("steam_release_date")  # segundos desde 1970 (None si no la da)
    return {
        "anio": time.gmtime(fecha).tm_year if fecha else None,  # gmtime: segundos -> fecha; tm_year: su año
        "appid": item["appid"],
        "nombre": item.get("name", "?"),
        "precio": compra.get("formatted_final_price"),  # "19,99€"; None = gratis o no está a la venta
        "precio_original": compra.get("formatted_original_price"),  # solo viene si hay descuento
        "descuento": compra.get("discount_pct", 0),  # % de descuento (0 = sin oferta)
        "gratis": item.get("is_free") is True,  # free-to-play (no traen precio)
        # Nombres de los estudios que lo hicieron ([] si Steam no los da)
        "desarrolladores": [d["name"] for d in (item.get("basic_info") or {}).get("developers", []) if d.get("name")],
        "resenas": resenas.get("review_count", 0),
        "pct": resenas.get("percent_positive"),  # % de reseñas positivas
        "etiquetas": [_nombres_etiquetas[t["tagid"]] for t in votadas if t["tagid"] in _nombres_etiquetas],
    }


def _pedir_tienda(query):
    """Hace UNA búsqueda en la tienda. query: qué buscar (start, count, sort, filters).

    Devuelve (juegos, total de coincidencias); None si falla. Siempre solo juegos ya publicados.
    """
    query["filters"].update({
        "released_only": True,  # sin esto salen juegos "Próximamente", sin precio
        "type_filters": {"include_games": True},  # solo juegos (ni DLC, ni bandas sonoras...)
    })
    consulta = {
        "query": query,
        "context": {"language": "spanish", "country_code": "ES"},  # textos en español y precios en euros
        "data_request": {"include_all_purchase_options": True, "include_reviews": True, "include_tag_count": 20,
                         "include_basic_info": True,  # basic_info: desarrolladores (para no repetir sagas)
                         "include_release": True},  # release: fecha de lanzamiento (el año)
    }
    try:
        respuesta = requests.get(QUERY_URL, params={"input_json": json.dumps(consulta)}, timeout=15)
        respuesta.raise_for_status()
        datos = respuesta.json()["response"]
        items = datos.get("store_items", [])
        total = datos.get("metadata", {}).get("total_matching_records", 0)
    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):  # red, JSON raro...
        return None
    return [_ficha_tienda(i) for i in items if i.get("success") == 1 and "appid" in i], total


def buscar_tienda(etiquetas, todas=False, orden=ORDEN_POPULARES, cantidad=100):
    """Juegos YA publicados de la tienda con esas etiquetas (nombres en español), con precio en euros.

    todas=False: con ALGUNA de las etiquetas; todas=True: con TODAS a la vez (mezclas raras).
    Devuelve una lista de diccionarios (ver _ficha_tienda); [] si ninguna etiqueta existe;
    None si falla la consulta (no se guarda en caché).
    """
    if not _cargar_nombres_etiquetas():  # sin la lista de etiquetas no podemos traducir nombres a números
        return None
    numero_de = {nombre: tagid for tagid, nombre in _nombres_etiquetas.items()}  # al revés: nombre -> número
    tagids = sorted({numero_de[e] for e in etiquetas if e in numero_de})  # {}: sin repetidos; sorted: mismo orden
    if not tagids:
        return []
    clave = (tuple(tagids), todas, orden, cantidad)  # tupla: puede ser clave de diccionario (una lista no)
    with _cerrojo_tienda:  # leer la caché con el cerrojo, por si otro hilo está escribiendo o limpiando
        guardado = _cache_tienda.get(clave)
    if guardado and time.time() - guardado[0] < CADUCIDAD_TIENDA:  # está y no ha caducado
        return guardado[1]
    # Dentro de un grupo vale CUALQUIERA de sus etiquetas; entre grupos hacen falta TODOS
    grupos = [{"tagids": [t]} for t in tagids] if todas else [{"tagids": tagids}]
    respuesta = _pedir_tienda({"start": 0, "count": cantidad, "sort": orden,
                               "filters": {"tagids_must_match": grupos}})
    if respuesta is None:  # falló: no se guarda nada
        return None
    juegos = respuesta[0]  # [0]: los juegos ([1] sería el total, que aquí no hace falta)
    # Limpiar y escribir: un hilo cada vez. Sin el cerrojo, si otra visita añadía una búsqueda mientras
    # este bucle recorría la caché, Python fallaba ("dictionary changed size during iteration")
    with _cerrojo_tienda:
        ahora = time.time()
        for k in [k for k, (momento, _) in _cache_tienda.items() if ahora - momento >= CADUCIDAD_TIENDA]:
            del _cache_tienda[k]  # limpieza: fuera las búsquedas caducadas (la memoria no crece sin fin)
        _cache_tienda[clave] = (ahora, juegos)
    return juegos


_total_catalogo = []  # [(momento en que se guardó, nº de juegos publicados)]: dato de la tienda, no del usuario


def tienda_al_azar(cantidad=50):
    """'cantidad' juegos seguidos desde un punto al azar de TODO el catálogo publicado (paso 5.4).

    El total del catálogo se guarda 3 h; los juegos no (cada visita cae en otro sitio). None si falla.
    """
    if not _total_catalogo or time.time() - _total_catalogo[0][0] >= CADUCIDAD_TIENDA:  # no está o caducó
        respuesta = _pedir_tienda({"start": 0, "count": 1, "filters": {}})  # solo queremos el total
        if respuesta is None or not respuesta[1]:
            return None
        _total_catalogo[:] = [(time.time(), respuesta[1])]  # [:] = sustituye el contenido de la lista
    _cargar_nombres_etiquetas()  # para traducir sus etiquetas (si falla, saldrán sin etiquetas)
    inicio = random.randrange(max(_total_catalogo[0][1] - cantidad, 1))  # randrange(n): de 0 a n-1, al azar
    respuesta = _pedir_tienda({"start": inicio, "count": cantidad, "filters": {}})
    return None if respuesta is None else respuesta[0]


# ===================== Tienda: los más vendidos de siempre (paso 5.6, el juego malísimo) =====================
ORDEN_VENDIDOS = 11  # ...y 11 = más vendidos de siempre (también deducido; trae clásicos, no solo novedades)
PAGINAS_VENDIDOS = 5  # páginas de 1.000 juegos (~2 s cada una)
CADUCIDAD_VENDIDOS = 24 * 3600  # esta lista apenas cambia: se guarda 1 día
_cache_vendidos = []  # [(momento en que se guardó, juegos)]: datos de la tienda, no del usuario
_cerrojo_vendidos = threading.Lock()  # solo una visita a la vez puede rellenar la caché de los más vendidos


def _pagina_vendidos(pagina):
    """Pide UNA página de los más vendidos (se ejecuta en un hilo). No toca nada compartido: solo devuelve."""
    with _semaforo_steam:  # espera turno si ya hay 5 peticiones en marcha; al salir del with, devuelve la llave
        return _pedir_tienda({"start": pagina * 1000, "count": 1000, "sort": ORDEN_VENDIDOS, "filters": {}})


def mas_vendidos():
    """Los 5.000 juegos más vendidos de siempre (paso 5.6), guardados 24 h. None si falla.
    Las 5 páginas se piden a la vez (paso 3.1)."""
    with _cerrojo_vendidos:  # si otra visita ya los está pidiendo, esta espera y luego usa su caché
        if _cache_vendidos and time.time() - _cache_vendidos[0][0] < CADUCIDAD_VENDIDOS:  # está y no ha caducado
            return _cache_vendidos[0][1]
        # Sin etiquetas no se pueden quitar los adultos: mejor nada. Se cargan ANTES de los hilos,
        # así ellos solo LEEN los nombres (nadie escribe mientras otros leen)
        if not _cargar_nombres_etiquetas():
            return None
        with ThreadPoolExecutor(max_workers=PAGINAS_VENDIDOS) as hilos:  # al salir, espera a que acaben todos
            # map: reparte las páginas 0-4 entre los hilos y devuelve los resultados EN ORDEN de página
            respuestas = list(hilos.map(_pagina_vendidos, range(PAGINAS_VENDIDOS)))
        if any(r is None for r in respuestas):  # falla alguna página: no se guarda nada (se reintenta otra visita)
            return None
        juegos = [j for r in respuestas for j in r[0]]  # junta las 5 páginas (r[0]: los juegos de cada una)
        _cache_vendidos[:] = [(time.time(), juegos)]  # [:] = sustituye el contenido; solo escribe este hilo, con el cerrojo
        return juegos
