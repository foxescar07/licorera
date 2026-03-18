
from email.header import Header
from xml.etree.ElementInclude import include

from django.contrib import admin
from django.urls import path, include # Importante agregar 'include'
from licorera.views import home
from controlador import views

urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('home/', home, name='home'), 
    path('proveedores/', views.proveedores, name='proveedores'),
    path('producto/', include('producto.urls')), 
    path('prueba/', views.prueba, name='prueba'),
]