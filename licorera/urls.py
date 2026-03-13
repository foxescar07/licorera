
from django.contrib import admin
from django.urls import path
from controlador import views
from licorera.views import home

urlpatterns = [
    path('', home, name='home'),
    path('proveedores/', views.proveedores, name='proveedores'),
]
