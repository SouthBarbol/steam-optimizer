import re  # módulo de expresiones regulares, para validar el Steam ID

from flask import Flask, render_template, request  # render_template rellena una plantilla HTML con datos

from steam_service import get_owned_games, get_recently_played_games, unir_juegos, unir_familia  # funciones de steam_service.py

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
        familia = validar_familia(request.args.get("familia", ""), steam_id)  # lista de IDs limpios (aún no se usa: paso 0b)
    except ValueError as e:  # validar_familia lanza ValueError si algo no cuadra
        return render_template("index.html", error=str(e)), 400  # 400 = petición incorrecta

    try:  # intentamos pedir la librería a Steam
        propios = get_owned_games(steam_id)  # librería propia (+ gratuitos jugados)
        recientes = get_recently_played_games(steam_id)  # jugados en 2 semanas (incluye prestados)
        juegos = unir_juegos(propios, recientes)  # lista única, con la marca "propio"
    except RuntimeError as e:  # nuestro error limpio (sin la API key)
        return render_template("index.html", error=str(e)), 502  # 502 = fallo del servicio externo

    librerias, avisos = pedir_familia(familia)  # librerías de los familiares + avisos de los que fallen
    juegos = unir_familia(juegos, librerias)  # una fila por juego, con la lista de dueños

    if not juegos:  # lista vacía: perfil privado o sin juegos
        return render_template("index.html", error="No se encontraron juegos (¿perfil privado?).")

    return render_template("index.html", juegos=preparar_juegos(juegos))  # pasamos los juegos a la plantilla


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


def pedir_familia(familia):
    """Pide la librería de cada familiar; devuelve [(etiqueta, juegos), ...] y una lista de avisos."""
    librerias, avisos = [], []  # dos listas vacías que iremos llenando
    for n, fid in enumerate(familia, start=1):  # enumerate numera desde 1: Familiar 1, 2...
        etiqueta = f"Familiar {n}"  # en los avisos usamos la etiqueta, nunca el ID
        try:
            juegos_f = get_owned_games(fid)  # una llamada a Steam por familiar
        except RuntimeError:  # si falla, avisamos y seguimos con los demás
            avisos.append(f"{etiqueta}: no se pudo consultar su librería.")
            continue  # salta al siguiente familiar
        if not juegos_f:  # lista vacía: perfil privado o sin juegos
            avisos.append(f"{etiqueta}: perfil privado o sin juegos.")
        librerias.append((etiqueta, juegos_f))  # guardamos el par (etiqueta, juegos)
    return librerias, avisos


def preparar_juegos(juegos):
    """Convierte los datos de Steam en una lista simple (nombre, horas) ordenada por horas."""
    # Ordenamos de más a menos horas jugadas (playtime_forever está en minutos)
    ordenados = sorted(juegos, key=lambda j: j.get("playtime_forever", 0), reverse=True)
    return [  # un diccionario por juego, con solo lo que necesita la plantilla
        {
            "nombre": j.get("name", "?"),
            "horas": j.get("playtime_forever", 0) // 60,
            "propio": j.get("propio", True),  # True por defecto (la ruta /demo no trae este campo)
        }
        for j in ordenados
    ]


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
