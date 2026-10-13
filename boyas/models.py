from django.contrib.auth.models import User
from django.db import models


class Boya(models.Model):
    
    serial_number = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='Número de Serie / MAC'
    )
    nombre = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name='Nombre de la Boya'
    )
    ubicacion = models.CharField(
        max_length=255, 
        verbose_name='Ubicación o Coordenadas'
    )
    activa = models.BooleanField(
        default=True, 
        verbose_name='Activa'
    )
    propietario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='boyas',
        verbose_name='Propietario',
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Fecha de Creación'
    )

    def __str__(self):
        return f'{self.nombre} (SN: {self.serial_number})'


class Sensor(models.Model):
    
    class TipoSensor(models.TextChoices):
        TEMPERATURA = 'temp', 'Temperatura'
        PH = 'ph', 'pH'
        TURBIDEZ = 'tb', 'Turbidez'
        OXIGENO = 'ox', 'Oxígeno Disuelto'

    boya = models.ForeignKey(
        Boya,
        on_delete=models.CASCADE,
        related_name='sensores',
        verbose_name='Boya',
    )
    tipo = models.CharField(
        max_length=10, 
        choices=TipoSensor.choices, 
        verbose_name='Tipo de Sensor'
    )
    
    # Rangos de alerta configurables
    rango_min = models.FloatField(
        default=0.0, 
        verbose_name='Rango Mínimo'
    )
    rango_max = models.FloatField(
        default=100.0, 
        verbose_name='Rango Máximo'
    )

    def __str__(self):
        return f'Sensor de {self.get_tipo_display()} - Boya: {self.boya.nombre}'


class Lectura(models.Model):
    sensor = models.ForeignKey(
        Sensor,
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Sensor',
    )
    valor = models.FloatField(
        verbose_name='Valor Medido'
    )
    alerta = models.BooleanField(
        default=False,
        verbose_name='Fuera de Rango (Alerta)'
    )
    fecha_hora = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora de Lectura'
    )

    class Meta:
        ordering = ['-fecha_hora'] # Para ver siempre las lecturas más recientes primero

    def __str__(self):
        estado_alerta = " [ALERTA]" if self.alerta else ""
        return f'{self.sensor.get_tipo_display()}: {self.valor} ({self.fecha_hora}) {estado_alerta}'