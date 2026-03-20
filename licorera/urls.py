from email.header import Header
from xml.etree.ElementInclude import include # type: ignore

from django.contrib import admin
from django.urls import path, include
from licorera.views import home
from controlador import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('producto/', include('producto.urls')),
    path('reportes/', include('reportes.urls')),
    path('prueba/', views.prueba, name='prueba'),
    path('proveedores/', include('proveedores.urls')),
]