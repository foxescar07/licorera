from django.db import models

class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    empresa = models.CharField(max_length=100)
    correo = models.EmailField()

    def __str__(self):
        return self.nombre