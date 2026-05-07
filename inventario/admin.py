from django.contrib import admin
from .models import SesionConteo, ConteoProducto, ResultadoInventario, Lote

@admin.register(SesionConteo)
class SesionConteoAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'fecha_inicio', 'estado', 'activa', 'responsable']
    list_filter   = ['estado', 'activa']

@admin.register(ConteoProducto)
class ConteoProductoAdmin(admin.ModelAdmin):
    list_display  = ['sesion', 'producto', 'cantidad_contada']
    search_fields = ['producto__nombre']

@admin.register(ResultadoInventario)
class ResultadoInventarioAdmin(admin.ModelAdmin):
    list_display = ['sesion', 'producto', 'cantidad_sistema', 'cantidad_fisica', 'diferencia']

@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display  = ['numero_lote', 'producto', 'fecha_vencimiento', 'esta_vencido']
    search_fields = ['numero_lote', 'producto__nombre']