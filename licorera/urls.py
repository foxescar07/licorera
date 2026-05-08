from django.contrib import admin
from django.urls import path, include
from licorera import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('producto/', include('producto.urls')),
    path('reportes/', include('reportes.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('inventario/', include('inventario.urls')),
    path('ventas/', include('ventas.urls')),
    path('usuario/', include('usuario.urls')),
    path('categorias-json/', views.categorias_json, name='categorias_json'),
    path('semana-json/', views.semana_json, name='semana_json'),
    path('meses-json/', views.meses_json, name='meses_json'),
]