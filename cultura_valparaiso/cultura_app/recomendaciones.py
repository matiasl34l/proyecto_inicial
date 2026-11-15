import math


def calcular_distancia(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, (lat1, lon1, lat2, lon2))
    diferencia_latitud = lat2 - lat1
    diferencia_longitud = lon2 - lon1
    a = (
        math.sin(diferencia_latitud / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(diferencia_longitud / 2) ** 2
    )
    a = min(1, max(0, a))
    return 6371 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def recomendar(usuario, eventos):
    lista = []
    gustos = set(usuario.gustos.filter(activo=True).values_list('nombre', flat=True))
    for evento in eventos:
        if not (
            math.isfinite(evento.latitud)
            and math.isfinite(evento.longitud)
            and -90 <= evento.latitud <= 90
            and -180 <= evento.longitud <= 180
        ):
            continue
        etiquetas_activas = getattr(evento, 'etiquetas_activas', None)
        if etiquetas_activas is None:
            etiquetas = set(
                evento.etiquetas.filter(activo=True).values_list('nombre', flat=True)
            )
        else:
            etiquetas = {etiqueta.nombre for etiqueta in etiquetas_activas}
        coincidencias = len(gustos & etiquetas)
        distancia = calcular_distancia(usuario.latitud, usuario.longitud, evento.latitud, evento.longitud)
        if coincidencias >= 2 and distancia <= usuario.distancia_maxima:
            lista.append({"evento": evento, "coincidencias": coincidencias, "distancia": round(distancia, 2)})
    lista.sort(key=lambda x: (-x["coincidencias"], x["distancia"]))
    return lista