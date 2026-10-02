from django import forms
from .models import Boya, Sensor

class BoyaForm(forms.ModelForm):
    class Meta:
        model = Boya
        fields = ['nombre', 'ubicacion', 'activa', 'propietario']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-white/60 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-gray-800',
                'placeholder': 'Ej: Boya Río Paraná 01'
            }),
            'ubicacion': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 bg-white/60 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-gray-800',
                'placeholder': 'Ej: Sector Norte - Muelle 4'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            'propietario': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-white/60 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-gray-800'
            }),
        }



class SensorForm(forms.ModelForm):
    class Meta:
        model = Sensor
        fields = ['boya', 'tipo', 'rango_min', 'rango_max']
        widgets = {
            'boya': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-white/60 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-gray-800'
            }),
            'tipo': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 bg-white/60 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-gray-800'
            }),
            'rango_min': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'w-full px-4 py-2.5 bg-white/60 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-gray-800'
            }),
            'rango_max': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'w-full px-4 py-2.5 bg-white/60 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-gray-800'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['boya'].label_from_instance = lambda obj: (
            f"{obj.nombre} (Propietario: {obj.propietario.username if obj.propietario else 'Sin asignar'})"
        )

