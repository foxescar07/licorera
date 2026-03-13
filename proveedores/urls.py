
from django.contrib import admin
from django.urls import path, include
from licorera.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('proveedores/', include('proveedores.urls')),
]
