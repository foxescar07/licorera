from django.contrib import admin
from django.urls import path, include
from licorera.views import home
# Borra la línea de "xml.etree", no la necesitas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'), 
    path('proveedores/', views.proveedores, name='proveedores'),
    path('producto/', include('producto.urls')),  
    
    # CAMBIO CLAVE: Cambia 'usuario.urls' por 'reportes.urls'
    # porque ahí es donde tienes definida la ruta 'login'
    path('', include('reportes.urls')),  
]