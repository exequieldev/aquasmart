from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin  # Opcional: si solo quieres que usuarios logueados creen boyas
from .models import Boya,Sensor
from .forms import BoyaForm,SensorForm

class HomeView(LoginRequiredMixin, ListView):
    model = Boya
    template_name = 'boyas/index.html'
    context_object_name = 'boyas'
    
    # Opcional: Si quieres personalizar a dónde redirige (por defecto busca 'accounts/login/')
    login_url = '/login/' 

    def get_queryset(self):
        # Como LoginRequiredMixin ya bloquea a los anónimos, 
        # aquí ya tienes la seguridad de que el usuario está autenticado.
        if self.request.user.is_superuser:
            return Boya.objects.all()

        return Boya.objects.filter(propietario=self.request.user)


class BoyaCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView): # o simplemente CreateView si no requiere login
    model               = Boya
    form_class          = BoyaForm
    template_name       = 'boyas/boya_form.html'  # El HTML con el formulario
    success_url         = reverse_lazy('boyas_home')      # A dónde redirige al crearse (ajusta el nombre de tu URL 'home')

    def test_func(self):
        
        # Retorna True solo si el usuario actual es superusuario (administrador)
        return self.request.user.is_superuser


class SensorCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Sensor
    form_class = SensorForm
    template_name = 'boyas/sensor_form.html'
    success_url = reverse_lazy('boyas_home')

    def test_func(self):
        return self.request.user.is_superuser


class SensorDeleteView(LoginRequiredMixin, DeleteView):
    model = Sensor
    success_url = reverse_lazy('boyas_home')

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs
        return qs.filter(boya__propietario=self.request.user)

    # Esto evita que busque el archivo HTML de confirmación y borre directo al hacer GET
    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)