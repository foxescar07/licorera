from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('licorera.urls')),       # app principal
    path('', include('usuario.urls')),        # app usuario
    path('', include('proveedores.urls')),    # app proveedores
    path('', include('reportes.urls')),       # app reportes
    path('', include('producto.urls')),       # app producto
    path('', include('cajero.urls')),         # app cajero
    path('', include('cliente.urls')),        # app cliente
    path('', include('Rol.urls')),            # app Rol
]