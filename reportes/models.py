from django.db import models
from django.utils import timezone


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre


class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    cantidad_disponible = models.PositiveIntegerField(default=0)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_disponible} unidades"


class Venta(models.Model):
    cliente = models.CharField(max_length=100)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, related_name='ventas')
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)

    def total(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"{self.cliente} - {self.producto}"


class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, related_name='proveedores')
    fecha_entrega = models.DateField()

    def __str__(self):
        return self.nombre