from django.db import models
from producto.models import Producto

class Venta(models.Model):
    cliente         = models.CharField(max_length=100)
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='ventas')
    cantidad        = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    fecha           = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Venta"
        verbose_name_plural = "Ventas"
        ordering            = ["-fecha"]

    def total(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.cliente} — {self.producto.nombre} x{self.cantidad}"