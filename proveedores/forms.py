from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'telefono', 'empresa', 'correo']

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Proveedor.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado con otro proveedor.")
        return correo