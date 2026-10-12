# Capa de integración: el ÚNICO módulo que habla con Steam (conoce la API key y las URLs).
# Aquí no hay cálculos: solo pedir datos y devolverlos (los cálculos van en analysis.py).
import json  # para escribir la consulta de GetItems en formato JSON
import os  # para leer variables de entorno
import time  # para saber cuándo caduca la caché de la tienda

import requests  # librería para hacer peticiones HTTP
from dotenv import load_dotenv  # lee el archivo .env

load_dotenv()  # carga las variables de .env en el entorno

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
# Segunda caché con el nº de reseñas de cada juego {appid: nº o None}; se rellena a la vez que la de géneros
_cache_resenas = {}


def get_genres(appid):
    """Devuelve la lista de géneros (en español) de un juego, o None si no se pudo consultar."""
    if appid in _cache_generos:  # ¿ya lo pedimos antes?...
        return _cache_generos[appid]  # ...devolvemos lo guardado, sin llamar a Steam

    params = {"appids": appid, "filters": "genres,recommendations", "l": "spanish"}  # géneros (en español) y nº de reseñas
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
        _cache_resenas[appid] = (info.get("recommendations") or {}).get("total")  # nº de reseñas; None si Steam no lo da
    else:  # juego retirado o sin ficha: es un dato definitivo, no un fallo
        generos = []
    _cache_generos[appid] = generos  # guardamos para no volver a pedirlo
    return generos


def en_cache(appid):
    """True si los géneros de este juego ya están en la caché (pedirlos no llamará a Steam)."""
    return appid in _cache_generos


def get_resenas(appid):
    """Nº de reseñas de un juego ya consultado con get_genres (None si no se sabe). No llama a Steam."""
    return _cache_resenas.get(appid)


# URL (no oficial) con el resumen de reseñas de un juego; no necesita API key. {} = hueco para el appid
REVIEWS_URL = "https://store.steampowered.com/appreviews/{}"

# Caché en memoria: {appid: {"pct", "total"}}. Datos del JUEGO, no del usuario
_cache_valoraciones = {}


def get_valoracion(appid):
    """{"pct": % de reseñas positivas (None si no tiene), "total": nº de reseñas}, o None si falla la consulta."""
    if appid in _cache_valoraciones:  # ¿ya lo pedimos antes?
        return _cache_valoraciones[appid]

    # num_per_page=0: solo el resumen, sin descargar reseñas; language/purchase_type=all: todas
    params = {"json": 1, "language": "all", "purchase_type": "all", "num_per_page": 0}
    try:
        # int(appid): el appid va dentro de la URL; así nos aseguramos de que solo es un número
        respuesta = requests.get(REVIEWS_URL.format(int(appid)), params=params, timeout=10)
        respuesta.raise_for_status()  # error si Steam devolvió 4xx/5xx (p. ej. 429)
        resumen = (respuesta.json() or {}).get("query_summary") or {}
    except (requests.exceptions.RequestException, ValueError):  # red, código de error o JSON inválido
        return None  # fallo temporal: NO se guarda en caché

    total = resumen.get("total_reviews") or 0
    # % con el redondeo normal; sin reseñas no hay % (evita dividir entre 0)
    pct = round(resumen.get("total_positive", 0) / total * 100) if total else None
    _cache_valoraciones[appid] = {"pct": pct, "total": total}
    return _cache_valoraciones[appid]


# API OFICIAL de Steam con las etiquetas de los juegos (las ponen los jugadores); no necesita API key
ITEMS_URL = "https://api.steampowered.com/IStoreBrowseService/GetItems/v1/"
TAGLIST_URL = "https://api.steampowered.com/IStoreService/GetTagList/v1/"
LOTE_ETIQUETAS = 50  # juegos por llamada (probado con 61 sin problema)
_cache_etiquetas = {}  # {appid: [etiquetas en español, de más a menos votada]}; datos del JUEGO
_nombres_etiquetas = {}  # {número de etiqueta: nombre en español}; se pide una sola vez


def _cargar_nombres_etiquetas():
    """Pide a Steam los nombres de las ~450 etiquetas (solo la primera vez). True si los tenemos."""
    if not _nombres_etiquetas:  # diccionario vacío: aún no los hemos pedido (o falló)
        try:
            respuesta = requests.get(TAGLIST_URL, params={"language": "spanish"}, timeout=10)
            respuesta.raise_for_status()  # error si Steam devolvió 4xx/5xx
            lista = respuesta.json()["response"]["tags"]  # [{"tagid": 1667, "name": "Terror"}, ...]
        except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):  # red, JSON raro...
            return False  # sin nombres no podemos traducir: esta visita va sin etiquetas
        _nombres_etiquetas.update({t["tagid"]: t["name"] for t in lista})  # update: añade todos
    return True


