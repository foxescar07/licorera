from django.urls import path
from . import views
 
app_name = 'ventas'
 
urlpatterns = [
    path('',                    views.ventas_lista,        name='ventas_lista'),
    path('nueva/',              views.nueva_venta,         name='nueva_venta'),
    path('eliminar/<int:pk>/',  views.eliminar_venta,      name='eliminar_venta'),
    path('stock/<int:pk>/',     views.producto_stock_json, name='producto_stock'),
    path('dia/',                views.ventas_dia,          name='ventas_dia'),
 
    # ── Caja ──────────────────────────────────────────────────
    path('caja/apertura/',      views.apertura_caja,       name='apertura_caja'),
    path('caja/cierre/',        views.cierre_caja,         name='cierre_caja'),
 
    # ── Devoluciones ──────────────────────────────────────────
    path('devoluciones/',                                  views.lista_devoluciones,      name='lista_devoluciones'),
    path('devoluciones/buscar/',                           views.buscar_venta_devolucion,  name='buscar_venta_devolucion'),
    path('devoluciones/venta/<int:venta_id>/detalle/',     views.detalle_venta_devolucion, name='detalle_venta_devolucion'),
    path('devoluciones/registrar/',                        views.registrar_devolucion,     name='registrar_devolucion'),
    path('devoluciones/comprobante/<int:pk>/',             views.comprobante_devolucion,   name='comprobante_devolucion'),
]
 