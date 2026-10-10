import re  # módulo de expresiones regulares, para validar el Steam ID

from flask import Flask, render_template, request  # render_template rellena una plantilla HTML con datos

from analysis import candidatos_sorpresa, estadisticas, unir_juegos, unir_familia  # capa de lógica: cálculos sin red ni Flask
from steam_client import get_owned_games, get_recently_played_games, get_player_names  # capa de integración: llamadas a Steam

app = Flask(__name__)  # crea la aplicación web


@app.route("/")  # esta función responde cuando se visita la raíz: http://127.0.0.1:5000/
def index():
    steam_id = request.args.get("steam_id", "")  # lee ?steam_id=... de la URL ("" si no viene)

    if not steam_id:  # si no se ha enviado ningún ID...
        return render_template("index.html")  # ...mostramos solo el formulario vacío

    if not re.fullmatch(r"\d{17}", steam_id):  # el ID debe ser exactamente 17 dígitos
        # 400 = petición incorrecta; "error" es la variable que usa la plantilla
        return render_template("index.html", error="Steam ID no válido: deben ser 17 dígitos."), 400

    try:  # validamos los IDs de familiares (campo opcional)
        familia = validar_familia(request.args.get("familia", ""), steam_id)  # lista de IDs limpios
    except ValueError as e:  # validar_familia lanza ValueError si algo no cuadra
        return render_template("index.html", error=str(e)), 400  # 400 = petición incorrecta

    try:  # intentamos pedir la librería a Steam
        propios = get_owned_games(steam_id)  # librería propia (+ gratuitos jugados)
        recientes = get_recently_played_games(steam_id)  # jugados en 2 semanas (incluye prestados)
        juegos = unir_juegos(propios, recientes)  # lista única, con la marca "propio"
    except RuntimeError as e:  # nuestro error limpio (sin la API key)
        return render_template("index.html", error=str(e)), 502  # 502 = fallo del servicio externo

    try:  # nombres de Steam de todos (tú + familia) en UNA llamada
        nombres = get_player_names([steam_id] + familia)  # {steam_id: nombre}
    except RuntimeError:  # el nombre es cosmético: si falla, seguimos con etiquetas genéricas
        nombres = {}
    yo = nombres.get(steam_id) or "Tú"  # tu nombre de Steam; "Tú" si no llegó (o vino vacío)

    librerias, jugados, avisos = pedir_familia(familia, nombres, yo)  # ver la explicación en pedir_familia
    juegos = unir_familia(juegos, librerias, yo)  # una fila por juego, con la lista de dueños

    if not juegos:  # lista vacía: perfil privado o sin juegos
        return render_template("index.html", error="No se encontraron juegos (¿perfil privado?).")

    # Número fijo por dueño (tú = 0, familiar 1 = 1...) para que cada uno tenga siempre el mismo color
    colores = {yo: 0}  # tú siempre eres el color 0
    for n, (etiqueta, _) in enumerate(librerias, start=1):  # "_" = valor que no usamos (los juegos)
        colores[etiqueta] = n  # cada familiar recibe el siguiente número

    # Una tarjeta de estadísticas por persona: primero tú, luego cada familiar con librería
    # (usamos la lista original: preparar_juegos quita el campo "propio")
    tarjetas = [{"nombre": yo, "color": 0, "stats": estadisticas(juegos)}]
    for etiqueta, lista in jugados.items():  # .items() da pares (clave, valor) del diccionario
        if lista:  # sin juegos (perfil privado) no hay tarjeta; ya sale en los avisos
            # propios + recientes del familiar, con SUS horas (unir_juegos ya marca "propio")
            tarjetas.append({"nombre": etiqueta, "color": colores[etiqueta], "stats": estadisticas(lista)})

    # pasamos juegos, avisos (familiares que fallaron), colores y tarjetas a la plantilla
    return render_template(
        "index.html",
        juegos=preparar_juegos(juegos),
        avisos=avisos,
        colores=colores,
        tarjetas=tarjetas,
        candidatos=candidatos_sorpresa(juegos),  # juegos posibles para el "juego sorpresa"
    )


def validar_familia(texto, steam_id):
    """Convierte "id1, id2" en una lista de IDs válidos; lanza ValueError si alguno es incorrecto."""
    ids = [t.strip() for t in texto.split(",") if t.strip()]  # separa por comas, quita espacios y huecos vacíos
    ids = list(dict.fromkeys(i for i in ids if i != steam_id))  # quita tu propio ID y duplicados, conservando el orden
    if len(ids) > 5:  # límite para no hacer demasiadas llamadas a Steam
        raise ValueError("Como máximo 5 IDs de familiares.")
    for i in ids:  # revisamos cada ID por separado
        if not re.fullmatch(r"\d{17}", i):  # mismo criterio que tu Steam ID: exactamente 17 dígitos
            raise ValueError("ID de familiar no válido: deben ser 17 dígitos.")  # no repetimos el valor recibido
    return ids  # lista limpia (puede estar vacía)


