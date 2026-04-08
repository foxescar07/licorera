from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_contacto', 'nombre_empresa', 'email', 'telefono']
        widgets = {
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Nombre del asesor'
            }),
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Ej: Bavaria S.A.'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'correo@empresa.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Solo números',
                'maxlength': '10',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"
            }),
        }

    from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre_contacto', 'nombre_empresa', 'email', 'telefono']
        widgets = {
            'nombre_contacto': forms.TextInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Nombre del asesor'
            }),
            'nombre_empresa': forms.TextInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Ej: Bavaria S.A.'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'correo@empresa.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control text-dark',
                'placeholder': 'Solo números',
                'maxlength': '10',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '');"
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
import re
def clean_telefono(self):
    telefono = self.cleaned_data.get('telefono')

    if not telefono:
        return telefono  # required ya lo maneja

    # Solo números y longitud entre 7 y 10 (Colombia típico)
    if not re.fullmatch(r'^\d{7,10}$', telefono):
        raise forms.ValidationError("⚠️ El teléfono debe tener entre 7 y 10 dígitos numéricos")

    return telefono