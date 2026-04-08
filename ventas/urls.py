from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('',                    views.ventas_lista,       name='ventas_lista'),
    path('nueva/',              views.nueva_venta,         name='nueva_venta'),
    path('eliminar/<int:pk>/',  views.eliminar_venta,      name='eliminar_venta'),
    path('stock/<int:pk>/',     views.producto_stock_json, name='producto_stock'),
]