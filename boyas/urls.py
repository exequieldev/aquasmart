from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import (
    BoyaCreateView,
    HomeView,
    SensorCreateView,
    SensorUpdateView,  # <- 1. Importamos la vista de actualización
    SensorDeleteView,
    prueba_numero,
)
from . import views

urlpatterns = [
    path('', HomeView.as_view(), name='boyas_home'),
    path(
        'login/', LoginView.as_view(template_name='login.html'), name='login'
    ),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('boya/nueva/', BoyaCreateView.as_view(), name='crear_boya'),
    path('sensor/nuevo/', SensorCreateView.as_view(), name='crear_sensor'),
    path(
        'sensor/<int:pk>/editar/', 
        SensorUpdateView.as_view(), 
        name='editar_sensor'
    ),  # <- 2. Añadimos la ruta para configurar/editar el sensor
    path(
        'sensor/<int:pk>/eliminar/',
        SensorDeleteView.as_view(),
        name='eliminar_sensor',
    ),
    path('prueba-numero/', prueba_numero, name='prueba_numero'),
    path('api/boyas/', views.api_estado_boyas, name='api_boyas'),
    path('sensor/<int:pk>/editar/', views.SensorUpdateView.as_view(), name='sensor_update'),
]