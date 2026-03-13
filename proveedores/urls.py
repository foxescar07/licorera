
from django.contrib import admin
from django.urls import path
from licorera.views import home

urlpatterns = [
    path('', proveedores, name='proveedores'),
]
