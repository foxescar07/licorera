from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

class Proveedor(models.Model):
    nombre_empresa  = models.CharField(max_length=200, verbose_name="Proveedor / Empresa")
    nombre_contacto = models.CharField(max_length=100, verbose_name="Persona de Contacto")
    email           = models.EmailField(unique=True, verbose_name="Correo Electrónico")

    telefono_regex  = RegexValidator(
        regex=r'^\d{10}$',
        message="El celular debe tener exactamente 10 dígitos."
    )
    telefono        = models.CharField(validators=[telefono_regex], max_length=10, verbose_name="Celular")

    fecha_registro  = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro") # Usar auto_now_add para la creación
    ultima_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")
    
    registrado_por  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='proveedores_registrados')
    modificado_por  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='proveedores_modificados')

    class Meta:
        ordering = ['-fecha_registro']

    def __str__(self):
        return self.nombre_empresa