from django.contrib import admin
from .models import Proveedor, Compra

@admin.register(Compra)
class CompraAdmin(admin.ModelAdmin):
    list_display  = ('id', 'proveedor', 'producto', 'cantidad', 'precio_unitario', 'fecha_registro', 'recibida')
    list_filter   = ('proveedor', 'recibida', 'fecha_registro')
    search_fields = ('proveedor__nombre_empresa', 'producto__nombre')
    ordering      = ('-fecha_registro',)

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display  = ('nombre_empresa', 'nombre_contacto', 'telefono', 'email', 'estado')
    list_filter   = ('estado',)
    search_fields = ('nombre_empresa', 'nombre_contacto', 'email')