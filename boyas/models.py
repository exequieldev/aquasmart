from django.contrib.auth.models import User
from django.db import models


class Boya(models.Model):
    nombre = models.CharField(
        max_length=100, unique=True, verbose_name='Nombre de la Boya'
    )
    ubicacion = models.CharField(
        max_length=255, verbose_name='Ubicación o Coordenadas'
    )
    activa = models.BooleanField(default=True, verbose_name='Activa')
    propietario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boyas',
        verbose_name='Propietario',
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, verbose_name='Fecha de Creación'
    )

    def __str__(self):
        return f'{self.nombre} ({self.ubicacion})'


class Sensor(models.Model):
    TIPO_SENSORES = [
        ('temperatura', 'Temperatura'),
        ('ph', 'pH'),
        ('turbidez', 'Turbidez'),
        ('oxigeno', 'Oxígeno Disuelto'),
    ]

    boya = models.ForeignKey(
        Boya,
        on_delete=models.CASCADE,
        related_name='sensores',
        verbose_name='Boya',
    )
    tipo = models.CharField(
        max_length=50, choices=TIPO_SENSORES, verbose_name='Tipo de Sensor'
    )
    valor = models.CharField(
        max_length=50, default='---', verbose_name='Valor Actual'
    )
    
    # Rangos de alerta configurables
    rango_min = models.FloatField(default=0.0, verbose_name='Rango Mínimo')
    rango_max = models.FloatField(default=100.0, verbose_name='Rango Máximo')

    ultima_actualizacion = models.DateTimeField(
        auto_now=True, verbose_name='Última Medición'
    )

    def __str__(self):
        return f'Sensor de {self.get_tipo_display()} - Boya: {self.boya.nombre}'