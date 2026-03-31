from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model  = Proveedor
        fields = ['nombre_contacto', 'nombre_empresa', 'email', 'telefono',]
        widgets = {
            'nombre_contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del asesor'}),
            'nombre_empresa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bavaria S.A.'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@empresa.com'}),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '10',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"
            }),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}), # Cambiado a TextInput para que sea más corto
        }