

from django.urls import path
from . import views # Asegúrate de tener funciones en views.py

urlpatterns = [
    
    path('', views.proveedores, name='proveedores'),
]

from django.contrib import admin
from django.urls import path
from licorera.views import home

urlpatterns = [
    path('', proveedores, name='proveedores'),
]
