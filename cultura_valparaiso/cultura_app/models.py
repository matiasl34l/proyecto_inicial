from django.db import models

# Create your models here.
class Usuario(models.Model):
    nombre = models.CharField(max_length=50)
    gustos = models.ManyToManyField('Etiqueta', related_name='usuarios', blank=True)
    latitud = models.FloatField(default=-33.0472)
    longitud = models.FloatField(default=-71.6127)
    distancia_maxima = models.IntegerField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Etiqueta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Evento(models.Model):
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField(null=True)
    direccion = models.CharField(max_length=200)
    descripcion = models.TextField()
    latitud = models.FloatField()
    longitud = models.FloatField()
    etiquetas = models.ManyToManyField(Etiqueta, related_name='eventos', blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre
