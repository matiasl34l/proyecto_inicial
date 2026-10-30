import math


def contar_coincidencias(gustos_usuario, etiquetas_evento):
    gustos = set(gustos_usuario.filter(activo=True).values_list("nombre", flat=True))
    etiquetas = set(etiquetas_evento.filter(activo=True).values_list("nombre", flat=True))
    return len(gustos & etiquetas)


def calcular_distancia(lat1, lon1, lat2, lon2):
    return math.sqrt((lat2 - lat1) ** 2 + (lon2 - lon1) ** 2) * 111


def recomendar(usuario, eventos):
    lista = []
    for evento in eventos:
        coincidencias = contar_coincidencias(usuario.gustos, evento.etiquetas)
        distancia = calcular_distancia(usuario.latitud, usuario.longitud, evento.latitud, evento.longitud)
        if coincidencias >= 2 and distancia <= usuario.distancia_maxima:
            lista.append({"evento": evento, "coincidencias": coincidencias, "distancia": round(distancia, 2)})
    lista.sort(key=lambda x: (-x["coincidencias"], x["distancia"]))
    return lista