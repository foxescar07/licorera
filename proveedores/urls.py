from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.inicio_proveedores,        name='proveedores'),
    path('editar/<int:id>/',                    views.editar_proveedor,          name='editar_proveedor'),
    path('eliminar/<int:id>/',                  views.eliminar_proveedor,        name='eliminar_proveedor'),
    path('compra/<int:compra_id>/recibida/',    views.marcar_recibida,           name='marcar_recibida'),
    path('compra/',                             views.registrar_compra,          name='registrar_compra'),
    path('<int:id>/estado/',                    views.cambiar_estado_proveedor,  name='cambiar_estado_proveedor'),
]