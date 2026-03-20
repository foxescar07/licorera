from django.urls import path
from . import views  # Esto importa el views.py de la carpeta controlador

urlpatterns = [
    # Al dejarlo vacío '', se combinará con 'proveedores/' del archivo principal
    path('', views.inicio_proveedores, name='proveedores'),
]
