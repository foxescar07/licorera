
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('licorera/', include('licorera.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('reportes/', include('reportes.urls')),
    path('usuario/',include('usuario.urls')),
    path('producto/',include('producto.urls')),
    
]
