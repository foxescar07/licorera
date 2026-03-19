from django.contrib import admin
from .models import Categoria, Producto, Inventario, AgendaInventario


# ─────────────────────────────────────────────
#  Inline: muestra los movimientos de inventario
#  dentro del detalle de un Producto
# ─────────────────────────────────────────────
class InventarioInline(admin.TabularInline):
    model          = Inventario
    extra          = 1
    readonly_fields = ["fecha_actualizada"]
    fields         = ["ubicacion", "cantidad", "fecha_actualizada"]


# ─────────────────────────────────────────────
#  Categoría
# ─────────────────────────────────────────────
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display  = ["codigo", "nombre", "descripcion"]
    search_fields = ["codigo", "nombre"]
    ordering      = ["nombre"]


# ─────────────────────────────────────────────
#  Producto
# ─────────────────────────────────────────────
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display   = ["codigo", "nombre", "categoria", "cantidad_disponible", "unidad", "precio_unitario", "stock_critico"]
    list_filter    = ["categoria", "unidad"]
    search_fields  = ["codigo", "nombre"]
    ordering       = ["nombre"]
    readonly_fields = ["stock_critico"]
    inlines        = [InventarioInline]

    # Resalta en rojo los productos con stock crítico
    def get_list_display_links(self, request, list_display):
        return ["nombre"]

    @admin.display(boolean=True, description="Stock crítico")
    def stock_critico(self, obj):
        return obj.stock_critico


# ─────────────────────────────────────────────
#  Inventario
# ─────────────────────────────────────────────
@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display   = ["producto", "cantidad", "ubicacion", "fecha_actualizada"]
    list_filter    = ["producto__categoria"]
    search_fields  = ["producto__nombre", "producto__codigo"]
    ordering       = ["-fecha_actualizada"]
    readonly_fields = ["fecha_actualizada"]
    

@admin.register(AgendaInventario)
class AgendaInventarioAdmin(admin.ModelAdmin):
    list_display  = ["titulo", "fecha_programada", "estado", "creado_en"]
    list_filter   = ["estado"]
    search_fields = ["titulo"]
    ordering      = ["fecha_programada"]