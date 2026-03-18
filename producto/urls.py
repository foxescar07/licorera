from django.urls import path
from . import views

app_name = "producto"

urlpatterns = [
    path("", views.producto_lista, name="producto_lista"),
    path("producto/<int:pk>/", views.producto_detalle, name="producto_detalle"),
    path("producto/<int:pk>/editar/", views.producto_editar, name="producto_editar"),
]