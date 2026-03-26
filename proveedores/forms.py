from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    telefono = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 3101234567',
            'type': 'tel',            # Indica que es un teléfono
            'minlength': '10',        # Mínimo 10 caracteres
            'maxlength': '10',        # Máximo 10 caracteres (Bloquea el teclado al llegar a 10)
            'pattern': '[0-9]{10}',   # Solo permite números y exactamente 10
            'required': 'required'    # Campo obligatorio
        })
    )

    class Meta:
        model = Proveedor
        fields = ['nombre', 'empresa', 'telefono', 'correo']
        