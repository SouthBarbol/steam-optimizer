# Capa de integración: el ÚNICO módulo que habla con Steam (conoce la API key y las URLs).
# Aquí no hay cálculos: solo pedir datos y devolverlos (los cálculos van en analysis.py).
import os  # para leer variables de entorno

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


def get_genres(appid):
    """Devuelve la lista de géneros (en español) de un juego, o None si no se pudo consultar."""
    if appid in _cache_generos:  # ¿ya lo pedimos antes?...
        return _cache_generos[appid]  # ...devolvemos lo guardado, sin llamar a Steam

    params = {"appids": appid, "filters": "genres", "l": "spanish"}  # solo géneros, en español
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
    _cache_generos[appid] = generos  # guardamos para no volver a pedirlo
    return generos
