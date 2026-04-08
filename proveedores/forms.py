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

    # Validar correo duplicado
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Proveedor.objects.filter(email=email).exists():
            raise forms.ValidationError("⚠️ Este correo ya está registrado")
        return email

    # Validar teléfono
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and len(telefono) < 7:
            raise forms.ValidationError("⚠️ Teléfono muy corto")
        return telefono