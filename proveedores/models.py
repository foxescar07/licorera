from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import User


# =======================
# MODELO PROVEEDOR
# =======================
class Proveedor(models.Model):

    ESTADO_CHOICES = [
        ('activo',     'Activo'),
        ('inactivo',   'Inactivo'),
        ('sancionado', 'Sancionado'),
    ]

    nombre_contacto = models.CharField(max_length=100)
    nombre_empresa  = models.CharField(max_length=100)
    email           = models.EmailField(unique=True)

    telefono_regex = RegexValidator(
        regex=r'^\d{10}$',
        message="El celular debe tener exactamente 10 dígitos."
    )
    telefono = models.CharField(
        validators=[telefono_regex],
        max_length=10,
        verbose_name="Celular"
    )

    # ── Categorización ──────────────────────────────────────────
    categorias_surtidas = models.ManyToManyField(
        'producto.Categoria',
        blank=True,
        related_name='proveedores',
        verbose_name="Categorías que surte"
    )

    # ── Estado ──────────────────────────────────────────────────
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo',
        verbose_name="Estado"
    )
    motivo_sancion = models.TextField(
        blank=True,
        default='',
        verbose_name="Motivo de sanción"
    )

    fecha_registro      = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    ultima_modificacion = models.DateTimeField(auto_now=True,     verbose_name="Última modificación")

    registrado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='proveedores_registrados'
    )
    modificado_por = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
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
    proveedor       = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='compras')
    producto        = models.ForeignKey('producto.Producto', on_delete=models.CASCADE, related_name='compras')
    lote            = models.ForeignKey('inventario.Lote', on_delete=models.SET_NULL, null=True, blank=True, related_name='compras')
    cantidad        = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    fecha_registro  = models.DateTimeField(auto_now_add=True)
    recibida        = models.BooleanField(default=False)

    @property
    def total(self):
        if self.precio_unitario:
            return self.cantidad * self.precio_unitario
        return None

    class Meta:
        ordering            = ['-fecha_registro']
        verbose_name        = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        return f"{self.proveedor.nombre_empresa} → {self.producto.nombre} ({self.cantidad} uds)"