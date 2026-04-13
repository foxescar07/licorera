from django import forms
from .models import Proveedor
import re

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_empresa', 'nombre_contacto', 'email', 'telefono']

        widgets = {
    'nombre_empresa': forms.TextInput(attrs={
        'class': 'cys-input',
        'placeholder': 'Ej: Bavaria S.A.',
        'style': 'background-color:#0b1220 !important; color:#e2e8f0 !important; border:1px solid rgba(77,168,218,0.25) !important; border-radius:10px !important; padding:12px 16px !important;'
    }),
    'nombre_contacto': forms.TextInput(attrs={
        'class': 'cys-input',
        'placeholder': 'Nombre del asesor',
        'style': 'background-color:#0b1220 !important; color:#e2e8f0 !important; border:1px solid rgba(77,168,218,0.25) !important; border-radius:10px !important; padding:12px 16px !important;'
    }),
    'email': forms.EmailInput(attrs={
        'class': 'cys-input',
        'placeholder': 'correo@empresa.com',
        'style': 'background-color:#0b1220 !important; color:#e2e8f0 !important; border:1px solid rgba(77,168,218,0.25) !important; border-radius:10px !important; padding:12px 16px !important;'
    }),
    'telefono': forms.TextInput(attrs={
        'class': 'cys-input',
        'placeholder': 'Solo números',
        'style': 'background-color:#0b1220 !important; color:#e2e8f0 !important; border:1px solid rgba(77,168,218,0.25) !important; border-radius:10px !important; padding:12px 16px !important;'
    }),
}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 🔥 Campos obligatorios + mensajes personalizados
        self.fields['nombre_contacto'].required = True
        self.fields['nombre_empresa'].required = True
        self.fields['email'].required = True
        self.fields['telefono'].required = True

        self.fields['nombre_contacto'].error_messages = {
            'required': 'Debe ingresar el nombre del contacto.'
        }
        self.fields['nombre_empresa'].error_messages = {
            'required': 'Debe ingresar el nombre de la empresa.'
        }
        self.fields['email'].error_messages = {
            'required': 'Debe ingresar un correo.'
        }
        self.fields['telefono'].error_messages = {
            'required': 'Debe ingresar un teléfono.'
        }

    # ✅ Validar correo duplicado
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and Proveedor.objects.filter(email=email).exists():
            raise forms.ValidationError("⚠️ Este correo ya está registrado")
        return email

    # ✅ Validar teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')

        if not telefono:
            return telefono

        # Solo números y longitud entre 7 y 10
        if not re.fullmatch(r'^\d{7,10}$', telefono):
            raise forms.ValidationError("⚠️ El teléfono debe tener entre 7 y 10 dígitos numéricos")

        return telefono