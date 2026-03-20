from django.db import models

class Venta(models.Model):

    cliente = models.CharField(max_length=100)
    producto = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    precio = models.IntegerField()

    def total(self):
        return self.cantidad * self.precio

    def __str__(self):
        return self.cliente