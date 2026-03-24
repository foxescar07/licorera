from django.urls import path
from . import views

urlpatterns = [
    # Ruta para la lista que ya tenías
    path('usuario/', views.lista_usuarios, name='usuario'), 
    
    # ESTAS SON LAS QUE HACEN QUE EL LOGIN FUNCIONE:
    path('login/', views.login_usuario, name='login'), 
    path('registro/', views.registro_usuario, name='registro_usuario'),
]