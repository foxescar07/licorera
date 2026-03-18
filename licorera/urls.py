

from xml.etree.ElementInclude import include

from django.contrib import admin
from django.urls import path, include # Importante agregar 'include'
from licorera.views import home
from controlador import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('proveedores/', views.proveedores, name='proveedores'),
    path('producto/', include('producto.urls')),  
    path('reportes/', include('reportes.urls')),  

]