from django.urls import path
from . import views

app_name = "producto"

urlpatterns = [
    path("", views.producto_lista, name="producto_lista"),
    path("buscar/", views.buscar_producto, name="buscar_producto"),
    path("producto/<int:pk>/", views.producto_detalle, name="producto_detalle"),
    path("producto/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
    path("registro/", views.producto_registro, name="producto_registro"),
    

    # ✅ Endpoint centralizado para crear producto (usado desde inventario/gestion_productos)
    path("crear/", views.crear_producto, name="crear_producto"),

    path("agenda/", views.agenda_lista, name="agenda_lista"),
    path("agenda/<int:pk>/eliminar/", views.agenda_eliminar, name="agenda_eliminar"),
    path("categoria/crear/", views.categoria_crear, name="categoria_crear"),

    # ingreso/ eliminado — el ingreso de stock viene de proveedores/compra/
    path("salida/", views.producto_salida, name="producto_salida"),
    path("presentaciones/<int:pk>/guardar/", views.presentaciones_guardar, name="presentaciones_guardar"),
    path("presentaciones/<int:pk>/json/", views.presentaciones_json, name="presentaciones_json"),
    path("stock-status/", views.stock_status, name="stock_status"),
    
]