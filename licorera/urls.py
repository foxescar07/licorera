from django.contrib import admin
from django.urls import path, include
from licorera import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # HOME REAL
    path('', views.home, name='home'),

    # APP USUARIO
    path('usuario/', include('usuario.urls')),

    path('producto/', include('producto.urls')),
    path('reportes/', include('reportes.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventario/', include('inventario.urls')),

    path('categorias-json/', views.categorias_json, name='categorias_json'),

]