from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('ingresar/', views.ingresar, name='ingresar'),
    path('registrar/', views.registrar, name='registrar'),
    path('perfil/', views.perfil, name='perfil'),
    path('buscar-direccion/', views.buscar_direccion, name='buscar_direccion'),
    path('salir/', views.salir, name='salir'),
    path('guardados/', views.guardados, name='guardados'),
    path('guardar/<int:evento_id>/', views.guardar_evento, name='guardar_evento'),
]