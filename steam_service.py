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
