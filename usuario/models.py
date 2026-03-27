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