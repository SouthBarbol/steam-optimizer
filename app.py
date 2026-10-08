import re  # módulo de expresiones regulares, para validar el Steam ID

from flask import Flask, render_template, request  # render_template rellena una plantilla HTML con datos

from steam_service import get_owned_games  # nuestra función que habla con la Steam API

app = Flask(__name__)  # crea la aplicación web


@app.route("/")  # esta función responde cuando se visita la raíz: http://127.0.0.1:5000/
def index():
    steam_id = request.args.get("steam_id", "")  # lee ?steam_id=... de la URL ("" si no viene)

    if not steam_id:  # si no se ha enviado ningún ID...
        return render_template("index.html")  # ...mostramos solo el formulario vacío

    if not re.fullmatch(r"\d{17}", steam_id):  # el ID debe ser exactamente 17 dígitos
        # 400 = petición incorrecta; "error" es la variable que usa la plantilla
        return render_template("index.html", error="Steam ID no válido: deben ser 17 dígitos."), 400

    try:  # intentamos pedir la librería a Steam
        juegos = get_owned_games(steam_id)
    except RuntimeError as e:  # nuestro error limpio (sin la API key)
        return render_template("index.html", error=str(e)), 502  # 502 = fallo del servicio externo

    if not juegos:  # lista vacía: perfil privado o sin juegos
        return render_template("index.html", error="No se encontraron juegos (¿perfil privado?).")

    return render_template("index.html", juegos=preparar_juegos(juegos))  # pasamos los juegos a la plantilla


def preparar_juegos(juegos):
    """Convierte los datos de Steam en una lista simple (nombre, horas) ordenada por horas."""
    # Ordenamos de más a menos horas jugadas (playtime_forever está en minutos)
    ordenados = sorted(juegos, key=lambda j: j.get("playtime_forever", 0), reverse=True)
    return [  # un diccionario por juego, con solo lo que necesita la plantilla
        {"nombre": j.get("name", "?"), "horas": j.get("playtime_forever", 0) // 60}
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
