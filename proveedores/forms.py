from django import forms
from .models import Proveedor

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'empresa', 'telefono', 'correo']

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        queryset = Proveedor.objects.filter(correo=correo)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Este correo ya está registrado.")
        return correo

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        queryset = Proveedor.objects.filter(telefono=telefono)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Este teléfono ya está registrado.")
        return telefono