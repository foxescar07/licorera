from django.contrib import admin
from django.urls import path, include
from licorera.views import home
from controlador import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),
    path('home/', home, name='home'),

    path('proveedores/', include('proveedores.urls')),
    path('producto/', include('producto.urls')),
    path('reportes/', include('reportes.urls')),

    path('prueba/', views.prueba, name='prueba'),
]