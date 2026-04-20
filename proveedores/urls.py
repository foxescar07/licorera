from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_proveedores, name='proveedores'),
    path('editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('compra/<int:proveedor_id>/', views.registrar_compra, name='registrar_compra'),

    # ── Gestión de Productos desde Proveedores ──
    path('gestion/', views.gestion_productos, name='gestion_productos'),
    path('gestion/salida/', views.gestion_salida, name='gestion_salida'),
    path('gestion/categoria/crear/', views.gestion_categoria_crear, name='gestion_categoria_crear'),
    path('gestion/categoria/eliminar/<int:pk>/', views.gestion_categoria_eliminar, name='gestion_categoria_eliminar'),
    path('gestion/producto/eliminar/<int:pk>/', views.gestion_producto_eliminar, name='gestion_producto_eliminar'),
]