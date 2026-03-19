from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'telefono', 'empresa', 'correo']

    # Validación para el CORREO
    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        # Verificamos si ya existe en la base de datos
        if Proveedor.objects.filter(correo=correo).exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado con otro proveedor.")
        return correo

    # Validación para la EMPRESA (Opcional, si quieres que el nombre sea único)
    def clean_empresa(self):
        empresa = self.cleaned_data.get('empresa')
        if Proveedor.objects.filter(empresa__iexact=empresa).exists():
            raise forms.ValidationError("Ya existe un proveedor registrado bajo esta empresa.")
        return empresa