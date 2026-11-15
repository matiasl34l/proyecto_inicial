import json
import math
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import PreferenciasForm, RegistroForm
from .models import Etiqueta, Evento, Usuario
from .recomendaciones import recomendar


@login_required
def inicio(request):
    usuario = Usuario.objects.filter(cuenta=request.user).first()
    if usuario is None:
        return redirect('perfil')
    if not usuario.activo:
        return render(request, 'cultura_app/perfil.html', {'cuenta_inactiva': True}, status=403)

    eventos = list(Evento.objects.filter(activo=True).prefetch_related(
        Prefetch(
            'etiquetas',
            queryset=Etiqueta.objects.filter(activo=True),
            to_attr='etiquetas_activas',
        )
    ))
    recomendaciones = recomendar(usuario, eventos)

    consulta = request.GET.get('q', '').strip()[:100]
    resultados_busqueda = []
    if consulta:
        resultados_busqueda = Evento.objects.filter(activo=True).filter(
            Q(nombre__icontains=consulta)
            | Q(direccion__icontains=consulta)
            | Q(descripcion__icontains=consulta)
            | Q(etiquetas__activo=True, etiquetas__nombre__icontains=consulta)
        ).distinct().prefetch_related(
            Prefetch(
                'etiquetas',
                queryset=Etiqueta.objects.filter(activo=True),
                to_attr='etiquetas_activas',
            )
        )

    eventos_mapa = []
    for evento in eventos:
        coordenadas_validas = (
            math.isfinite(evento.latitud)
            and math.isfinite(evento.longitud)
            and -90 <= evento.latitud <= 90
            and -180 <= evento.longitud <= 180
        )
        if coordenadas_validas:
            eventos_mapa.append({
                'id': evento.pk,
                'nombre': evento.nombre,
                'direccion': evento.direccion,
                'descripcion': evento.descripcion,
                'fecha': evento.fecha.strftime('%d/%m/%Y'),
                'hora': evento.hora.strftime('%H:%M') if evento.hora else '',
                'latitud': evento.latitud,
                'longitud': evento.longitud,
                'etiquetas': [etiqueta.nombre for etiqueta in evento.etiquetas_activas],
            })

    ubicacion_usuario = {
        'nombre': usuario.nombre,
        'latitud': usuario.latitud,
        'longitud': usuario.longitud,
    }

    return render(
        request,
        "cultura_app/index.html",
        {
            "eventos_mapa": eventos_mapa,
            "resultados_busqueda": resultados_busqueda,
            "consulta": consulta,
            "recomendaciones": recomendaciones,
            "usuario": usuario,
            "ubicacion_usuario": ubicacion_usuario,
            "eventos_sin_coordenadas": len(eventos) - len(eventos_mapa),
            "eventos_mapa_ids": [evento['id'] for evento in eventos_mapa],
            "mapbox_access_token": settings.MAPBOX_ACCESS_TOKEN,
        },
    )


def ingresar(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('inicio')
    return render(request, 'cultura_app/ingresar.html', {'form': form})


def registrar(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cuenta = form.save()
        login(request, cuenta)
        return redirect('perfil')
    return render(request, 'cultura_app/registrar.html', {'form': form})


@login_required
def perfil(request):
    usuario = Usuario.objects.filter(cuenta=request.user).first()
    if usuario and not usuario.activo:
        return render(request, 'cultura_app/perfil.html', {'cuenta_inactiva': True}, status=403)

    if usuario is None:
        usuario = Usuario(
            cuenta=request.user,
            nombre=request.user.get_username(),
            distancia_maxima=1,
        )

    form = PreferenciasForm(request.POST or None, instance=usuario)
    if request.method == 'POST' and form.is_valid():
        usuario = form.save(commit=False)
        usuario.cuenta = request.user
        usuario.nombre = request.user.get_username()
        usuario.save()
        form.save_m2m()
        messages.success(request, 'Tus preferencias quedaron guardadas.')
        return redirect('inicio')

    return render(
        request,
        'cultura_app/perfil.html',
        {'form': form, 'mapbox_access_token': settings.MAPBOX_ACCESS_TOKEN},
    )


@login_required
@require_POST
def buscar_direccion(request):
    direccion = request.POST.get('direccion', '').strip()
    if not direccion or len(direccion) > 200:
        return JsonResponse({'error': 'Escribe una dirección de hasta 200 caracteres.'}, status=400)

    if not cache.add('nominatim_geocoding_rate_limit', True, timeout=1):
        return JsonResponse(
            {'error': 'Espera un segundo antes de buscar otra dirección.'},
            status=429,
        )

    parametros = urlencode({'q': direccion, 'format': 'jsonv2', 'limit': 1})
    peticion = Request(
        f'https://nominatim.openstreetmap.org/search?{parametros}',
        headers={
            'User-Agent': 'CulturaValparaiso/1.0',
            'Referer': request.build_absolute_uri(reverse('perfil')),
        },
    )
    try:
        with urlopen(peticion, timeout=10) as respuesta:
            resultados = json.load(respuesta)
    except (URLError, TimeoutError):
        return JsonResponse(
            {'error': 'No se pudo consultar el servicio de direcciones. Intenta de nuevo.'},
            status=502,
        )
    except json.JSONDecodeError:
        return JsonResponse(
            {'error': 'El servicio de direcciones devolvió una respuesta inválida.'},
            status=502,
        )

    if not isinstance(resultados, list):
        return JsonResponse(
            {'error': 'El servicio de direcciones devolvió una respuesta inválida.'},
            status=502,
        )
    if not resultados:
        return JsonResponse({'error': 'No se encontró esa dirección.'}, status=404)
    if not isinstance(resultados[0], dict):
        return JsonResponse(
            {'error': 'El servicio de direcciones devolvió una respuesta inválida.'},
            status=502,
        )

    try:
        latitud = float(resultados[0]['lat'])
        longitud = float(resultados[0]['lon'])
    except (KeyError, TypeError, ValueError):
        return JsonResponse(
            {'error': 'El servicio de direcciones devolvió coordenadas inválidas.'},
            status=502,
        )
    if (
        not math.isfinite(latitud)
        or not math.isfinite(longitud)
        or not -90 <= latitud <= 90
        or not -180 <= longitud <= 180
    ):
        return JsonResponse(
            {'error': 'El servicio de direcciones devolvió coordenadas inválidas.'},
            status=502,
        )

    nombre = resultados[0].get('display_name')
    return JsonResponse({
        'latitud': latitud,
        'longitud': longitud,
        'nombre': nombre if isinstance(nombre, str) else direccion,
    })


@require_POST
def salir(request):
    logout(request)
    return redirect('ingresar')
