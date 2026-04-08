from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User

# =======================
# MODELO PROVEEDOR
# =======================
class Proveedor(models.Model):
    nombre_contacto = models.CharField(max_length=100)
    nombre_empresa = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    telefono_regex = RegexValidator(
        regex=r'^\d{10}$',
        message="El celular debe tener exactamente 10 dígitos."
    )
    telefono = models.CharField(
        validators=[telefono_regex],
        max_length=10,
        verbose_name="Celular"
    )

    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    ultima_modificacion = models.DateTimeField(auto_now=True, verbose_name="Última modificación")

    registrado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proveedores_registrados'
    )
    modificado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='proveedores_modificados'
    )

    class Meta:
        ordering = ['-fecha_registro']

    def __str__(self):
        return self.nombre_empresa

# =======================
# MODELO COMPRA
# =======================
class Compra(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    producto = models.CharField(max_length=100)
    cantidad = models.PositiveIntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto} ({self.cantidad}) - {self.proveedor.nombre_empresa}"