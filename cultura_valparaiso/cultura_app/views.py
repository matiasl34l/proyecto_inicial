from django.shortcuts import render
from .models import Evento
from .models import Usuario
from .recomendaciones import recomendar


def inicio(request):
    usuario = Usuario.objects.filter(activo=True).first()
    eventos = Evento.objects.filter(activo=True).prefetch_related("etiquetas")
    recomendaciones = recomendar(usuario, eventos) if usuario else []
    return render(
        request,
        "cultura_app/index.html",
        {"eventos": eventos, "recomendaciones": recomendaciones, "usuario": usuario},
    )
