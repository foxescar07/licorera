from django import forms
from .models import Usuario
 
class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['identificacion', 'nombre', 'telefono', 'direccion']
 
    def clean_identificacion(self):
        identificacion = self.cleaned_data.get('identificacion')
        if not identificacion.isdigit():
            raise forms.ValidationError("La identificación solo debe contener números.")
        if Usuario.objects.filter(identificacion=identificacion).exists():
            raise forms.ValidationError("Ya existe un usuario con esta identificación.")
        return identificacion
 
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