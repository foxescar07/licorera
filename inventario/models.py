from django.db import models
from producto.models import Producto


class SesionConteo(models.Model):
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    activa       = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'Sesión de Conteo'

    def __str__(self):
        return f"Sesión {self.pk} — {self.fecha_inicio:%d/%m/%Y %H:%M}"


class ConteoProducto(models.Model):
    sesion           = models.ForeignKey(SesionConteo, on_delete=models.CASCADE, related_name='conteos')
    producto         = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_contada = models.IntegerField(default=0)
    actualizado_en   = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('sesion', 'producto')
        verbose_name = 'Conteo de Producto'

    def __str__(self):
        return f"{self.producto.nombre} → {self.cantidad_contada}"