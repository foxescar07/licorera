from email.header import Header
from xml.etree.ElementInclude import include # type: ignore

from django.contrib import admin
from django.urls import path, include
from licorera import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('prueba/', views.prueba, name='prueba'),
    path('producto/', include('producto.urls')),
    path('reportes/', include('reportes.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('categorias-json/', views.categorias_json, name='categorias_json'),

]