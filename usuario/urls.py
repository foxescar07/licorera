
from django.urls import path
from . import views # Asegúrate de tener funciones en views.py

urlpatterns = [
    
    path('', views.usuario, name='usuario'),
]