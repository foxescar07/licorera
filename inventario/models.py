from django.db import models
from producto.models import Producto


class SesionConteo(models.Model):
    ESTADO_CHOICES = [
        ('activa',     'Activa'),
        ('finalizada', 'Finalizada'),
    ]
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin    = models.DateTimeField(null=True, blank=True)
    activa       = models.BooleanField(default=True)
    estado       = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activa')

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

class ResultadoInventario(models.Model):
    sesion           = models.ForeignKey(SesionConteo, on_delete=models.CASCADE, related_name='resultados')
    producto         = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_sistema = models.IntegerField(default=0)  # ← añade default=0
    cantidad_fisica  = models.IntegerField(default=0)  # ← añade default=0
    diferencia       = models.IntegerField(default=0)  # ← añade default=0
    guardado_en      = models.DateTimeField(auto_now_add=True)

    def get_estado(self):
        if self.diferencia == 0:
            return 'ok'
        return 'sobrante' if self.diferencia > 0 else 'faltante'

    def __str__(self):
        return f"{self.producto.nombre} | diff: {self.diferencia}"