from django.contrib import admin
from django.urls import path, include
from licorera import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
  
    path('', views.home, name='usuario'), 
    
    path('usuario/', views.home, name='usuario_link'), 

    path('prueba/', views.prueba, name='prueba'),
    path('producto/', include('producto.urls')),
    path('reportes/', include('reportes.urls')),
    path('proveedores/', include('proveedores.urls')),
    path('dashboard/', views.dashboard, name='dashboard'),
]