import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import BoyaForm, SensorForm
from .models import Boya, Lectura, Sensor


def actualizar_y_obtener_boyas(user):
    """Consulta al Gateway (192.168.1.200), extrae el serial_number recibido

    en la trama LoRa y registra la lectura únicamente en la boya correspondiente.
    """
    url = 'http://192.168.1.200'
    headers = {'ngrok-skip-browser-warning': 'true'}

    try:
        # Petición única al Gateway
        response = requests.get(url, headers=headers, timeout=1.5)
        if response.status_code == 200:
            texto_crudo = response.text.strip()
            partes = [v.strip() for v in texto_crudo.split(',')]

            # Trama esperada: [SERIAL, Temp, pH, Turb, Ox]
            if len(partes) >= 5:
                serial_recibido = partes[0]
                valores_sensores = partes[1:]

                # Buscar únicamente la boya que coincida con el serial recibido
                boya_coincidente = Boya.objects.filter(
                    serial_number__iexact=serial_recibido
                ).first()

                if boya_coincidente:
                    sensores = list(boya_coincidente.sensores.all())
                    for i, sensor in enumerate(sensores):
                        if i < len(valores_sensores):
                            try:
                                val_float = float(valores_sensores[i])
                                alerta = (
                                    val_float < sensor.rango_min
                                    or val_float > sensor.rango_max
                                )

                                # Registrar la lectura aislada para esta boya
                                Lectura.objects.create(
                                    sensor=sensor,
                                    valor=val_float,
                                    alerta=alerta,
                                )
                            except ValueError:
                                pass
    except Exception as e:
        print(f'Error al conectar con el Gateway: {e}')

    # Filtrar boyas según los permisos del usuario actual
    if user.is_superuser:
        return Boya.objects.all()
    return Boya.objects.filter(propietario=user)


class HomeView(LoginRequiredMixin, ListView):
    model = Boya
    template_name = 'boyas/index.html'
    context_object_name = 'boyas'
    login_url = '/login/'

    def get_queryset(self):
        return actualizar_y_obtener_boyas(self.request.user)


# ==========================================
# VISTA API PARA EL SEGUNDO PLANO (AJAX)
# ==========================================
def api_estado_boyas(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    boyas = actualizar_y_obtener_boyas(request.user)

    boyas_data = []
    for boya in boyas:
        sensores_data = []
        for sensor in boya.sensores.all():
            ultima_lectura = sensor.lecturas.first()

            rango_min = getattr(sensor, 'rango_min', 0)
            rango_max = getattr(sensor, 'rango_max', 100)

            valor_str = str(ultima_lectura.valor) if ultima_lectura else '---'
            fecha_str = (
                ultima_lectura.fecha_hora.strftime('%H:%M:%S')
                if ultima_lectura and ultima_lectura.fecha_hora
                else ''
            )

            sensores_data.append({
                'id': sensor.pk,
                'tipo': sensor.tipo,
                'tipo_display': (
                    sensor.get_tipo_display()
                    if hasattr(sensor, 'get_tipo_display')
                    else str(sensor.tipo)
                ),
                'valor': valor_str,
                'rango_min': float(rango_min) if rango_min is not None else 0,
                'rango_max': float(rango_max) if rango_max is not None else 100,
                'ultima_actualizacion': fecha_str,
            })

        boyas_data.append({
            'id': boya.pk,
            'nombre': boya.nombre,
            'serial_number': boya.serial_number,
            'activa': boya.activa,
            'sensores': sensores_data,
        })

    return JsonResponse({'boyas': boyas_data})


class BoyaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Boya
    form_class = BoyaForm
    template_name = 'boyas/boya_form.html'
    success_url = reverse_lazy('boyas_home')

    def form_valid(self, form):
        # Guarda directamente el serial_number ingresado manualmente en el formulario web
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser


class SensorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'boyas/sensor_form.html'
    success_url = reverse_lazy('boyas_home')

    def test_func(self):
        return self.request.user.is_superuser


# ==========================================
# VISTA DE ACTUALIZACIÓN DE SENSORES (EDICIÓN)
# ==========================================
class SensorUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'boyas/sensor_form.html'
    success_url = reverse_lazy('boyas_home')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(boya__propietario=self.request.user)

    def test_func(self):
        sensor = self.get_object()
        return (
            self.request.user.is_superuser
            or sensor.boya.propietario == self.request.user
        )


class SensorDeleteView(LoginRequiredMixin, DeleteView):
    model = Sensor
    success_url = reverse_lazy('boyas_home')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(boya__propietario=self.request.user)

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


# ==========================================
# VISTA DE PRUEBA INDEPENDIENTE
# ==========================================
def prueba_numero(request):
    url = 'http://192.168.1.200'
    headers = {'ngrok-skip-browser-warning': 'true'}

    numero_a_mostrar = '---'
    try:
        response = requests.get(url, headers=headers, timeout=1)
        if response.status_code == 200:
            numero_a_mostrar = response.text
        else:
            numero_a_mostrar = f'Error {response.status_code}'
    except Exception as e:
        numero_a_mostrar = 'Sin conexión'

    html = f"""
    <div style="display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #0f172a; font-family: sans-serif;">
        <div style="text-align: center; color: white;">
            <h1 style="font-size: 20px; color: #94a3b8; margin-bottom: 10px;">DATO RECIBIDO DE LA BOYA (192.168.1.200):</h1>
            <div style="font-size: 80px; font-weight: bold; color: #38bdf8;">{numero_a_mostrar}</div>
        </div>
    </div>
    """
    return HttpResponse(html)