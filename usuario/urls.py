from django.urls import path
from . import views
 
urlpatterns = [
    path('usuario/registro/', views.registro_usuario, name='registro_usuario'),
    path('usuario/', views.lista_usuarios, name='lista_usuarios'),
]