def pedir_familia(familia, nombres, yo):
    """Pide los juegos de cada familiar. Devuelve tres cosas:

    librerias: [(etiqueta, juegos propios), ...] -> para saber quién es dueño de cada juego.
    jugados: {etiqueta: propios + recientes} -> solo para sus estadísticas (incluye préstamos jugados).
    avisos: mensajes de los familiares que fallaron.
    nombres: {steam_id: nombre de Steam}; yo: tu etiqueta (para no repetirla).
    """
    librerias, avisos = [], []  # dos listas vacías que iremos llenando
    jugados = {}  # diccionario vacío: etiqueta -> lista de juegos para estadísticas
    usadas = {yo}  # conjunto de etiquetas ya asignadas (empezando por la tuya)
    for n, fid in enumerate(familia, start=1):  # enumerate numera desde 1: Familiar 1, 2...
        etiqueta = nombres.get(fid) or f"Familiar {n}"  # su nombre de Steam, o genérico si no hay
        if etiqueta in usadas:  # nombre repetido: sus juegos y colores se mezclarían...
            etiqueta = f"{etiqueta} ({n})"  # ...así que le añadimos su número
        usadas.add(etiqueta)  # la marcamos como usada
        # en los avisos usamos la etiqueta, nunca el ID
        try:
            juegos_f = get_owned_games(fid)  # una llamada a Steam por familiar
        except RuntimeError:  # si falla, avisamos y seguimos con los demás
            avisos.append(f"{etiqueta}: no se pudo consultar su librería.")
            continue  # salta al siguiente familiar
        if not juegos_f:  # lista vacía: perfil privado o sin juegos
            avisos.append(f"{etiqueta}: perfil privado o sin juegos.")
        librerias.append((etiqueta, juegos_f))  # guardamos el par (etiqueta, juegos)

        try:  # sus juegos de las últimas 2 semanas (incluye préstamos): dato complementario
            recientes_f = get_recently_played_games(fid)  # una llamada más por familiar
        except RuntimeError:  # si falla, seguimos sin ellos (no hace falta avisar)
            recientes_f = []
        jugados[etiqueta] = unir_juegos(juegos_f, recientes_f)  # misma unión que hacemos contigo
    return librerias, jugados, avisos


def preparar_juegos(juegos):
    """Convierte los datos de Steam en una lista simple (appid, nombre, horas, dueños) ordenada por horas."""
    # Ordenamos de más a menos minutos; "or 0" convierte None (desconocido) en 0 para poder comparar
    ordenados = sorted(juegos, key=lambda j: j.get("playtime_forever") or 0, reverse=True)
    return [  # un diccionario por juego, con solo lo que necesita la plantilla
        {
            "appid": j.get("appid"),  # número del juego en Steam; sirve para la URL de la carátula (None en /demo)
            "nombre": j.get("name", "?"),
            "horas": horas_con_decimal(j.get("playtime_forever", 0)),  # p. ej. 126 min -> 2.1
            "duenos": j.get("duenos", ["Tú"]),  # ["Tú"] por defecto (la ruta /demo no trae este campo)
        }
        for j in ordenados
    ]


def horas_con_decimal(minutos):
    """Pasa minutos a horas con un decimal; devuelve None si el dato es desconocido."""
    if minutos is None:  # Steam no nos dio el dato (juego prestado)
        return None
    return round(minutos / 60, 1)  # round(x, 1) redondea a un decimal


@app.route("/demo")  # RUTA TEMPORAL: ver la página sin API key; borrar al terminar la fase 2
def demo():
    ejemplo = [  # juegos inventados con el mismo formato que devuelve Steam
        {"name": "Hollow Knight", "playtime_forever": 3000},
        {"name": "Hades", "playtime_forever": 1800},
        {"name": "<b>Prueba de escapado</b>", "playtime_forever": 60},  # Jinja2 debe mostrarlo como texto
    ]
    return render_template("index.html", juegos=preparar_juegos(ejemplo))


if __name__ == "__main__":  # solo si ejecutamos este archivo directamente (python app.py)
    app.run(debug=False)  # arranca el servidor con debug desactivado (seguridad)
