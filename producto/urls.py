from django.urls import path
from . import views

app_name = 'producto'

urlpatterns = [
    path('', views.producto, name='producto_lista'),
    path('editar/<int:pk>/', views.editar_producto, name='producto_editar'),
    path('detalle/<int:pk>/', views.detalle_producto, name='producto_detalle'),
]