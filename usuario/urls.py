from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_usuarios, name='usuario'),
    path('registro/', views.registro_usuario, name='registro_usuario'),
]