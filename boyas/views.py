from django.http import JsonResponse
import requests
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from .forms import BoyaForm, SensorForm
from .models import Boya, Sensor


def actualizar_y_obtener_boyas(user):
    """Función auxiliar para consultar la boya por red, actualizar la BD y filtrar por permisos."""
    url = 'http://192.168.1.200'
    headers = {'ngrok-skip-browser-warning': 'true'}

    # Valores por defecto en caso de que falle la red
    valores = ['Sin conexión', 'Sin conexión', 'Sin conexión', 'Sin conexión']

    try:
        response = requests.get(url, headers=headers, timeout=1.5)
        if response.status_code == 200:
            texto_limpio = response.text.strip()
            valores = [v.strip() for v in texto_limpio.split(',')]
    except Exception as e:
        print(f'Error al conectar con la boya: {e}')

    # Filtrar boyas según el usuario
    if user.is_superuser:
        boyas = Boya.objects.all()
    else:
        boyas = Boya.objects.filter(propietario=user)

    # Asignar valores a los sensores y guardar en la base de datos
    for boya in boyas:
        sensores = list(boya.sensores.all())
        for i, sensor in enumerate(sensores):
            if i < len(valores):
                sensor.valor = valores[i]
            else:
                sensor.valor = 'N/D'
            sensor.save()

    return boyas


class HomeView(LoginRequiredMixin, ListView):
    model = Boya
    template_name = 'boyas/index.html'
    context_object_name = 'boyas'
    login_url = '/login/'

    def get_queryset(self):
        # La consulta inicial delega en la función de actualización
        return actualizar_y_obtener_boyas(self.request.user)


# ==========================================
# VISTA API PARA EL SEGUNDO PLANO (AJAX)
# ==========================================
def api_estado_boyas(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    # Actualiza y obtiene las boyas correspondientes al usuario actual
    boyas = actualizar_y_obtener_boyas(request.user)

    boyas_data = []
    for boya in boyas:
        sensores_data = []
        for sensor in boya.sensores.all():
            # Obtención segura de rangos por si cambian de nombre en el modelo
            rango_min = getattr(sensor, 'rango_min', getattr(sensor, 'minimo', 0))
            rango_max = getattr(sensor, 'rango_max', getattr(sensor, 'maximo', 100))

            sensores_data.append({
                'id': sensor.pk,
                'tipo': sensor.tipo,
                'tipo_display': sensor.get_tipo_display() if hasattr(sensor, 'get_tipo_display') else str(sensor.tipo),
                'valor': str(sensor.valor) if sensor.valor is not None else '---',
                'rango_min': float(rango_min) if rango_min is not None else 0,
                'rango_max': float(rango_max) if rango_max is not None else 100,
                'ultima_actualizacion': sensor.ultima_actualizacion.strftime('%H:%M:%S') if hasattr(sensor, 'ultima_actualizacion') and sensor.ultima_actualizacion else ''
            })
        boyas_data.append({
            'id': boya.pk,
            'nombre': boya.nombre,
            'activa': boya.activa,
            'sensores': sensores_data
        })
    return JsonResponse({'boyas': boyas_data})


class BoyaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Boya
    form_class = BoyaForm
    template_name = 'boyas/boya_form.html'
    success_url = reverse_lazy('boyas_home')

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
    template_name = 'boyas/sensor_form.html'  # Apunta al formulario para renderizar los campos correctamente
    success_url = reverse_lazy('boyas_home')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        # Los usuarios normales solo pueden editar sensores de sus propias boyas asignadas
        return qs.filter(boya__propietario=self.request.user)

    def test_func(self):
        sensor = self.get_object()
        return self.request.user.is_superuser or sensor.boya.propietario == self.request.user


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