# Capa de lógica: funciones puras (reciben datos y devuelven datos).
# Aquí NO se importa Flask ni se hacen peticiones a Steam.


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

    return {  # diccionario con todo lo que mostrará la plantilla
        "total_propios": total_propios,
        "sin_jugar": sin_jugar,
        # porcentaje con un decimal; si no tienes juegos evitamos dividir entre 0
        "pile_pct": round(sin_jugar / total_propios * 100, 1) if total_propios else 0,
        "abandonados": abandonados,
        "horas": round(horas),  # horas enteras
        "dias": round(horas / 24, 1),  # días seguidos jugando
        "pct_anio": round(horas / (365 * 24) * 100, 1),  # porcentaje de un año entero
        "peliculas": round(horas / 2),  # películas de 2 horas que podrías haber visto
    }
