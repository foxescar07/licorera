from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio_proveedores, name='proveedores'),  
    path('editar-proveedor/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('eliminar-proveedor/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor')
]