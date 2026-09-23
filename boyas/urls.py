from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import HomeView, BoyaCreateView, SensorCreateView, SensorDeleteView

urlpatterns = [
    path('', HomeView.as_view(), name='boyas_home'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('boya/nueva/', BoyaCreateView.as_view(), name='crear_boya'),
    path('sensor/nuevo/', SensorCreateView.as_view(), name='crear_sensor'),
    path('sensor/<int:pk>/eliminar/', SensorDeleteView.as_view(), name='eliminar_sensor'),
]