from django.db import models
from producto.models import Producto, PresentacionProducto


class Venta(models.Model):
    cliente              = models.CharField(max_length=100)
    fecha                = models.DateTimeField(auto_now_add=True)
    descuento_porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_con_descuento  = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    pago_efectivo       = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pago_tarjeta        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pago_transferencia  = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pago_nequi          = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pago_daviplata      = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name        = "Venta"
        verbose_name_plural = "Ventas"
        ordering            = ["-fecha"]

    def __str__(self):
        return f"{self.cliente} — {self.fecha:%d/%m/%Y %H:%M}"

    def subtotal(self):
        return sum(d.subtotal() for d in self.detalles.all())

    @property
    def total_venta(self):
        return self.total_con_descuento if self.total_con_descuento else self.subtotal()


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


class Devolucion(models.Model):
    MOTIVO_CHOICES = [
        ('defectuoso',   'Producto defectuoso'),
        ('equivocado',   'Producto equivocado'),
        ('insatisfecho', 'Cliente insatisfecho'),
        ('otro',         'Otro'),
    ]

    venta             = models.ForeignKey(Venta, on_delete=models.PROTECT,
                                          related_name='devoluciones',
                                          verbose_name='Venta original')
    fecha             = models.DateTimeField(auto_now_add=True)
    motivo            = models.CharField(max_length=20, choices=MOTIVO_CHOICES, default='otro')
    observaciones     = models.TextField(blank=True)
    restaurar_stock   = models.BooleanField(default=True, verbose_name='Restaurar stock')
    tiene_comprobante = models.BooleanField(default=True, verbose_name='Tiene comprobante de compra')
    total_devuelto    = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name        = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering            = ['-fecha']

    def __str__(self):
        return f'DEV-{self.pk:04d} | {self.venta.cliente} — {self.fecha:%d/%m/%Y %H:%M}'

    @property
    def numero(self):
        return f'DEV-{self.pk:04d}'


class DetalleDevolucion(models.Model):
    devolucion      = models.ForeignKey(Devolucion, on_delete=models.CASCADE,
                                        related_name='detalles')
    producto        = models.ForeignKey(Producto, on_delete=models.PROTECT,
                                        related_name='detalles_devolucion')
    presentacion    = models.ForeignKey(PresentacionProducto, on_delete=models.SET_NULL,
                                        null=True, blank=True,
                                        related_name='detalles_devolucion')
    cantidad        = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name        = 'Detalle de Devolución'
        verbose_name_plural = 'Detalles de Devolución'

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        pres = f' ({self.presentacion.nombre})' if self.presentacion else ''
        return f'{self.producto.nombre}{pres} x{self.cantidad}'
    from django.db import models
from django.utils import timezone
 
 
class AperturaCaja(models.Model):
    fecha_apertura    = models.DateTimeField(default=timezone.now)
    fecha             = models.DateField(default=timezone.localdate)
    monto_base        = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    usuario           = models.CharField(max_length=150, blank=True, default='')
    observacion       = models.TextField(blank=True, default='')
    denominaciones    = models.JSONField(default=dict, blank=True)   # {valor: cantidad}
 
    class Meta:
        ordering = ['-fecha_apertura']
        verbose_name        = 'Apertura de caja'
        verbose_name_plural = 'Aperturas de caja'
 
    def __str__(self):
        return f'Apertura {self.fecha} — ${self.monto_base:,.0f}'
 
 
class CierreCaja(models.Model):
    apertura          = models.OneToOneField(
                            AperturaCaja, on_delete=models.SET_NULL,
                            null=True, blank=True, related_name='cierre'
                        )
    fecha_cierre      = models.DateTimeField(default=timezone.now)
    fecha             = models.DateField(default=timezone.localdate)
    total_contado     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_retirado    = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monto_base_siguiente = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    denominaciones    = models.JSONField(default=dict, blank=True)
 
    class Meta:
        ordering = ['-fecha_cierre']
        verbose_name        = 'Cierre de caja'
        verbose_name_plural = 'Cierres de caja'
 
    def __str__(self):
        return f'Cierre {self.fecha} — contado ${self.total_contado:,.0f}'
 