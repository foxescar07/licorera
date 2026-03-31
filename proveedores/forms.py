from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'telefono', 'empresa', 'correo']

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if not telefono.isdigit():
            raise forms.ValidationError("El teléfono solo debe contener números.")
        return telefono

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if any(char.isdigit() for char in nombre):
            raise forms.ValidationError("El nombre no debe contener números.")
        return nombre