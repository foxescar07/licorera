from django.db import models
from producto.models import Producto, PresentacionProducto


class Venta(models.Model):
    cliente = models.CharField(max_length=100)
    fecha   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Venta"
        verbose_name_plural = "Ventas"
        ordering            = ["-fecha"]

    def __str__(self):
        return f"{self.cliente} — {self.fecha:%d/%m/%Y %H:%M}"

    def total(self):
        return sum(d.subtotal() for d in self.detalles.all())


class DetalleVenta(models.Model):
    venta           = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='detalles_venta')
    presentacion    = models.ForeignKey(PresentacionProducto, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='detalles_venta')
    cantidad        = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name        = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        pres = f" ({self.presentacion.nombre})" if self.presentacion else " (unidad suelta)"
        return f"{self.producto.nombre}{pres} x{self.cantidad}"