def get_tags(appids):
    """{appid: [etiquetas, de más a menos votada]}, pidiendo a Steam por lotes de 50 solo lo que
    no está en caché. Si un lote falla, sus juegos no salen (se reintentan en otra visita)."""
    faltan = [a for a in dict.fromkeys(appids) if a not in _cache_etiquetas]  # sin repetidos ni los de caché
    if faltan and _cargar_nombres_etiquetas():
        for i in range(0, len(faltan), LOTE_ETIQUETAS):  # range(inicio, fin, paso): 0, 50, 100...
            lote = faltan[i:i + LOTE_ETIQUETAS]  # [i:i+50]: los 50 siguientes
            consulta = {
                "ids": [{"appid": int(a)} for a in lote],  # int(): solo números en la consulta
                "context": {"language": "spanish", "country_code": "ES"},
                "data_request": {"include_tag_count": 20},  # sus 20 etiquetas más votadas
            }
            try:
                respuesta = requests.get(ITEMS_URL, params={"input_json": json.dumps(consulta)}, timeout=15)
                respuesta.raise_for_status()
                items = respuesta.json()["response"].get("store_items", [])
            except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
                continue  # este lote falla: NO se guarda nada, se reintentará en otra visita
            for item in items:
                if item.get("success") == 1:  # 1 = juego con ficha en la tienda
                    # Ordenamos por votos ("weight"), de más a menos, y traducimos número -> nombre
                    votadas = sorted(item.get("tags", []), key=lambda t: t.get("weight", 0), reverse=True)
                    _cache_etiquetas[item["appid"]] = [
                        _nombres_etiquetas[t["tagid"]] for t in votadas if t["tagid"] in _nombres_etiquetas
                    ]
            for a in lote:  # los del lote que Steam no devolvió con ficha (retirados...): dato definitivo
                _cache_etiquetas.setdefault(a, [])  # setdefault: pone [] solo si no tiene ya etiquetas
    return {a: _cache_etiquetas[a] for a in appids if a in _cache_etiquetas}


# ===================== Tienda: buscar juegos para comprar (paso 5.1) =====================
# URL de la Web API de Steam que busca en la tienda (no necesita API key; ver "Resultado 5.0" en CLAUDE.md)
QUERY_URL = "https://api.steampowered.com/IStoreQueryService/Query/v1/"
ORDEN_POPULARES = 10  # valores de "sort" SIN documentar, deducidos probando: 10 = más populares...
ORDEN_VALORADOS = 21  # ...y 21 = mejor valorados
CADUCIDAD_TIENDA = 3 * 3600  # segundos: los precios y las ofertas cambian, así que la caché caduca a las 3 h
_cache_tienda = {}  # {búsqueda: (momento en que se guardó, juegos)}; datos de la tienda, no del usuario


def _ficha_tienda(item):
    """Convierte un juego de la respuesta de Steam en un diccionario sencillo."""
    compra = item.get("best_purchase_option") or {}  # la mejor forma de comprarlo ({} si no se vende)
    resenas = (item.get("reviews") or {}).get("summary_filtered") or {}
    votadas = sorted(item.get("tags", []), key=lambda t: t.get("weight", 0), reverse=True)  # más votadas primero
    return {
        "appid": item["appid"],
        "nombre": item.get("name", "?"),
        "precio": compra.get("formatted_final_price"),  # "19,99€"; None = gratis o no está a la venta
        "precio_original": compra.get("formatted_original_price"),  # solo viene si hay descuento
        "descuento": compra.get("discount_pct", 0),  # % de descuento (0 = sin oferta)
        "resenas": resenas.get("review_count", 0),
        "pct": resenas.get("percent_positive"),  # % de reseñas positivas
        "etiquetas": [_nombres_etiquetas[t["tagid"]] for t in votadas if t["tagid"] in _nombres_etiquetas],
    }


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
    guardado = _cache_tienda.get(clave)
    if guardado and time.time() - guardado[0] < CADUCIDAD_TIENDA:  # está y no ha caducado
        return guardado[1]
    # Dentro de un grupo vale CUALQUIERA de sus etiquetas; entre grupos hacen falta TODOS
    grupos = [{"tagids": [t]} for t in tagids] if todas else [{"tagids": tagids}]
    consulta = {
        "query": {
            "start": 0, "count": cantidad, "sort": orden,
            "filters": {
                "released_only": True,  # sin esto salen juegos "Próximamente", sin precio
                "type_filters": {"include_games": True},  # solo juegos (ni DLC, ni bandas sonoras...)
                "tagids_must_match": grupos,
            },
        },
        "context": {"language": "spanish", "country_code": "ES"},  # textos en español y precios en euros
        "data_request": {"include_all_purchase_options": True, "include_reviews": True, "include_tag_count": 20},
    }
    try:
        respuesta = requests.get(QUERY_URL, params={"input_json": json.dumps(consulta)}, timeout=15)
        respuesta.raise_for_status()
        items = respuesta.json()["response"].get("store_items", [])
    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):  # red, JSON raro...
        return None
    juegos = [_ficha_tienda(i) for i in items if i.get("success") == 1 and "appid" in i]
    ahora = time.time()
    for k in [k for k, (momento, _) in _cache_tienda.items() if ahora - momento >= CADUCIDAD_TIENDA]:
        del _cache_tienda[k]  # limpieza: fuera las búsquedas caducadas (la memoria no crece sin fin)
    _cache_tienda[clave] = (ahora, juegos)
    return juegos
