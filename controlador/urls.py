from django.urls import path
from . import views

urlpatterns = [
    path('proveedor/', views.proveedores, name='proveedores'),
]