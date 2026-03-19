from django.db import models

class Categoria(models.Model):
    """
    Representa una categoría de productos.
    Ej: Cervezas, Gaseosas, Licores, Cigarrería
    """
    codigo      = models.CharField(max_length=20, unique=True)
    nombre      = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name        = "Categoría"
        verbose_name_plural = "Categorías"
        ordering            = ["nombre"]

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Producto del inventario.
    - Pertenece a una Categoría (FK → Categoria)
    """
    UNIDAD_CHOICES = [
        ("UND",   "Unidad"),
        ("CAJA",  "Caja"),
        ("PAQ",   "Paquete"),
        ("LITRO", "Litro"),
    ]

    codigo              = models.CharField(max_length=30, unique=True)
    nombre              = models.CharField(max_length=150)
    descripcion         = models.TextField(blank=True, null=True)
    cantidad_disponible = models.PositiveIntegerField(default=0)
    precio_unitario     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unidad              = models.CharField(max_length=10, choices=UNIDAD_CHOICES, default="UND")

    # Relaciones del MER
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT,
        related_name="productos"
    )

    class Meta:
        verbose_name        = "Producto"
        verbose_name_plural = "Productos"
        ordering            = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    @property
    def stock_critico(self):
        """Retorna True si el stock es <= 5 unidades."""
        return self.cantidad_disponible <= 5


class Inventario(models.Model):
    """
    Registro de movimientos/entradas de inventario.
    - Proviene de un Producto  (FK → Producto)
    - Posee / almacena al Producto
    """
    producto         = models.ForeignKey(
        Producto, on_delete=models.CASCADE,
        related_name="movimientos"
    )
    ubicacion        = models.CharField(max_length=100, blank=True, null=True)
    cantidad         = models.IntegerField(
        help_text="Positivo = entrada, Negativo = salida"
    )
    fecha_actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Registro de Inventario"
        verbose_name_plural = "Registros de Inventario"
        ordering            = ["-fecha_actualizada"]

    def __str__(self):
        return f"{self.producto.nombre} | {self.cantidad} | {self.fecha_actualizada:%d/%m/%Y}"
    
class AgendaInventario(models.Model):
        
    ESTADO_CHOICES = [
        ("pendiente",  "Pendiente"),
        ("en_proceso", "En Proceso"),
        ("completado", "Completado"),
        ("cancelado",  "Cancelado"),
    ]

    titulo           = models.CharField(max_length=150)
    descripcion      = models.TextField(blank=True, null=True)
    fecha_programada = models.DateTimeField()
    estado           = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="pendiente")
    creado_en        = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Agenda de Inventario"
        verbose_name_plural = "Agendas de Inventario"
        ordering            = ["fecha_programada"]

    def __str__(self):
        return f"{self.titulo} — {self.fecha_programada:%d/%m/%Y %H:%M}"
