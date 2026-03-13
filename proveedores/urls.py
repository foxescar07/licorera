

from django.urls import path
from . import views

urlpatterns = [
    path('', views.proveedores, name='proveedores'),
]