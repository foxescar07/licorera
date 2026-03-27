from django.db import models
 
class Usuario(models.Model):
    identificacion = models.CharField(max_length=20, unique=True, verbose_name="Identificación")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    fecha_registro = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
 
    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"
forms 
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
