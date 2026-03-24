from django.db import models
from django.contrib.auth.models import User

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    empresa = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(unique=True)
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now=True)  # auto_now para actualizar al editar

    def __str__(self):
        return self.nombre