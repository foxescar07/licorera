
from django.urls import path
from proveedores.views import inicio_proveedores

urlpatterns = [
    
    path ('', inicio_proveedores, name='proveedores'),
]