from django.urls import path
from . import views

urlpatterns = [
    path('', views.proveedores, name='proveedores'),
    path('inicio/', views.inicio_proveedores, name='inicio_proveedores'),
]