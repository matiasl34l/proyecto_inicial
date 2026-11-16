from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

# Create your models here.
class Usuario(models.Model):
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='perfil_cultural',
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=150)
    gustos = models.ManyToManyField('Etiqueta', related_name='usuarios', blank=True)
    latitud = models.FloatField(default=-33.0472)
    longitud = models.FloatField(default=-71.6127)
    distancia_maxima = models.IntegerField(validators=[MinValueValidator(1)])
    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(distancia_maxima__gte=1),
                name='usuario_distancia_min_1_km',
            ),
        ]

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


class Guardado(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='guardados')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='guardados')
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_agregado']
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'evento'],
                name='guardado_unico_por_usuario_y_evento',
            ),
        ]

    def __str__(self):
        return f'{self.usuario} guardó {self.evento}'
